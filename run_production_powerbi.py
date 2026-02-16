"""
Production Power BI data pipeline (memory-aware).

Scrapes products from 10 websites, writes a combined CSV incrementally,
then uploads to a Google Sheet worksheet for Power BI.
"""
import csv
import gc
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock

import psutil

from config import CSV_COLUMNS, DATA_DIR
from google_sheets_helper import push_data
from heima24_scraper import Heima24Scraper
from heizungsdiscount24_scraper import Heizungsdiscount24Scraper
from meinhausshop_scraper import MeinHausShopScraper
from pumpe24_scraper import Pumpe24Scraper
from pumpenheizung_scraper import PumpenheizungScraper
from sanundo_scraper import SanundoScraper
from selfio_scraper import SelfioScraper
from st_shop24_scraper import StShop24Scraper
from wasserpumpe_scraper import WasserpumpeScraper
from wolfonlineshop_scraper import WolfonlineshopScraper

gc.enable()

print_lock = Lock()
csv_lock = Lock()

POWER_BI_SHEET_ID = os.getenv(
    "POWER_BI_SHEET_ID",
    "1MrbHBVwR8wIP35syBl5vV2oJ_LqO_HuxqSlu3WZ2KRg",
)

SCRAPERS = [
    ("sanundo", SanundoScraper),
    ("heima24", Heima24Scraper),
    ("st_shop24", StShop24Scraper),
    ("selfio", SelfioScraper),
    ("heizungsdiscount24", Heizungsdiscount24Scraper),
    ("meinhausshop", MeinHausShopScraper),
    ("wolfonlineshop", WolfonlineshopScraper),
    ("pumpe24", Pumpe24Scraper),
    ("pumpenheizung", PumpenheizungScraper),
    ("wasserpumpe", WasserpumpeScraper),
]

DEFAULT_BATCH_SIZE = 1
DEFAULT_SCRAPER_WORKERS = 4
DEFAULT_MEMORY_LIMIT_MB = 1700
DEFAULT_SHEETS_BATCH_SIZE = 1500
DEFAULT_WORKSHEET_NAME = "raw_all_products"


def thread_safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


def get_memory_usage_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def log_memory(label=""):
    mem = get_memory_usage_mb()
    thread_safe_print(f"[MEMORY] {label}: {mem:.1f} MB")
    return mem


def get_int_env(name, default, minimum=1):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
        return max(parsed, minimum)
    except ValueError:
        return default


def get_target_scrapers():
    """
    Resolve the list of scrapers from SCRAPER_FILTER.
    Example: SCRAPER_FILTER="sanundo,heima24,selfio"
    """
    filter_value = (os.getenv("SCRAPER_FILTER") or "").strip()
    if not filter_value:
        return SCRAPERS

    allowed = {name: cls for name, cls in SCRAPERS}
    selected = []
    for raw_name in filter_value.split(","):
        name = raw_name.strip()
        if not name:
            continue
        if name not in allowed:
            raise ValueError(
                f"Unknown scraper '{name}' in SCRAPER_FILTER. "
                f"Allowed: {', '.join(sorted(allowed))}"
            )
        selected.append((name, allowed[name]))

    if not selected:
        raise ValueError("SCRAPER_FILTER was set but no valid scraper names were provided")

    return selected


def convert_price(price_str):
    """Convert German price format to float when possible."""
    if not price_str or not str(price_str).strip():
        return ""
    try:
        value = str(price_str).strip().strip('"')
        if "," in value:
            value = value.replace(".", "").replace(",", ".")
        return float(value)
    except (ValueError, AttributeError):
        return ""


def process_and_write_products(
    source_name,
    csv_file,
    combined_csv_path,
    columns_with_source,
    header_written_ref,
):
    """
    Stream rows from scraper CSV and append to combined CSV in chunks.
    """
    product_count = 0
    chunk_size = 500
    chunk = []

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for product in reader:
                product["Quelle"] = source_name
                if product.get("Preis_Netto"):
                    product["Preis_Netto"] = convert_price(product["Preis_Netto"])
                if product.get("Preis_Brutto"):
                    product["Preis_Brutto"] = convert_price(product["Preis_Brutto"])

                chunk.append(product)
                product_count += 1

                if len(chunk) >= chunk_size:
                    with csv_lock:
                        with open(combined_csv_path, "a", newline="", encoding="utf-8") as out:
                            writer = csv.DictWriter(out, fieldnames=columns_with_source)
                            if not header_written_ref[0]:
                                writer.writeheader()
                                header_written_ref[0] = True
                            writer.writerows(chunk)
                    chunk = []

                    if product_count % (chunk_size * 3) == 0:
                        gc.collect()

            if chunk:
                with csv_lock:
                    with open(combined_csv_path, "a", newline="", encoding="utf-8") as out:
                        writer = csv.DictWriter(out, fieldnames=columns_with_source)
                        if not header_written_ref[0]:
                            writer.writeheader()
                            header_written_ref[0] = True
                        writer.writerows(chunk)

    except Exception as e:
        thread_safe_print(f"[ERROR] failed processing {source_name}: {e}")
        import traceback

        thread_safe_print(traceback.format_exc())

    return product_count


def run_single_scraper(
    name,
    scraper_class,
    idx,
    total,
    combined_csv_path,
    columns_with_source,
    header_written_ref,
    scraper_workers,
):
    thread_safe_print(f"\n[{idx}/{total}] starting {name}")
    thread_safe_print("-" * 80)

    start_time = time.time()
    mem_before = get_memory_usage_mb()

    try:
        scraper = scraper_class()
        scraper.run(max_products=None, concurrent_workers=scraper_workers)
        elapsed = time.time() - start_time

        del scraper
        gc.collect()
        mem_after_scrape = get_memory_usage_mb()

        csv_file = DATA_DIR / f"{name}.csv"
        if not csv_file.exists():
            thread_safe_print(f"[ERROR] {name}: CSV output not found")
            return {"scraper": name, "status": "failed", "products": 0, "time": elapsed}

        processed_count = process_and_write_products(
            source_name=name,
            csv_file=csv_file,
            combined_csv_path=combined_csv_path,
            columns_with_source=columns_with_source,
            header_written_ref=header_written_ref,
        )
        mem_after_process = get_memory_usage_mb()

        thread_safe_print(
            f"[OK] {name}: {processed_count} products in {elapsed:.1f}s "
            f"(memory {mem_before:.1f} -> {mem_after_scrape:.1f} -> {mem_after_process:.1f} MB)"
        )
        return {
            "scraper": name,
            "status": "success",
            "products": processed_count,
            "time": elapsed,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        thread_safe_print(f"[ERROR] {name}: {e}")
        import traceback

        thread_safe_print(traceback.format_exc())
        return {
            "scraper": name,
            "status": "error",
            "products": 0,
            "time": elapsed,
            "error": str(e),
        }


def run_production_pipeline():
    target_scrapers = get_target_scrapers()

    print("=" * 80)
    print("PRODUCTION POWER BI DATA PIPELINE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Sheet ID: {POWER_BI_SHEET_ID}")
    print(f"Total scrapers: {len(target_scrapers)}")
    print(f"Scrapers: {[name for name, _ in target_scrapers]}")
    print("=" * 80)

    batch_size = min(
        get_int_env("PIPELINE_BATCH_SIZE", DEFAULT_BATCH_SIZE),
        len(target_scrapers),
    )
    scraper_workers = get_int_env("SCRAPER_WORKERS", DEFAULT_SCRAPER_WORKERS, minimum=1)
    memory_limit_mb = get_int_env(
        "PIPELINE_MEMORY_LIMIT_MB", DEFAULT_MEMORY_LIMIT_MB, minimum=256
    )
    sheets_batch_size = get_int_env(
        "SHEETS_BATCH_SIZE", DEFAULT_SHEETS_BATCH_SIZE, minimum=100
    )
    worksheet_name = (
        os.getenv("POWERBI_WORKSHEET_NAME", DEFAULT_WORKSHEET_NAME).strip()
        or DEFAULT_WORKSHEET_NAME
    )

    print(f"Batch size (parallel scrapers): {batch_size}")
    print(f"Per-scraper workers: {scraper_workers}")
    print(f"Memory GC threshold: {memory_limit_mb} MB")
    print(f"Google Sheets worksheet: {worksheet_name}")
    print(f"Google Sheets batch size: {sheets_batch_size}")
    print()

    log_memory("initial")

    combined_csv = DATA_DIR / "power_bi_production.csv"
    if combined_csv.exists():
        combined_csv.unlink()
        print("Removed previous combined CSV")

    columns_with_source = (
        CSV_COLUMNS + ["Quelle"] if "Quelle" not in CSV_COLUMNS else CSV_COLUMNS
    )
    header_written_ref = [False]

    total_start_time = time.time()
    total_products = 0
    results = []

    for batch_start in range(0, len(target_scrapers), batch_size):
        batch_end = min(batch_start + batch_size, len(target_scrapers))
        batch_scrapers = target_scrapers[batch_start:batch_end]
        batch_num = (batch_start // batch_size) + 1

        thread_safe_print("\n" + "=" * 80)
        thread_safe_print(
            f"Batch {batch_num}: {[name for name, _ in batch_scrapers]}"
        )
        thread_safe_print("=" * 80)
        log_memory(f"before batch {batch_num}")

        with ThreadPoolExecutor(max_workers=len(batch_scrapers)) as executor:
            future_to_name = {
                executor.submit(
                    run_single_scraper,
                    name,
                    scraper_class,
                    batch_start + idx + 1,
                    len(target_scrapers),
                    combined_csv,
                    columns_with_source,
                    header_written_ref,
                    scraper_workers,
                ): name
                for idx, (name, scraper_class) in enumerate(batch_scrapers)
            }

            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    result = future.result()
                    results.append(result)
                    total_products += int(result.get("products", 0) or 0)

                    current_mem = get_memory_usage_mb()
                    if current_mem > memory_limit_mb:
                        thread_safe_print(
                            f"[WARN] memory {current_mem:.1f} MB above threshold, running GC"
                        )
                        gc.collect()
                        time.sleep(1)

                    log_memory(f"after {name}")
                    gc.collect()
                except Exception as e:
                    thread_safe_print(f"[ERROR] unexpected error for {name}: {e}")
                    results.append(
                        {
                            "scraper": name,
                            "status": "error",
                            "products": 0,
                            "time": 0,
                            "error": str(e),
                        }
                    )

        gc.collect()
        time.sleep(2)
        log_memory(f"after batch {batch_num}")

    total_elapsed = time.time() - total_start_time

    if not combined_csv.exists() or total_products <= 0:
        print("\n[ERROR] no products scraped, pipeline failed")
        if not combined_csv.exists():
            print("Combined CSV file was not created")
        if total_products <= 0:
            print("Total product count is 0")
        sys.exit(1)

    with open(combined_csv, "r", encoding="utf-8") as f:
        actual_rows = max(sum(1 for _ in csv.reader(f)) - 1, 0)

    print("\n" + "=" * 80)
    print("PUSHING TO GOOGLE SHEETS")
    print("=" * 80)
    log_memory("before sheets upload")

    try:
        ok = push_data(
            sheet_id=POWER_BI_SHEET_ID,
            csv_file=combined_csv,
            worksheet_name=worksheet_name,
            clear_existing=True,
            batch_size=sheets_batch_size,
        )
        if not ok:
            raise RuntimeError("Google Sheets upload reported failure")
        print(f"[OK] pushed {actual_rows:,} products to Google Sheets")
        log_memory("after sheets upload")
    except Exception as e:
        print(f"[ERROR] failed to push to Google Sheets: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    print(f"Total products scraped: {total_products:,}")
    print(f"Total time: {total_elapsed / 60:.1f} minutes ({total_elapsed:.1f} seconds)")
    print("\nResults by scraper:")
    print("-" * 80)

    results.sort(key=lambda x: x["scraper"])
    for result in results:
        status = "OK" if result["status"] == "success" else "ERROR"
        print(
            f"{status:5s} {result['scraper']:20s} | "
            f"{result['products']:6,d} products | {result['time']:7.1f}s"
        )
        if "error" in result:
            print(f"      error: {result['error']}")

    print("\n" + "=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Worksheet: {worksheet_name}")
    print("=" * 80)
    log_memory("final")


if __name__ == "__main__":
    try:
        run_production_pipeline()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
