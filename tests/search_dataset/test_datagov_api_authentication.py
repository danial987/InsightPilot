import pytest
from unittest.mock import patch, MagicMock
from pages.search_dataset import DatasetSearch


@patch("requests.get")
def test_datagov_api_authentication_success(mock_get):
    """
    Test successful API response from Data.gov.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "result": {"results": []}}
    mock_get.return_value = mock_response

    dataset_search = DatasetSearch()

    datasets = dataset_search.search_data_gov_datasets("sample_query")

    mock_get.assert_called_once_with(
        "https://catalog.data.gov/api/3/action/package_search",
        params={"q": "sample_query", "rows": 10}
    )
    assert datasets == []


@patch("requests.get")
def test_datagov_api_authentication_failure(mock_get):
    """
    Test failure in API response from Data.gov.
    """
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_get.return_value = mock_response

    dataset_search = DatasetSearch()

    datasets = dataset_search.search_data_gov_datasets("invalid_query")

    mock_get.assert_called_once_with(
        "https://catalog.data.gov/api/3/action/package_search",
        params={"q": "invalid_query", "rows": 10}
    )
    assert datasets == [] 
