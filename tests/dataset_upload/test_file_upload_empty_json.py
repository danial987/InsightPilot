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


@patch("pages.dataset_upload.Dataset.try_parsing_json")
@patch("streamlit.warning")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_file_upload_empty_json(mock_file_uploader, mock_warning, mock_try_parsing_json, setup_manager):
    """
    Test handling of an empty JSON file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "empty_file.json"
    mock_uploaded_file.size = 1024  
    mock_uploaded_file.getvalue.return_value = b"" 

    mock_file_uploader.return_value = mock_uploaded_file

    mock_try_parsing_json.return_value = pd.DataFrame()

    manager.dataset_db.dataset_exists.return_value = False

    manager.dataset_upload_page()

    manager.dataset_db.dataset_exists.assert_called_once_with("empty_file.json", 1)
    manager.dataset_db.save_to_database.assert_not_called()  

    mock_warning.assert_called_once_with("The uploaded file is empty or does not contain any columns.")
