import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_visualization import CorrelationMatrix

@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame."""
    return pd.DataFrame({
        "Numeric1": [1, 2, 3, 4, 5],
        "Numeric2": [5, 4, 3, 2, 1],
        "Numeric3": [2, 3, 4, 5, 6],
        "Category": ["A", "B", "C", "A", "B"]
    })

@pytest.fixture
def correlation_matrix_instance():
    """Fixture to create a CorrelationMatrix instance."""
    return CorrelationMatrix()

def test_correlation_matrix_valid_data(sample_dataframe, correlation_matrix_instance, mocker):
    """Test CorrelationMatrix with valid numeric data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    correlation_matrix_instance.plot(
        df=sample_dataframe,
        y_columns=["Numeric1", "Numeric2", "Numeric3"],
        chart_title="Valid Correlation Matrix Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_not_called()
    mock_st.plotly_chart.assert_called_once()

def test_correlation_matrix_not_enough_numeric_columns(sample_dataframe, correlation_matrix_instance, mocker):
    """Test CorrelationMatrix when there are less than two numeric columns."""
    mock_st = mocker.patch("pages.data_visualization.st")
    small_df = sample_dataframe[["Numeric1"]]
    correlation_matrix_instance.plot(
        df=small_df,
        y_columns=None,
        chart_title="Not Enough Numeric Columns Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Not enough numeric columns for correlation matrix.")

def test_correlation_matrix_empty_dataframe(correlation_matrix_instance, mocker):
    """Test CorrelationMatrix with an empty DataFrame."""
    mock_st = mocker.patch("pages.data_visualization.st")
    empty_df = pd.DataFrame()
    correlation_matrix_instance.plot(
        df=empty_df,
        y_columns=None,
        chart_title="Empty DataFrame Correlation Matrix",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Not enough numeric columns for correlation matrix.")

def test_correlation_matrix_valid_data_3d(sample_dataframe, correlation_matrix_instance, mocker):
    """Test CorrelationMatrix in 3D mode with valid numeric data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    correlation_matrix_instance.plot(
        df=sample_dataframe,
        y_columns=["Numeric1", "Numeric2", "Numeric3"],
        chart_title="3D Correlation Matrix Test",
        show_legend=True,
        show_labels=True,
        is_3d=True
    )
    mock_st.warning.assert_not_called()
    mock_st.plotly_chart.assert_called_once()

def test_correlation_matrix_invalid_column_names(sample_dataframe, correlation_matrix_instance, mocker):
    """Test CorrelationMatrix with invalid column names."""
    mock_st = mocker.patch("pages.data_visualization.st")
    correlation_matrix_instance.plot(
        df=sample_dataframe,
        y_columns=["InvalidColumn"],
        chart_title="Invalid Column Names Correlation Matrix",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Invalid columns: InvalidColumn. Please provide valid numeric columns.")

