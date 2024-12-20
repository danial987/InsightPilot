import pytest
from unittest.mock import patch, MagicMock
from pages.search_dataset import DatasetSearch


@pytest.fixture
def setup_search():
    """Fixture to initialize DatasetSearch instance."""
    return DatasetSearch()

@patch("pages.search_dataset.requests.get")
def test_datagov_dataset_search_with_valid_query(mock_get, setup_search):
    """
    Test Data.gov dataset search with a valid query.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "results": [
                {
                    "id": "dataset1",
                    "title": "Valid Dataset",
                    "metadata_modified": "2024-11-19T00:00:00",
                    "resources": [
                        {"format": "CSV", "url": "https://example.com/dataset1.csv"},
                        {"format": "JSON", "url": "https://example.com/dataset1.json"}
                    ]
                },
                {
                    "id": "dataset2",
                    "title": "Another Valid Dataset",
                    "metadata_modified": "2024-11-18T00:00:00",
                    "resources": [
                        {"format": "XLSX", "url": "https://example.com/dataset2.xlsx"}
                    ]
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    datasets = setup_search.search_data_gov_datasets("valid_query")

    assert len(datasets) == 2

    assert datasets[0]['title'] == "Valid Dataset"
    assert datasets[0]['lastUpdated'] == "2024-11-19"
    assert len(datasets[0]['download_urls']) == 2
    assert datasets[0]['download_urls'][0] == ("CSV", "https://example.com/dataset1.csv")

    assert datasets[1]['title'] == "Another Valid Dataset"
    assert datasets[1]['lastUpdated'] == "2024-11-18"
    assert len(datasets[1]['download_urls']) == 1
    assert datasets[1]['download_urls'][0] == ("XLSX", "https://example.com/dataset2.xlsx")

@patch("pages.search_dataset.requests.get")
def test_datagov_dataset_search_with_invalid_query(mock_get, setup_search):
    """
    Test Data.gov dataset search with an invalid query.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"results": []}}
    mock_get.return_value = mock_response

    datasets = setup_search.search_data_gov_datasets("invalid_query")

    assert len(datasets) == 0