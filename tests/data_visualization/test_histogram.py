import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_visualization import Histogram

@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame."""
    return pd.DataFrame({
        "Category": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"],
        "Value1": [10, 20, 30, 10, 20, 30, 10, 20, 30, 10],
        "Value2": [5, 15, 25, 5, 15, 25, 5, 15, 25, 5]
    })

@pytest.fixture
def histogram_instance():
    """Fixture to create a Histogram instance."""
    return Histogram()

def test_histogram_valid_data(sample_dataframe, histogram_instance, mocker):
    """Test Histogram with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    histogram_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1"],
        chart_title="Valid Histogram Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_not_called()
    mock_st.plotly_chart.assert_called_once()

def test_histogram_missing_x_column(sample_dataframe, histogram_instance, mocker):
    """Test Histogram when X-axis column is missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    histogram_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Value1"],
        chart_title="Missing X Column Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and one Y-axis column to generate a histogram.")

def test_histogram_missing_y_columns(sample_dataframe, histogram_instance, mocker):
    """Test Histogram when Y-axis column is missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    histogram_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=None,
        chart_title="Missing Y Column Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and one Y-axis column to generate a histogram.")


def test_histogram_valid_multiple_y_columns(sample_dataframe, histogram_instance, mocker):
    """Test Histogram with multiple Y columns (only first used)."""
    mock_st = mocker.patch("pages.data_visualization.st")
    histogram_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1", "Value2"],
        chart_title="Valid Multiple Y Columns Histogram",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_not_called()
    mock_st.plotly_chart.assert_called_once()