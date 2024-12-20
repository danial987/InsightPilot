import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from dataset import Dataset
from pages.dataset_upload import DatasetUploadManager
import pandas as pd
import streamlit as st  


@pytest.fixture
def setup_manager():
    """
    Fixture to set up the DatasetUploadManager instance and mock dependencies.
    """
    manager = DatasetUploadManager()
    manager.dataset_db = MagicMock(spec=Dataset)
    return manager


@patch("pages.dataset_upload.Dataset.try_parsing_csv")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_file_upload_csv_success(mock_file_uploader, mock_try_parsing_csv, setup_manager):
    """
    Test successful upload of a valid CSV file.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "test_file.csv"
    mock_uploaded_file.size = 1024  
    mock_uploaded_file.getvalue.return_value = b"name,age,city\nAlice,30,New York\nBob,25,Los Angeles"

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    mock_df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25], "city": ["New York", "Los Angeles"]})
    mock_try_parsing_csv.return_value = mock_df

    manager.dataset_upload_page()

    manager.dataset_db.dataset_exists.assert_called_once_with("test_file.csv", 1)
    mock_try_parsing_csv.assert_called_once()
    manager.dataset_db.save_to_database.assert_called_once_with(
        "test_file.csv",
        "csv",
        1024,
        mock_uploaded_file.getvalue(),
        1
    )

    assert "uploaded" in st.session_state
    assert st.session_state["uploaded"] is True
    assert "show_summary_button" in st.session_state
    assert st.session_state["show_summary_button"] is True


@patch("pages.dataset_upload.pd.read_excel")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_file_upload_xlsx_success(mock_file_uploader, mock_read_excel, setup_manager):
    """
    Test successful upload of a valid XLSX file.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "test_file.xlsx"
    mock_uploaded_file.size = 3072 
    file_content = b"dummy binary content for xlsx"
    mock_uploaded_file.getvalue.return_value = file_content

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    mock_df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25], "city": ["New York", "Los Angeles"]})
    mock_read_excel.return_value = mock_df

    with patch("io.BytesIO", return_value=BytesIO(file_content)) as mock_bytes_io:
        manager.dataset_upload_page()

        manager.dataset_db.dataset_exists.assert_called_once_with("test_file.xlsx", 1)
        mock_read_excel.assert_called_once_with(mock_bytes_io.return_value, engine="openpyxl")
        manager.dataset_db.save_to_database.assert_called_once_with(
            "test_file.xlsx",
            "xlsx",
            3072,
            file_content,
            1
        )

    assert "uploaded" in st.session_state
    assert st.session_state["uploaded"] is True
    assert "show_summary_button" in st.session_state
    assert st.session_state["show_summary_button"] is True


@patch("pages.dataset_upload.Dataset.try_parsing_json")
@patch("streamlit.file_uploader")
@patch.dict("streamlit.session_state", {"user_id": 1}, clear=True)
def test_file_upload_json_success(mock_file_uploader, mock_try_parsing_json, setup_manager):
    """
    Test successful upload of a valid JSON file.
    """
    manager = setup_manager

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "test_file.json"
    mock_uploaded_file.size = 2048  
    mock_uploaded_file.getvalue.return_value = b'{"name": "Alice", "age": 30, "city": "New York"}\n' \
                                               b'{"name": "Bob", "age": 25, "city": "Los Angeles"}'

    mock_file_uploader.return_value = mock_uploaded_file

    manager.dataset_db.dataset_exists.return_value = False

    mock_df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25], "city": ["New York", "Los Angeles"]})
    mock_try_parsing_json.return_value = mock_df

    manager.dataset_upload_page()

    manager.dataset_db.dataset_exists.assert_called_once_with("test_file.json", 1)
    mock_try_parsing_json.assert_called_once()
    manager.dataset_db.save_to_database.assert_called_once_with(
        "test_file.json",
        "json",
        2048,
        mock_uploaded_file.getvalue(),
        1
    )

    assert "uploaded" in st.session_state
    assert st.session_state["uploaded"] is True
    assert "show_summary_button" in st.session_state
    assert st.session_state["show_summary_button"] is True
