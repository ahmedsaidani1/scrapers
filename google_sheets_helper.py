"""
Google Sheets integration helper.
Handles authentication and data pushing to Google Sheets.
"""
import csv
import json
import logging
import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import CREDENTIALS_FILE, CSV_COLUMNS

logger = logging.getLogger(__name__)


class GoogleSheetsHelper:
    """
    Helper class for Google Sheets operations.

    Usage:
        helper = GoogleSheetsHelper()
        helper.push_csv_to_sheet("your_sheet_id", "data/output.csv")
    """

    def __init__(self, credentials_file: Path = CREDENTIALS_FILE):
        """
        Initialize Google Sheets helper with credentials.

        Args:
            credentials_file: Path to credentials.json file
        """
        self.credentials_file = credentials_file
        self.client = None
        self._ensure_credentials_file()
        self._authenticate()

    def _ensure_credentials_file(self) -> None:
        """
        Ensure credentials file exists.

        On Render, credentials are typically stored in the environment variable
        GOOGLE_APPLICATION_CREDENTIALS_JSON. If the file is missing, materialize
        it to config.CREDENTIALS_FILE.
        """
        if self.credentials_file.exists():
            return

        raw_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not raw_json:
            return

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error(
                "GOOGLE_APPLICATION_CREDENTIALS_JSON is set but is not valid JSON: %s",
                e,
            )
            return

        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.credentials_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Created credentials file from GOOGLE_APPLICATION_CREDENTIALS_JSON")

    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API using service account."""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                str(self.credentials_file),
                scope,
            )

            self.client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Sheets API")

        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_file}")
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def push_csv_to_sheet(
        self,
        sheet_id: str,
        csv_file: Path,
        worksheet_name: str = "Sheet1",
        clear_existing: bool = True,
        batch_size: int = 2000,
    ) -> bool:
        """
        Push CSV data to a Google Sheet in chunks to keep memory bounded.

        Args:
            sheet_id: Google Sheet ID (from URL)
            csv_file: Path to CSV file to upload
            worksheet_name: Name of worksheet to update (default: "Sheet1")
            clear_existing: Whether to clear existing data first
            batch_size: Number of rows per Sheets update call

        Returns:
            True if successful, False otherwise
        """
        try:
            header_row, row_iter = self._iter_csv_rows(csv_file)
            if not header_row:
                logger.warning(f"No data found in {csv_file}")
                return False

            num_cols = len(header_row)
            spreadsheet = self.client.open_by_key(sheet_id)
            logger.info(f"Opened spreadsheet: {spreadsheet.title}")

            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=max(len(CSV_COLUMNS), num_cols),
                )
                logger.info(f"Created new worksheet: {worksheet_name}")

            # Ensure the worksheet has enough columns for this CSV.
            if worksheet.col_count < num_cols:
                old_cols = worksheet.col_count
                worksheet.add_cols(num_cols - old_cols)
                logger.info(
                    f"Expanded worksheet columns from {old_cols} to at least {num_cols}"
                )

            if clear_existing:
                worksheet.clear()
                logger.info("Cleared existing worksheet data")

            worksheet.update(values=[header_row], range_name="A1", value_input_option="RAW")

            end_col = self._column_to_letter(num_cols)
            safe_batch_size = max(1, int(batch_size))

            next_row = 2
            total_data_rows = 0
            batch: List[List] = []

            for row in row_iter:
                batch.append(row)
                if len(batch) >= safe_batch_size:
                    end_row = next_row + len(batch) - 1
                    range_name = f"A{next_row}:{end_col}{end_row}"
                    worksheet.update(
                        values=batch,
                        range_name=range_name,
                        value_input_option="USER_ENTERED",
                    )
                    total_data_rows += len(batch)
                    next_row = end_row + 1
                    batch = []

            if batch:
                end_row = next_row + len(batch) - 1
                range_name = f"A{next_row}:{end_col}{end_row}"
                worksheet.update(
                    values=batch,
                    range_name=range_name,
                    value_input_option="USER_ENTERED",
                )
                total_data_rows += len(batch)

            self._format_price_columns(
                worksheet=worksheet,
                header_row=header_row,
                last_data_row=total_data_rows + 1,
            )

            logger.info(f"Successfully pushed {total_data_rows} rows to Google Sheets")
            return True

        except gspread.exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}")
            print(f"Google Sheets API error: {e}")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            logger.error(f"Failed to push data to Google Sheets: {e}")
            print(f"Failed to push data to Google Sheets: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _column_to_letter(self, col_num: int) -> str:
        """Convert 1-based column number to A1 notation letters."""
        if col_num < 1:
            raise ValueError("Column number must be >= 1")

        letters: List[str] = []
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            letters.append(chr(65 + remainder))
        return "".join(reversed(letters))

    def _format_price_columns(self, worksheet, header_row: List[str], last_data_row: int) -> None:
        """Format known price columns as numeric."""
        if last_data_row < 2:
            return

        price_columns = {"price_net", "price_gross", "Preis_Netto", "Preis_Brutto"}
        for idx, column_name in enumerate(header_row, start=1):
            if column_name in price_columns:
                col_letter = self._column_to_letter(idx)
                range_to_format = f"{col_letter}2:{col_letter}{last_data_row}"
                worksheet.format(
                    range_to_format,
                    {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}},
                )
                logger.info(f"Formatted {column_name} column ({col_letter}) as number")

    def _iter_csv_rows(self, csv_file: Path) -> Tuple[List[str], Iterator[List]]:
        """
        Return header and a row iterator with on-the-fly numeric conversion.
        This avoids loading the full CSV into memory.
        """
        try:
            f = open(csv_file, "r", encoding="utf-8", newline="")
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file}")
            return [], iter(())

        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            f.close()
            return [], iter(())

        price_indices: List[int] = []
        for col_name in ("price_net", "price_gross", "Preis_Netto", "Preis_Brutto"):
            try:
                price_indices.append(header.index(col_name))
            except ValueError:
                continue

        def row_generator() -> Iterator[List]:
            try:
                for row in reader:
                    for idx in price_indices:
                        if idx >= len(row):
                            continue
                        try:
                            price_str = str(row[idx]).strip().strip('"')
                            if not price_str:
                                continue
                            if "," in price_str:
                                price_str = price_str.replace(".", "").replace(",", ".")
                            row[idx] = float(price_str)
                        except (ValueError, AttributeError):
                            # Keep original value on conversion failure
                            pass
                    yield row
            finally:
                f.close()

        return header, row_generator()

    def get_sheet_data(
        self,
        sheet_id: str,
        worksheet_name: str = "Sheet1",
    ) -> List[Dict[str, str]]:
        """
        Get data from Google Sheet as list of dictionaries.

        Args:
            sheet_id: Google Sheet ID
            worksheet_name: Name of worksheet to read

        Returns:
            List of dictionaries (one per row)
        """
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            records = worksheet.get_all_records()

            logger.info(f"Retrieved {len(records)} records from Google Sheets")
            return records

        except Exception as e:
            logger.error(f"Failed to get data from Google Sheets: {e}")
            return []

    def create_new_sheet(
        self,
        title: str,
        share_with_email: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a new Google Sheet.

        Args:
            title: Title for the new spreadsheet
            share_with_email: Email to share the sheet with (optional)

        Returns:
            Sheet ID if successful, None otherwise
        """
        try:
            spreadsheet = self.client.create(title)

            worksheet = spreadsheet.sheet1
            worksheet.update([CSV_COLUMNS], value_input_option="RAW")

            if share_with_email:
                spreadsheet.share(
                    share_with_email,
                    perm_type="user",
                    role="writer",
                )
                logger.info(f"Shared sheet with {share_with_email}")

            logger.info(f"Created new sheet: {title} (ID: {spreadsheet.id})")
            return spreadsheet.id

        except Exception as e:
            logger.error(f"Failed to create new sheet: {e}")
            return None


def push_data(
    sheet_id: str,
    csv_file: Path,
    worksheet_name: str = "Sheet1",
    clear_existing: bool = True,
    batch_size: int = 2000,
) -> bool:
    """
    Simple function to push CSV data to Google Sheets.
    Compatible with existing scraper code while adding optional controls.

    Args:
        sheet_id: Google Sheet ID
        csv_file: Path to CSV file
        worksheet_name: Target worksheet/tab name
        clear_existing: Whether to clear existing worksheet before upload
        batch_size: Number of rows per API update call

    Returns:
        True if successful, False otherwise
    """
    helper = GoogleSheetsHelper()
    return helper.push_csv_to_sheet(
        sheet_id=sheet_id,
        csv_file=csv_file,
        worksheet_name=worksheet_name,
        clear_existing=clear_existing,
        batch_size=batch_size,
    )
