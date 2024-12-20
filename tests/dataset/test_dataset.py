import pytest
from unittest.mock import patch, MagicMock, ANY
from dataset import Dataset


@patch("database.Dataset.session")  
def test_delete_dataset(mock_session):
    dataset = Dataset()

    mock_session.execute.return_value = None
    mock_session.commit.return_value = None

    dataset_id = 1
    user_id = 1

    dataset.delete_dataset(dataset_id, user_id)

    mock_session.execute.assert_called_once_with(ANY)  
    mock_session.commit.assert_called_once() 


@patch("database.Dataset.session")  
def test_fetch_datasets(mock_session):
    dataset = Dataset()

    mock_session.execute.return_value.fetchall.return_value = [
        {"id": 1, "name": "dataset1.csv", "last_accessed": "2024-11-18"},
        {"id": 2, "name": "dataset2.csv", "last_accessed": "2024-11-17"}
    ]

    user_id = 1
    result = dataset.fetch_datasets(user_id)

    assert len(result) == 2 
    assert result[0]["name"] == "dataset1.csv" 
    assert result[1]["name"] == "dataset2.csv" 

    mock_session.execute.assert_called_once_with(ANY)


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
