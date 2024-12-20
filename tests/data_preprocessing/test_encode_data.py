import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_preprocessing import EncodeData


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "CategoricalColumn1": ["A", "B", "C", "A"],
        "CategoricalColumn2": ["X", "Y", "X", "Z"],
        "NumericalColumn": [1, 2, 3, 4]
    })


def test_encode_data_no_categorical_columns(mocker):
    df = pd.DataFrame({
        "NumericalColumn": [1, 2, 3, 4]
    })
    mock_st = mocker.patch("pages.data_preprocessing.st")
    encode_data_strategy = EncodeData()
    processed_df = encode_data_strategy.apply(df)

    assert processed_df.equals(df)
    mock_st.warning.assert_called_once_with("This dataset has no categorical columns to encode.")
    mock_st.success.assert_not_called()

def test_encode_data_one_hot_encoding(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func() 
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)
    mock_st.selectbox = MagicMock(return_value="One-Hot Encoding")

    encode_data_strategy = EncodeData()
    processed_df = encode_data_strategy.apply(sample_dataframe)

    assert "CategoricalColumn1_A" in processed_df.columns
    assert "CategoricalColumn1_B" in processed_df.columns
    assert "CategoricalColumn2_X" in processed_df.columns
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['encoding_applied']


def test_encode_data_label_encoding(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func() 
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)
    mock_st.selectbox = MagicMock(return_value="Label Encoding")

    encode_data_strategy = EncodeData()
    processed_df = encode_data_strategy.apply(sample_dataframe)

    assert processed_df["CategoricalColumn1"].dtype == "int64"
    assert processed_df["CategoricalColumn2"].dtype == "int64"
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['encoding_applied']
