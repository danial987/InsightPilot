import pytest
from unittest.mock import patch, MagicMock
from pages.dataset_upload import DatasetUploadManager
from dataset import Dataset
import pandas as pd


@pytest.fixture
def setup_manager():
    """
    Fixture to set up the DatasetUploadManager instance and mock dependencies.
    """
    manager = DatasetUploadManager()

    manager.dataset_db = MagicMock(spec=Dataset)
    return manager


@patch("streamlit.error")
@patch("streamlit.spinner")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_invalid_csv_format(mock_file_uploader, mock_spinner, mock_error, setup_manager):
    """
    Test handling of an invalid CSV file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "invalid_file.csv"
    mock_uploaded_file.size = 2048  
    mock_uploaded_file.getvalue.return_value = b"Name, Age\nJohn, Doe\n"  

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    with patch("pages.dataset_upload.Dataset.try_parsing_csv", side_effect=pd.errors.ParserError("CSV Parsing Error")):
        manager.dataset_upload_page()

    mock_error.assert_called_once_with("Error parsing the file: CSV Parsing Error")


@patch("streamlit.error")
@patch("streamlit.spinner")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_invalid_json_format(mock_file_uploader, mock_spinner, mock_error, setup_manager):
    """
    Test handling of an invalid JSON file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "invalid_file.json"
    mock_uploaded_file.size = 2048  
    mock_uploaded_file.getvalue.return_value = b"{ invalid_json_content: True, }"  

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    with patch("pages.dataset_upload.Dataset.try_parsing_json", return_value=None):
        manager.dataset_upload_page()

    mock_error.assert_called_once_with("Failed to parse the JSON file. Please check the file format.")

    
@patch("streamlit.error")
@patch("streamlit.spinner")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_invalid_xlsx_format(mock_file_uploader, mock_spinner, mock_error, setup_manager):
    """
    Test handling of an invalid XLSX file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "invalid_file.xlsx"
    mock_uploaded_file.size = 2048 
    mock_uploaded_file.getvalue.return_value = b"Invalid XLSX content" 

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    with patch("pandas.read_excel", side_effect=ValueError("XLSX Parsing Error")):
        manager.dataset_upload_page()

    mock_error.assert_called_once_with("Error reading the file: XLSX Parsing Error")


@patch("streamlit.error")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_file_upload_invalid_format(mock_file_uploader, mock_error, setup_manager):
    """
    Test handling of a file with an unsupported format upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "unsupported_file.txt"
    mock_uploaded_file.size = 1024  
    mock_uploaded_file.getvalue.return_value = b"Some content" 
    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    manager.dataset_upload_page()

    mock_error.assert_called_once_with("Unsupported file type")
