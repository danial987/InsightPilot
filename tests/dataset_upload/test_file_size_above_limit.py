import pytest
from unittest.mock import patch, MagicMock
from pages.dataset_upload import DatasetUploadManager
from dataset import Dataset


@pytest.fixture
def setup_manager():
    """
    Fixture to set up the DatasetUploadManager instance and mock dependencies.
    """
    manager = DatasetUploadManager()
    manager.dataset_db = MagicMock(spec=Dataset)  
    return manager


@patch("streamlit.error")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_file_size_above_limit(mock_file_uploader, mock_error, setup_manager):
    """
    Test handling of file uploads exceeding the 200MB size limit.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "large_file.csv"
    mock_uploaded_file.size = 210 * 1024 * 1024  
    mock_uploaded_file.getvalue.return_value = b"Some content"

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_upload_page()

    try:
        mock_error.assert_called_once_with("The file exceeds the 200MB size limit.")
        print("Error correctly triggered for large file size.")
    except AssertionError as e:
        print("Error message was not triggered. Debugging dataset_upload_page method...")
        raise e
