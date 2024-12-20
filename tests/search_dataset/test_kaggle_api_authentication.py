import pytest
from unittest.mock import patch, MagicMock
from kaggle.api.kaggle_api_extended import KaggleApi
from pages.search_dataset import DatasetSearch


@patch("kaggle.api.kaggle_api_extended.KaggleApi.authenticate")
def test_kaggle_api_authentication_success(mock_authenticate):
    """
    Test successful authentication with the Kaggle API.
    """
    mock_authenticate.return_value = None

    dataset_search = DatasetSearch()

    mock_authenticate.assert_called_once()
    assert isinstance(dataset_search.kaggle_api, KaggleApi)


@patch("kaggle.api.kaggle_api_extended.KaggleApi.authenticate")
def test_kaggle_api_authentication_failure(mock_authenticate):
    """
    Test failure during authentication with the Kaggle API.
    """
    mock_authenticate.side_effect = Exception("Invalid API credentials")

    with pytest.raises(Exception, match="Invalid API credentials"):
        DatasetSearch()

    mock_authenticate.assert_called_once()
