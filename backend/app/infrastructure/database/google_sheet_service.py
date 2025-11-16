"""
Google Sheets Service - Database Layer for 11-Agent System
Provides CRUD operations for Google Sheets as a database
Optimized for Google Cloud Run deployment
"""

import gspread
from google.oauth2 import service_account
from google.auth import default as google_default_auth
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleSheetService:
    """
    Service for interacting with Google Sheets as a database.
    Uses Application Default Credentials (ADC) for Cloud Run,
    or service account JSON from environment variable for local testing.
    """

    def __init__(self, sheet_id: Optional[str] = None):
        """
        Initialize Google Sheets connection.

        Args:
            sheet_id: Google Sheet ID. If None, reads from GOOGLE_SHEET_ID env var.
        """
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        if not self.sheet_id:
            raise ValueError("GOOGLE_SHEET_ID environment variable not set")

        self.client = self._authenticate()
        self.spreadsheet = None

        try:
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            logger.info(f"Connected to Google Sheet: {self.spreadsheet.title}")
        except Exception as e:
            logger.error(f"Failed to open spreadsheet: {e}")
            raise

    def _authenticate(self) -> gspread.Client:
        """
        Authenticate with Google Sheets API.
        Priority 1: Application Default Credentials (for Cloud Run)
        Priority 2: Service Account JSON from GOOGLE_SERVICE_ACCOUNT_JSON env var

        Returns:
            Authenticated gspread client
        """
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # Priority 1: Try Application Default Credentials (ADC)
        try:
            credentials, project = google_default_auth(scopes=scopes)
            logger.info("Using Application Default Credentials (ADC)")
            return gspread.authorize(credentials)
        except Exception as e:
            logger.warning(f"ADC not available: {e}")

        # Priority 2: Try service account JSON from environment variable
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=scopes
                )
                logger.info("Using Service Account from GOOGLE_SERVICE_ACCOUNT_JSON")
                return gspread.authorize(credentials)
            except Exception as e:
                logger.error(f"Failed to load service account from env var: {e}")
                raise

        raise ValueError(
            "No valid authentication method found. "
            "Please set up Application Default Credentials or GOOGLE_SERVICE_ACCOUNT_JSON"
        )

    def _get_worksheet(self, sheet_name: str) -> gspread.Worksheet:
        """
        Get or create a worksheet by name.

        Args:
            sheet_name: Name of the worksheet

        Returns:
            Worksheet object
        """
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            logger.info(f"Worksheet '{sheet_name}' not found, creating...")
            return self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

    def _serialize_value(self, value: Any) -> str:
        """Convert Python values to sheet-compatible strings"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, dict)):
            return json.dumps(value)
        elif value is None:
            return ""
        else:
            return str(value)

    def read_sheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Read all records from a sheet.

        Args:
            sheet_name: Name of the worksheet

        Returns:
            List of dictionaries representing rows (header as keys)
        """
        try:
            worksheet = self._get_worksheet(sheet_name)
            records = worksheet.get_all_records()
            logger.info(f"Read {len(records)} records from '{sheet_name}'")
            return records
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet_name}': {e}")
            raise

    def append_to_sheet(self, sheet_name: str, data_dict: Dict[str, Any]) -> bool:
        """
        Append a row to the sheet. Creates header if sheet is empty.

        Args:
            sheet_name: Name of the worksheet
            data_dict: Dictionary of data to append

        Returns:
            True if successful
        """
        try:
            worksheet = self._get_worksheet(sheet_name)

            # Check if sheet is empty (no header)
            all_values = worksheet.get_all_values()
            if not all_values:
                # Create header row
                headers = list(data_dict.keys())
                worksheet.append_row(headers)
                logger.info(f"Created header row in '{sheet_name}': {headers}")

            # Get current headers
            headers = worksheet.row_values(1)

            # Create row values matching header order
            row_values = [self._serialize_value(data_dict.get(header, "")) for header in headers]

            # Append the row
            worksheet.append_row(row_values)
            logger.info(f"Appended row to '{sheet_name}'")
            return True

        except Exception as e:
            logger.error(f"Error appending to sheet '{sheet_name}': {e}")
            raise

    def update_cell(
        self,
        sheet_name: str,
        row_index: int,
        column_name_or_index: Any,
        value: Any
    ) -> bool:
        """
        Update a specific cell in the sheet.

        Args:
            sheet_name: Name of the worksheet
            row_index: Row number (1-based, including header)
            column_name_or_index: Column name (string) or column index (int, 1-based)
            value: Value to set

        Returns:
            True if successful
        """
        try:
            worksheet = self._get_worksheet(sheet_name)

            # Convert column name to index if needed
            if isinstance(column_name_or_index, str):
                headers = worksheet.row_values(1)
                try:
                    col_index = headers.index(column_name_or_index) + 1
                except ValueError:
                    raise ValueError(f"Column '{column_name_or_index}' not found in sheet")
            else:
                col_index = column_name_or_index

            # Update the cell
            worksheet.update_cell(row_index, col_index, self._serialize_value(value))
            logger.info(f"Updated cell ({row_index}, {col_index}) in '{sheet_name}'")
            return True

        except Exception as e:
            logger.error(f"Error updating cell in '{sheet_name}': {e}")
            raise

    def find_rows(
        self,
        sheet_name: str,
        search_column: str,
        search_value: Any
    ) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Find rows where a specific column matches a value.
        Returns both row index and row data.

        Args:
            sheet_name: Name of the worksheet
            search_column: Column name to search in
            search_value: Value to search for

        Returns:
            List of tuples: (row_index, row_data_dict)
            Row index is 1-based and includes the header row
        """
        try:
            worksheet = self._get_worksheet(sheet_name)
            all_values = worksheet.get_all_values()

            if not all_values:
                return []

            headers = all_values[0]

            # Find column index
            try:
                col_index = headers.index(search_column)
            except ValueError:
                raise ValueError(f"Column '{search_column}' not found in sheet")

            # Search for matching rows
            results = []
            for idx, row in enumerate(all_values[1:], start=2):  # Start at row 2 (after header)
                if idx <= len(all_values) and col_index < len(row):
                    if str(row[col_index]) == str(search_value):
                        row_dict = dict(zip(headers, row))
                        results.append((idx, row_dict))

            logger.info(f"Found {len(results)} matching rows in '{sheet_name}'")
            return results

        except Exception as e:
            logger.error(f"Error finding rows in '{sheet_name}': {e}")
            raise

    def batch_append(self, sheet_name: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        Batch append multiple rows to the sheet for better performance.

        Args:
            sheet_name: Name of the worksheet
            data_list: List of dictionaries to append

        Returns:
            True if successful
        """
        if not data_list:
            return True

        try:
            worksheet = self._get_worksheet(sheet_name)

            # Check if sheet is empty (no header)
            all_values = worksheet.get_all_values()
            if not all_values:
                # Create header row from first item
                headers = list(data_list[0].keys())
                worksheet.append_row(headers)
                logger.info(f"Created header row in '{sheet_name}': {headers}")

            # Get current headers
            headers = worksheet.row_values(1)

            # Create rows matching header order
            rows = []
            for data_dict in data_list:
                row_values = [self._serialize_value(data_dict.get(header, "")) for header in headers]
                rows.append(row_values)

            # Batch append
            worksheet.append_rows(rows)
            logger.info(f"Batch appended {len(rows)} rows to '{sheet_name}'")
            return True

        except Exception as e:
            logger.error(f"Error batch appending to '{sheet_name}': {e}")
            raise


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_google_sheet_service: Optional[GoogleSheetService] = None


def get_google_sheet_service() -> GoogleSheetService:
    """
    Get or create singleton instance of GoogleSheetService.

    Returns:
        GoogleSheetService instance
    """
    global _google_sheet_service
    if _google_sheet_service is None:
        _google_sheet_service = GoogleSheetService()
    return _google_sheet_service
