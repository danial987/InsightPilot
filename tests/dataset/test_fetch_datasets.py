import pytest
from unittest.mock import patch, MagicMock, ANY
from dataset import Dataset


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