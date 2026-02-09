"""
Google Sheets integration helper.
Handles authentication and data pushing to Google Sheets.
"""
import gspread
import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional
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
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API using service account."""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                str(self.credentials_file),
                scope
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
        clear_existing: bool = True
    ) -> bool:
        """
        Push CSV data to a Google Sheet.
        
        Args:
            sheet_id: Google Sheet ID (from URL)
            csv_file: Path to CSV file to upload
            worksheet_name: Name of worksheet to update (default: "Sheet1")
            clear_existing: Whether to clear existing data first
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(sheet_id)
            logger.info(f"Opened spreadsheet: {spreadsheet.title}")
            
            # Get or create worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=len(CSV_COLUMNS)
                )
                logger.info(f"Created new worksheet: {worksheet_name}")
            
            # Read CSV data
            data = self._read_csv(csv_file)
            
            if not data:
                logger.warning(f"No data found in {csv_file}")
                return False
            
            # Clear existing data if requested
            if clear_existing:
                worksheet.clear()
                logger.info("Cleared existing worksheet data")
            
            # Update worksheet with new data (specify range starting from A1)
            num_rows = len(data)
            num_cols = len(data[0]) if data else 0
            
            # Calculate the column letter for the range
            if num_cols <= 26:
                end_col = chr(64 + num_cols)
            else:
                # Handle columns beyond Z (AA, AB, etc.)
                end_col = chr(64 + (num_cols - 1) // 26) + chr(65 + (num_cols - 1) % 26)
            
            range_name = f'A1:{end_col}{num_rows}'
            
            logger.info(f"Updating range {range_name} with {num_rows} rows and {num_cols} columns")
            
            # Debug: print first few rows
            logger.info(f"First row (headers): {data[0][:5]}")
            if len(data) > 1:
                logger.info(f"Second row (data): {data[1][:5]}")
            
            # Use USER_ENTERED to let Google Sheets interpret data types (numbers, dates, etc.)
            # Note: gspread v5+ changed argument order to (values, range_name) or use named args
            result = worksheet.update(values=data, range_name=range_name, value_input_option='USER_ENTERED')
            logger.info(f"Update result: {result}")
            
            # Format price columns as numbers
            try:
                # Find price_net and price_gross column indices
                header_row = data[0]
                price_net_col = None
                price_gross_col = None
                
                for i, col_name in enumerate(header_row):
                    if col_name == 'price_net':
                        price_net_col = i
                    elif col_name == 'price_gross':
                        price_gross_col = i
                
                # Format the columns as numbers
                if price_net_col is not None:
                    col_letter = chr(65 + price_net_col) if price_net_col < 26 else chr(64 + price_net_col // 26) + chr(65 + price_net_col % 26)
                    range_to_format = f'{col_letter}2:{col_letter}{num_rows}'
                    worksheet.format(range_to_format, {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}})
                    logger.info(f"Formatted price_net column ({col_letter}) as number")
                
                if price_gross_col is not None:
                    col_letter = chr(65 + price_gross_col) if price_gross_col < 26 else chr(64 + price_gross_col // 26) + chr(65 + price_gross_col % 26)
                    range_to_format = f'{col_letter}2:{col_letter}{num_rows}'
                    worksheet.format(range_to_format, {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}})
                    logger.info(f"Formatted price_gross column ({col_letter}) as number")
                    
            except Exception as e:
                logger.warning(f"Could not format price columns: {e}")
            
            row_count = len(data) - 1  # Subtract header row
            logger.info(f"Successfully pushed {row_count} rows to Google Sheets")
            
            return True
            
        except gspread.exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}")
            print(f"✗ Google Sheets API error: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            logger.error(f"Failed to push data to Google Sheets: {e}")
            print(f"✗ Failed to push data to Google Sheets: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _read_csv(self, csv_file: Path) -> List[List]:
        """
        Read CSV file and return as list of lists.
        Converts price columns to proper numeric format for Google Sheets.
        
        Args:
            csv_file: Path to CSV file
        
        Returns:
            List of rows (each row is a list of values)
        """
        data = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if not rows:
                    return data
                
                # Get header row
                header = rows[0]
                data.append(header)
                
                # Find price column indices
                price_net_idx = None
                price_gross_idx = None
                
                try:
                    price_net_idx = header.index('price_net')
                except ValueError:
                    pass
                
                try:
                    price_gross_idx = header.index('price_gross')
                except ValueError:
                    pass
                
                # Process data rows
                for row in rows[1:]:
                    # Convert price columns to numeric format (dot as decimal separator)
                    if price_net_idx is not None and price_net_idx < len(row):
                        try:
                            price_str = str(row[price_net_idx]).strip().strip('"')
                            if price_str:
                                # Check if it's German format (has comma) or already numeric (has dot)
                                if ',' in price_str:
                                    # German format: remove thousand separators (.) and replace decimal comma with dot
                                    price_str = price_str.replace('.', '').replace(',', '.')
                                # Store as float (not string) so Google Sheets recognizes it as a number
                                row[price_net_idx] = float(price_str)
                        except (ValueError, AttributeError):
                            pass
                    
                    if price_gross_idx is not None and price_gross_idx < len(row):
                        try:
                            price_str = str(row[price_gross_idx]).strip().strip('"')
                            if price_str:
                                # Check if it's German format (has comma) or already numeric (has dot)
                                if ',' in price_str:
                                    # German format: remove thousand separators (.) and replace decimal comma with dot
                                    price_str = price_str.replace('.', '').replace(',', '.')
                                # Store as float (not string) so Google Sheets recognizes it as a number
                                row[price_gross_idx] = float(price_str)
                        except (ValueError, AttributeError):
                            pass
                    
                    data.append(row)
            
            logger.debug(f"Read {len(data)} rows from {csv_file}")
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file}")
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            import traceback
            traceback.print_exc()
        
        return data
    
    def get_sheet_data(
        self,
        sheet_id: str,
        worksheet_name: str = "Sheet1"
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
            
            # Get all records as list of dictionaries
            records = worksheet.get_all_records()
            
            logger.info(f"Retrieved {len(records)} records from Google Sheets")
            return records
            
        except Exception as e:
            logger.error(f"Failed to get data from Google Sheets: {e}")
            return []
    
    def create_new_sheet(
        self,
        title: str,
        share_with_email: Optional[str] = None
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
            
            # Add header row
            worksheet = spreadsheet.sheet1
            worksheet.update([CSV_COLUMNS], value_input_option='RAW')
            
            # Share with email if provided
            if share_with_email:
                spreadsheet.share(
                    share_with_email,
                    perm_type='user',
                    role='writer'
                )
                logger.info(f"Shared sheet with {share_with_email}")
            
            logger.info(f"Created new sheet: {title} (ID: {spreadsheet.id})")
            return spreadsheet.id
            
        except Exception as e:
            logger.error(f"Failed to create new sheet: {e}")
            return None


# Convenience function for backward compatibility with existing code
def push_data(sheet_id: str, csv_file: Path) -> bool:
    """
    Simple function to push CSV data to Google Sheets.
    Compatible with existing scraper code.
    
    Args:
        sheet_id: Google Sheet ID
        csv_file: Path to CSV file
    
    Returns:
        True if successful, False otherwise
    """
    helper = GoogleSheetsHelper()
    return helper.push_csv_to_sheet(sheet_id, csv_file)
