import pytest
from unittest.mock import patch, MagicMock
from pages.dataset_upload import DatasetUploadManager
from dataset import Dataset
import pandas as pd
import io
import json


@pytest.fixture
def setup_manager():
    """
    Fixture to set up the DatasetUploadManager instance and mock dependencies.
    """
    manager = DatasetUploadManager()

    manager.dataset_db = MagicMock(spec=Dataset)
    return manager
    

@patch("streamlit.success")
@patch("streamlit.spinner")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_format_validation_csv(mock_file_uploader, mock_spinner, mock_success, setup_manager):
    """
    Test handling of a valid CSV file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "valid_file.csv"
    mock_uploaded_file.size = 2048 
    csv_content = "col1,col2,col3\n1,2,3\n4,5,6" 
    mock_uploaded_file.getvalue.return_value = csv_content.encode("utf-8")

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    manager.dataset_db.save_to_database = MagicMock()

    with patch("pandas.read_csv", return_value=pd.read_csv(io.StringIO(csv_content))):
        manager.dataset_upload_page()

    manager.dataset_db.dataset_exists.assert_called_once_with("valid_file.csv", 1)
    manager.dataset_db.save_to_database.assert_called_once()
    mock_success.assert_called_once_with("Dataset uploaded successfully!")


@patch("streamlit.success")
@patch("streamlit.spinner")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_format_validation_xlsx(mock_file_uploader, mock_spinner, mock_success, setup_manager):
    """
    Test handling of a valid XLSX file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "valid_file.xlsx"
    mock_uploaded_file.size = 4096  
    mock_uploaded_file.getvalue.return_value = b"Mock XLSX Data"  

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    manager.dataset_db.save_to_database = MagicMock()

    def mock_read_excel(data, engine):
        return pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})

    with patch("pandas.read_excel", side_effect=mock_read_excel):
        manager.dataset_upload_page()

    manager.dataset_db.dataset_exists.assert_called_once_with("valid_file.xlsx", 1)
    manager.dataset_db.save_to_database.assert_called_once()
    mock_success.assert_called_once_with("Dataset uploaded successfully!")

    
@patch("streamlit.success")
@patch("streamlit.spinner")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_format_validation_json(mock_file_uploader, mock_spinner, mock_success, setup_manager):
    """
    Test handling of a valid JSON file upload.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "valid_file.json"
    mock_uploaded_file.size = 2048  
    json_content = """
    {"col1": 1, "col2": 2, "col3": 3}
    {"col1": 4, "col2": 5, "col3": 6}
    """ 
    mock_uploaded_file.getvalue.return_value = json_content.encode("utf-8")

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    manager.dataset_db.save_to_database = MagicMock()

    def mock_try_parsing_json(uploaded_file):
        data = uploaded_file.getvalue().decode("utf-8").strip().split("\n")
        json_data = [json.loads(line) for line in data if line.strip()]
        return pd.json_normalize(json_data)

    with patch("pages.dataset_upload.Dataset.try_parsing_json", side_effect=mock_try_parsing_json):
        manager.dataset_upload_page()

    manager.dataset_db.dataset_exists.assert_called_once_with("valid_file.json", 1)
    manager.dataset_db.save_to_database.assert_called_once()
    mock_success.assert_called_once_with("Dataset uploaded successfully!")
