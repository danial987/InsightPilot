import pytest
from unittest.mock import MagicMock
import pandas as pd
from sklearn.ensemble import IsolationForest
from scipy.stats import zscore
from pages.data_preprocessing import OutlierHandling


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Feature1": [1, 2, 3, 100, 5],  
        "Feature2": [10, 20, 30, 40, 50],
        "Category": ["A", "B", "C", "D", "E"]
    })

def test_outlier_handling_no_numerical_columns(mocker):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.warning = MagicMock()

    df = pd.DataFrame({"Category": ["A", "B", "C", "D", "E"]})
    outlier_strategy = OutlierHandling()
    processed_df = outlier_strategy.apply(df)

    assert processed_df.equals(df)
    mock_st.warning.assert_called_once_with("This dataset has no numerical columns to check for outliers.")
    

def test_outlier_handling_missing_values(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.error = MagicMock()

    sample_dataframe.loc[1, "Feature1"] = None 
    outlier_strategy = OutlierHandling()
    processed_df = outlier_strategy.apply(sample_dataframe)

    assert processed_df.equals(sample_dataframe)
    mock_st.error.assert_called_once_with("The dataset contains missing values. Please handle missing values before performing outlier detection.")


def test_outlier_handling_isolation_forest(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.slider = MagicMock(return_value=0.2)  
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()

    outlier_strategy = OutlierHandling()
    processed_df = outlier_strategy.apply(sample_dataframe)

    assert "Feature1" in processed_df.columns
    assert "Feature2" in processed_df.columns

    isolation_forest = IsolationForest(contamination=0.2, random_state=42)
    predictions = isolation_forest.fit_predict(sample_dataframe[["Feature1", "Feature2"]])
    mask = predictions == 1 
    expected_df = sample_dataframe[mask]

    pd.testing.assert_frame_equal(processed_df.reset_index(drop=True), expected_df.reset_index(drop=True))

    mock_st.success.assert_called_once_with("Outlier handling using Isolation Forest has been applied.")


def test_outlier_handling_z_score(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}
    mock_st.dialog = MagicMock(side_effect=lambda title: lambda func: func())
    mock_st.slider = MagicMock(return_value=2.0) 
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()

    outlier_strategy = OutlierHandling()
    processed_df = outlier_strategy.apply(sample_dataframe)

    assert "Feature1" in processed_df.columns
    assert "Feature2" in processed_df.columns

    z_scores = zscore(sample_dataframe[["Feature1", "Feature2"]])
    mask = (abs(z_scores) < 2).all(axis=1)
    expected_df = sample_dataframe[mask]

    pd.testing.assert_frame_equal(processed_df.reset_index(drop=True), expected_df.reset_index(drop=True))

    mock_st.success.assert_called_once_with("Outlier handling using Z-Score has been applied.")
