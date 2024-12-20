import pytest
from unittest.mock import patch, MagicMock
from pages.search_dataset import DatasetSearch

@pytest.fixture
def setup_search():
    """Fixture to initialize DatasetSearch instance."""
    return DatasetSearch()

@patch("pages.search_dataset.KaggleApi.dataset_list")
def test_kaggle_dataset_search_with_valid_query(mock_dataset_list, setup_search):
    """
    Test Kaggle dataset search with a valid query.
    """
    mock_dataset_list.return_value = [
        MagicMock(ref="dataset1", title="Valid Dataset", totalBytes=4 * 1024 * 1024, lastUpdated="2024-11-19"),
        MagicMock(ref="dataset2", title="Another Valid Dataset", totalBytes=8 * 1024 * 1024, lastUpdated="2024-11-18"),
    ]

    datasets = setup_search.search_kaggle_datasets("valid_query")

    # Assertions
    assert len(datasets) == 2
    assert datasets[0]['title'] == "Valid Dataset"
    assert datasets[0]['size'] == 4.0 
    assert datasets[0]['lastUpdated'] == "2024-11-19"

    assert datasets[1]['title'] == "Another Valid Dataset"
    assert datasets[1]['size'] == 8.0 
    assert datasets[1]['lastUpdated'] == "2024-11-18"

@patch("pages.search_dataset.KaggleApi.dataset_list")
def test_kaggle_dataset_search_with_invalid_query(mock_dataset_list, setup_search):
    """
    Test Kaggle dataset search with an invalid query.
    """
    mock_dataset_list.return_value = []

    datasets = setup_search.search_kaggle_datasets("invalid_query")

    assert len(datasets) == 0
