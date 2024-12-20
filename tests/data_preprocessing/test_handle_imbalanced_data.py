import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_preprocessing import HandleImbalancedData

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Feature1": [1, 2, 3, 4, 5],
        "Feature2": ["A", "B", "A", "C", "B"],
        "Target": [0, 1, 0, 1, 0]
    })

def test_handle_imbalanced_no_target_column(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.selectbox = MagicMock(side_effect=["NonExistentColumn", ""])
    mock_st.error = MagicMock()

    handle_imbalance_strategy = HandleImbalancedData()
    processed_df = handle_imbalance_strategy.apply(sample_dataframe)

    assert processed_df.equals(sample_dataframe)

    mock_st.error.assert_any_call("Please select a valid target column.")


def test_handle_imbalanced_with_smote(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.selectbox = MagicMock(side_effect=["Target", "Oversampling (SMOTE)"])
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()

    handle_imbalance_strategy = HandleImbalancedData()
    processed_df = handle_imbalance_strategy.apply(sample_dataframe)

    assert "Target" in processed_df.columns
    assert len(processed_df) > len(sample_dataframe)
    mock_st.success.assert_called_once_with("Oversampling (SMOTE) has been applied.")

def test_handle_imbalanced_with_undersampling(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.selectbox = MagicMock(side_effect=["Target", "Undersampling"])
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()

    handle_imbalance_strategy = HandleImbalancedData()
    processed_df = handle_imbalance_strategy.apply(sample_dataframe)

    assert "Target" in processed_df.columns
    assert len(processed_df) < len(sample_dataframe)
    mock_st.success.assert_called_once_with("Undersampling has been applied.")
