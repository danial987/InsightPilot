import pytest
from unittest.mock import patch, MagicMock, ANY
from dataset import Dataset


@patch("database.Dataset.session")  
def test_save_to_database(mock_session):
    dataset = Dataset()

    mock_session.execute.return_value = None
    mock_session.commit.return_value = None

    file_name = "test_file.csv"
    file_format = "csv"
    file_size = 1024
    data = b"testdata"
    user_id = 1

    dataset.save_to_database(file_name, file_format, file_size, data, user_id)

    mock_session.execute.assert_called_once_with(ANY) 
    mock_session.commit.assert_called_once()
