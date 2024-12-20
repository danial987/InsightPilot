import pytest
from unittest.mock import MagicMock
import pandas as pd
from pages.data_preprocessing import DeleteFeatures


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Feature1": [1, 2, 3, 4, 5],
        "Feature2": [10, 20, 30, 40, 50],
        "Feature3": ["A", "B", "C", "D", "E"]
    })


def test_delete_features_no_columns(mocker):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.multiselect = MagicMock(return_value=[])
    mock_st.warning = MagicMock()

    delete_features_strategy = DeleteFeatures()
    empty_df = pd.DataFrame()
    processed_df = delete_features_strategy.apply(empty_df)

    pd.testing.assert_frame_equal(processed_df, empty_df) 
    mock_st.warning.assert_called_once_with("This dataset has no columns to delete.")


def test_delete_features_no_selection(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    
    def mock_dialog(title):
        def decorator(func):
            return func  
        return decorator
    mock_st.dialog = MagicMock(side_effect=mock_dialog)

    mock_st.multiselect = MagicMock(return_value=[])  
    mock_st.warning = MagicMock()

    delete_features_strategy = DeleteFeatures()
    processed_df = delete_features_strategy.apply(sample_dataframe)

    pd.testing.assert_frame_equal(processed_df, sample_dataframe)

    mock_st.warning.assert_called_once_with("No columns selected for deletion.")


def test_delete_features_successful(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.multiselect = MagicMock(return_value=["Feature2", "Feature3"])
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()

    delete_features_strategy = DeleteFeatures()
    processed_df = delete_features_strategy.apply(sample_dataframe)

    expected_df = sample_dataframe.drop(columns=["Feature2", "Feature3"])
    pd.testing.assert_frame_equal(processed_df, expected_df) 
    mock_st.success.assert_called_once_with("Features ['Feature2', 'Feature3'] have been deleted.")


def test_delete_features_partial_selection(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.multiselect = MagicMock(return_value=["Feature1"])
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()

    delete_features_strategy = DeleteFeatures()
    processed_df = delete_features_strategy.apply(sample_dataframe)

    expected_df = sample_dataframe.drop(columns=["Feature1"])
    pd.testing.assert_frame_equal(processed_df, expected_df)  
    mock_st.success.assert_called_once_with("Features ['Feature1'] have been deleted.")
