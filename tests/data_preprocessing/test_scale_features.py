import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_preprocessing import ScaleFeatures


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "NumericalColumn1": [1.0, 2.0, 3.0, 4.0],
        "NumericalColumn2": [10.0, 20.0, 30.0, 40.0],
        "CategoricalColumn": ["A", "B", "C", "D"]
    })


def test_scale_features_no_numerical_columns(mocker):
    df = pd.DataFrame({
        "CategoricalColumn": ["A", "B", "C", "D"]
    })
    mock_st = mocker.patch("pages.data_preprocessing.st")
    scale_features_strategy = ScaleFeatures()
    processed_df = scale_features_strategy.apply(df)

    assert processed_df.equals(df)
    mock_st.warning.assert_called_once_with("This dataset has no numerical columns to scale.")
    mock_st.success.assert_not_called()


def test_scale_features_with_standardization(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)
    mock_st.selectbox = MagicMock(return_value="Standardization (Mean=0, Std=1)")

    scale_features_strategy = ScaleFeatures()
    processed_df = scale_features_strategy.apply(sample_dataframe)

    assert processed_df.select_dtypes(include=['float64']).shape[1] == 2
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['scaling_applied']


def test_scale_features_with_normalization(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)
    mock_st.selectbox = MagicMock(return_value="Normalization (0-1 range)")

    scale_features_strategy = ScaleFeatures()
    processed_df = scale_features_strategy.apply(sample_dataframe)

    assert processed_df["NumericalColumn1"].max() <= 1.0
    assert processed_df["NumericalColumn1"].min() >= 0.0
    assert processed_df["NumericalColumn2"].max() <= 1.0
    assert processed_df["NumericalColumn2"].min() >= 0.0
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['scaling_applied']
