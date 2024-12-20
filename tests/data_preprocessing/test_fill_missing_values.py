import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_preprocessing import FillMissingValues


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "NumericalColumn": [1.0, None, 3.0, None],
        "CategoricalColumn": ["A", None, "C", None]
    })


def test_fill_missing_values_no_missing(mocker):
    df = pd.DataFrame({
        "NumericalColumn": [1.0, 2.0, 3.0],
        "CategoricalColumn": ["A", "B", "C"]
    })
    mock_st = mocker.patch("pages.data_preprocessing.st")
    fill_missing_strategy = FillMissingValues()
    processed_df = fill_missing_strategy.apply(df)

    assert processed_df.equals(df)
    mock_st.warning.assert_called_once_with("This dataset has no missing values.")
    mock_st.success.assert_not_called()


def test_fill_missing_values_with_numerical(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)

    numerical_selectbox = MagicMock(side_effect=["Mean", "Mean"])
    mock_st.selectbox = numerical_selectbox

    mock_st.number_input = MagicMock(return_value=0)

    fill_missing_strategy = FillMissingValues()
    processed_df = fill_missing_strategy.apply(sample_dataframe)

    assert processed_df["NumericalColumn"].isnull().sum() == 0
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['missing_values_filled']


def test_fill_missing_values_with_categorical(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)

    categorical_selectbox = MagicMock(side_effect=["Mode", "Mode"])
    mock_st.selectbox = categorical_selectbox

    mock_st.text_input = MagicMock(return_value="DefaultValue")

    fill_missing_strategy = FillMissingValues()
    processed_df = fill_missing_strategy.apply(sample_dataframe)

    assert processed_df["CategoricalColumn"].isnull().sum() == 0
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['missing_values_filled']
