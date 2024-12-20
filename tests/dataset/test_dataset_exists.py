import pytest
from unittest.mock import patch, MagicMock, ANY
from dataset import Dataset


@patch("database.Dataset.session")  
def test_dataset_exists(mock_session):
    dataset = Dataset()

    mock_session.execute.return_value.fetchone.return_value = {"name": "existing_dataset.csv"}

    file_name = "existing_dataset.csv"
    user_id = 1

    result = dataset.dataset_exists(file_name, user_id)

    assert result is True 
    mock_session.execute.assert_called_once_with(ANY)  


@patch("database.Dataset.session")  
def test_dataset_not_exists(mock_session):
    dataset = Dataset()

    mock_session.execute.return_value.fetchone.return_value = None

    file_name = "nonexistent_dataset.csv"
    user_id = 1

    result = dataset.dataset_exists(file_name, user_id)

    assert result is False 
    mock_session.execute.assert_called_once_with(ANY)
