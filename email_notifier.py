"""
Email Notification System for Scraper Changes
Detects new and updated products and sends email summaries
"""
import smtplib
import csv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import json


class EmailNotifier:
    """Handles email notifications for scraper changes"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, 
                 sender_password: str, recipient_emails: List[str]):
        """
        Initialize email notifier
        
        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (e.g., 587 for TLS)
            sender_email: Email address to send from
            sender_password: Email password or app password
            recipient_emails: List of email addresses to send to
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails
        
        # Directory to store previous data snapshots
        self.snapshot_dir = Path(__file__).parent / "data" / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True, parents=True)
    
    def get_snapshot_path(self, scraper_name: str) -> Path:
        """Get path to snapshot file for a scraper"""
        return self.snapshot_dir / f"{scraper_name}_snapshot.json"
    
    def load_previous_data(self, scraper_name: str) -> Dict[str, dict]:
        """Load previous scraping data from snapshot"""
        snapshot_path = self.get_snapshot_path(scraper_name)
        
        if not snapshot_path.exists():
            return {}
        
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading snapshot for {scraper_name}: {e}")
            return {}
    
    def save_current_data(self, scraper_name: str, current_data: Dict[str, dict]):
        """Save current scraping data as snapshot"""
        snapshot_path = self.get_snapshot_path(scraper_name)
        
        try:
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving snapshot for {scraper_name}: {e}")
    
    def load_csv_data(self, csv_path: str) -> Dict[str, dict]:
        """Load CSV data into dictionary keyed by product URL"""
        data = {}
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get('product_url', '')
                    if url:
                        data[url] = row
        except Exception as e:
            print(f"Error loading CSV {csv_path}: {e}")
        
        return data
    
    def detect_changes(self, scraper_name: str, csv_path: str) -> Tuple[List[dict], List[dict], List[dict]]:
        """
        Detect new, updated, and removed products
        
        Returns:
            Tuple of (new_products, updated_products, removed_products)
        """
        previous_data = self.load_previous_data(scraper_name)
        current_data = self.load_csv_data(csv_path)
        
        new_products = []
        updated_products = []
        removed_products = []
        
        # Find new and updated products
        for url, current_product in current_data.items():
            if url not in previous_data:
                # New product
                new_products.append(current_product)
            else:
                # Check if product was updated
                previous_product = previous_data[url]
                
                # Compare key fields
                if self._is_product_updated(previous_product, current_product):
                    updated_products.append({
                        'current': current_product,
                        'previous': previous_product
                    })
        
        # Find removed products
        for url, previous_product in previous_data.items():
            if url not in current_data:
                removed_products.append(previous_product)
        
        # Save current data as new snapshot
        self.save_current_data(scraper_name, current_data)
        
        return new_products, updated_products, removed_products
    
    def _is_product_updated(self, previous: dict, current: dict) -> bool:
        """Check if product has been updated"""
        # Compare important fields
        fields_to_compare = ['name', 'price_gross', 'price_net', 'manufacturer', 'category']
        
        for field in fields_to_compare:
            if previous.get(field) != current.get(field):
                return True
        
        return False
    
    def format_html_email(self, scraper_name: str, new_products: List[dict], 
                         updated_products: List[dict], removed_products: List[dict]) -> str:
        """Format changes as HTML email"""
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th {{ background-color: #3498db; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .new {{ color: #27ae60; font-weight: bold; }}
                .updated {{ color: #f39c12; font-weight: bold; }}
                .removed {{ color: #e74c3c; font-weight: bold; }}
                .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .price-change {{ font-weight: bold; }}
                .price-up {{ color: #e74c3c; }}
                .price-down {{ color: #27ae60; }}
            </style>
        </head>
        <body>
            <h1>📊 Scraper Update Report: {scraper_name.upper()}</h1>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h3>Summary</h3>
                <ul>
                    <li class="new">New Products: {len(new_products)}</li>
                    <li class="updated">Updated Products: {len(updated_products)}</li>
                    <li class="removed">Removed Products: {len(removed_products)}</li>
                </ul>
            </div>
        """
        
        # New Products Section
        if new_products:
            html += """
            <h2 class="new">🆕 New Products</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Manufacturer</th>
                    <th>Category</th>
                    <th>Price (Gross)</th>
                    <th>Link</th>
                </tr>
            """
            
            for product in new_products[:50]:  # Limit to 50 to avoid huge emails
                name = product.get('name', 'N/A')
                manufacturer = product.get('manufacturer', 'N/A')
                category = product.get('category', 'N/A')
                price = product.get('price_gross', 'N/A')
                url = product.get('product_url', '#')
                
                html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{manufacturer}</td>
                    <td>{category}</td>
                    <td>€{price}</td>
                    <td><a href="{url}">View</a></td>
                </tr>
                """
            
            if len(new_products) > 50:
                html += f"<tr><td colspan='5'><em>... and {len(new_products) - 50} more</em></td></tr>"
            
            html += "</table>"
        
        # Updated Products Section
        if updated_products:
            html += """
            <h2 class="updated">🔄 Updated Products</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Field Changed</th>
                    <th>Old Value</th>
                    <th>New Value</th>
                    <th>Link</th>
                </tr>
            """
            
            for update in updated_products[:50]:
                current = update['current']
                previous = update['previous']
                name = current.get('name', 'N/A')
                url = current.get('product_url', '#')
                
                # Find what changed
                changes = []
                for field in ['price_gross', 'price_net', 'name', 'manufacturer', 'category']:
                    old_val = previous.get(field, '')
                    new_val = current.get(field, '')
                    if old_val != new_val:
                        changes.append((field, old_val, new_val))
                
                for field, old_val, new_val in changes:
                    # Determine if price went up or down
                    price_class = ""
                    if field in ['price_gross', 'price_net']:
                        try:
                            old_price = float(old_val.replace(',', '.'))
                            new_price = float(new_val.replace(',', '.'))
                            price_class = "price-up" if new_price > old_price else "price-down"
                        except:
                            pass
                    
                    html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{field}</td>
                        <td>{old_val}</td>
                        <td class="{price_class}">{new_val}</td>
                        <td><a href="{url}">View</a></td>
                    </tr>
                    """
            
            if len(updated_products) > 50:
                html += f"<tr><td colspan='5'><em>... and {len(updated_products) - 50} more</em></td></tr>"
            
            html += "</table>"
        
        # Removed Products Section
        if removed_products:
            html += """
            <h2 class="removed">❌ Removed Products</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Manufacturer</th>
                    <th>Last Price</th>
                </tr>
            """
            
            for product in removed_products[:50]:
                name = product.get('name', 'N/A')
                manufacturer = product.get('manufacturer', 'N/A')
                price = product.get('price_gross', 'N/A')
                
                html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{manufacturer}</td>
                    <td>€{price}</td>
                </tr>
                """
            
            if len(removed_products) > 50:
                html += f"<tr><td colspan='3'><em>... and {len(removed_products) - 50} more</em></td></tr>"
            
            html += "</table>"
        
        # No changes
        if not new_products and not updated_products and not removed_products:
            html += "<p><em>No changes detected since last scrape.</em></p>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, subject: str, html_content: str):
        """Send email notification"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✓ Email sent successfully to {', '.join(self.recipient_emails)}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def check_and_notify(self, scraper_name: str, csv_path: str):
        """Check for changes and send notification if any found"""
        print(f"\nChecking for changes in {scraper_name}...")
        
        # Detect changes
        new_products, updated_products, removed_products = self.detect_changes(scraper_name, csv_path)
        
        total_changes = len(new_products) + len(updated_products) + len(removed_products)
        
        print(f"  New: {len(new_products)}")
        print(f"  Updated: {len(updated_products)}")
        print(f"  Removed: {len(removed_products)}")
        
        # Send email if there are changes
        if total_changes > 0:
            subject = f"🔔 {scraper_name.upper()} - {total_changes} Changes Detected"
            html_content = self.format_html_email(scraper_name, new_products, updated_products, removed_products)
            self.send_email(subject, html_content)
        else:
            print("  No changes detected - no email sent")


def main():
    """Example usage"""
    from config import DATA_DIR
    
    # Email configuration
    notifier = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="your-email@gmail.com",  # Change this
        sender_password="your-app-password",   # Change this (use app password for Gmail)
        recipient_emails=["recipient@example.com"]  # Change this
    )
    
    # Check all scrapers
    scrapers = [
        "meinhausshop", "heima24", "sanundo", "heizungsdiscount24",
        "wolfonlineshop", "st_shop24", "selfio", "pumpe24", "wasserpumpe"
    ]
    
    for scraper in scrapers:
        csv_path = DATA_DIR / f"{scraper}.csv"
        if csv_path.exists():
            notifier.check_and_notify(scraper, str(csv_path))


if __name__ == "__main__":
    main()
