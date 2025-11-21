"""
Google Sheets Database Service
Singleton service for persisting data to Google Sheets
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, List, Dict, Any
from app.utils.logger import setup_logger

logger = setup_logger("GoogleSheetService")

# Sheet names for each agent
SHEET_A1_PROJECTS = "A1_Projects_DB"
SHEET_A1_TREND_DATABASE = "A1_Trend_Database"  # Live viral music trends
SHEET_A2_QC_FEEDBACK = "A2_QC_Feedback_DB"
SHEET_A3_AUDIO_ANALYSIS = "A3_AudioAnalysis_DB"
SHEET_A4_SCENES = "A4_Scenes_DB"
SHEET_A5_STYLES = "A5_Styles_DB"
SHEET_A6_VEO_PROMPTS = "A6_VeoPrompts_DB"
SHEET_A7_RUNWAY_PROMPTS = "A7_RunwayPrompts_DB"
SHEET_A8_REFINEMENTS = "A8_Refinements_DB"

# Suno Prompt Generation Sheets
SHEET_SUNO_PROMPTS = "Suno_Prompts_DB"
SHEET_APPROVED_BEST_PRACTICES = "ApprovedBestPractices"  # Few-Shot Learning Knowledge Base

# Video Production Reference Sheets
SHEET_VIDEO_PROMPT_CHEATSHEET = "Video_Prompt_Cheatsheet"  # Camera & Lighting Keywords
SHEET_A5_STYLE_DATABASE = "A5_Style_Database"  # Global Style Presets & Learned Styles
SHEET_A6_VIDEO_EXAMPLES = "A6_Video_Examples"  # Few-Shot Examples for Video Prompt Generation
SHEET_A9_CAPCUT_EFFECTS = "A9_CapCut_Effects"  # CapCut Effects Database for Edit Instructions


class GoogleSheetService:
    """Singleton service for Google Sheets operations"""

    _instance: Optional['GoogleSheetService'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        """Initialize Google Sheets connection using Application Default Credentials (ADC)"""
        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None

        try:
            sheet_id = os.getenv("GOOGLE_SHEET_ID")

            if not sheet_id:
                logger.warning("GOOGLE_SHEET_ID not configured. Using in-memory storage.")
                return

            # Set up credentials - Try multiple authentication methods
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            credentials = None

            # Method 1: Try Application Default Credentials (ADC) first
            # This works automatically after 'gcloud auth application-default login'
            try:
                from google.auth import default
                credentials, project = default(scopes=scopes)
                logger.info("Using Application Default Credentials (ADC)")
            except Exception as adc_error:
                logger.warning(f"ADC not available: {adc_error}")

                # Method 2: Fallback to service account file if GOOGLE_APPLICATION_CREDENTIALS is set
                creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if creds_path:
                    try:
                        credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
                        logger.info("Using Service Account credentials from file")
                    except Exception as file_error:
                        logger.error(f"Service Account file auth failed: {file_error}")
                        return

            if not credentials:
                logger.warning("No valid credentials found. Using in-memory storage.")
                return

            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(sheet_id)

            # Ensure all worksheets exist
            self._ensure_worksheets()

            logger.info("Google Sheets service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            self.client = None
            self.spreadsheet = None

    def _ensure_worksheets(self):
        """Ensure all required worksheets exist"""
        if not self.spreadsheet:
            return

        required_sheets = [
            SHEET_A1_PROJECTS,
            SHEET_A1_TREND_DATABASE,
            SHEET_A2_QC_FEEDBACK,
            SHEET_A3_AUDIO_ANALYSIS,
            SHEET_A4_SCENES,
            SHEET_A5_STYLES,
            SHEET_A5_STYLE_DATABASE,
            SHEET_A6_VEO_PROMPTS,
            SHEET_A6_VIDEO_EXAMPLES,
            SHEET_A7_RUNWAY_PROMPTS,
            SHEET_A8_REFINEMENTS,
            SHEET_A9_CAPCUT_EFFECTS,
            SHEET_SUNO_PROMPTS,
            SHEET_APPROVED_BEST_PRACTICES,
            SHEET_VIDEO_PROMPT_CHEATSHEET
        ]

        existing_sheets = [ws.title for ws in self.spreadsheet.worksheets()]

        for sheet_name in required_sheets:
            if sheet_name not in existing_sheets:
                try:
                    self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                    logger.info(f"Created worksheet: {sheet_name}")
                except Exception as e:
                    logger.error(f"Failed to create worksheet {sheet_name}: {e}")

    def _get_worksheet(self, sheet_name: str) -> Optional[gspread.Worksheet]:
        """Get a worksheet by name"""
        if not self.spreadsheet:
            return None

        try:
            return self.spreadsheet.worksheet(sheet_name)
        except Exception as e:
            logger.error(f"Failed to get worksheet {sheet_name}: {e}")
            return None

    async def append_row(self, sheet_name: str, data: List[Any]) -> bool:
        """
        Append a row to a worksheet

        Args:
            sheet_name: Name of the worksheet
            data: List of values to append

        Returns:
            True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.debug(f"Sheets not configured. Would append to {sheet_name}: {data}")
            return True  # Return success in mock mode

        try:
            worksheet = self._get_worksheet(sheet_name)
            if worksheet:
                worksheet.append_row(data)
                logger.debug(f"Appended row to {sheet_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to append row to {sheet_name}: {e}")
            return False

    async def get_all_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Get all records from a worksheet

        Args:
            sheet_name: Name of the worksheet

        Returns:
            List of records as dictionaries
        """
        if not self.spreadsheet:
            logger.debug(f"Sheets not configured. Returning empty records for {sheet_name}")
            return []

        try:
            worksheet = self._get_worksheet(sheet_name)
            if worksheet:
                records = worksheet.get_all_records()
                return records
            return []
        except Exception as e:
            logger.error(f"Failed to get records from {sheet_name}: {e}")
            return []

    async def find_record(self, sheet_name: str, key_column: str, key_value: str) -> Optional[Dict[str, Any]]:
        """
        Find a record by key

        Args:
            sheet_name: Name of the worksheet
            key_column: Column name to search
            key_value: Value to search for

        Returns:
            Found record or None
        """
        records = await self.get_all_records(sheet_name)
        for record in records:
            if record.get(key_column) == key_value:
                return record
        return None

    async def update_record(self, sheet_name: str, key_column: str, key_value: str, updates: Dict[str, Any]) -> bool:
        """
        Update a record

        Args:
            sheet_name: Name of the worksheet
            key_column: Column name to search
            key_value: Value to search for
            updates: Dictionary of updates

        Returns:
            True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.debug(f"Sheets not configured. Would update {sheet_name}")
            return True

        try:
            worksheet = self._get_worksheet(sheet_name)
            if not worksheet:
                return False

            # Find the row
            cell = worksheet.find(key_value)
            if not cell:
                return False

            row_number = cell.row
            headers = worksheet.row_values(1)

            # Update each column
            for col_name, value in updates.items():
                if col_name in headers:
                    col_index = headers.index(col_name) + 1
                    worksheet.update_cell(row_number, col_index, value)

            return True
        except Exception as e:
            logger.error(f"Failed to update record in {sheet_name}: {e}")
            return False

    async def clear_and_replace(self, sheet_name: str, headers: List[str], data_rows: List[List[Any]]) -> bool:
        """
        Clear a worksheet and replace with new data

        Args:
            sheet_name: Name of the worksheet
            headers: Column headers
            data_rows: List of data rows

        Returns:
            True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.debug(f"Sheets not configured. Would clear and replace {sheet_name}")
            return True  # Return success in mock mode

        try:
            worksheet = self._get_worksheet(sheet_name)
            if not worksheet:
                return False

            # Clear all existing data
            worksheet.clear()
            logger.info(f"Cleared worksheet: {sheet_name}")

            # Add headers
            worksheet.append_row(headers)

            # Add all data rows
            for row in data_rows:
                worksheet.append_row(row)

            logger.info(f"Replaced {sheet_name} with {len(data_rows)} rows")
            return True

        except Exception as e:
            logger.error(f"Failed to clear and replace {sheet_name}: {e}")
            return False


# Singleton instance
google_sheet_service = GoogleSheetService()
