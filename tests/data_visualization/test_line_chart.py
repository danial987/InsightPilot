import pytest
from unittest.mock import MagicMock
import pandas as pd
from pages.data_visualization import LineChart


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Category": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"],
        "Value1": [10, 20, 30, 10, 20, 30, 10, 20, 30, 10],
        "Value2": [5, 15, 25, 5, 15, 25, 5, 15, 25, 5],
        "Value3": [1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
    })


@pytest.fixture
def line_chart_instance():
    return LineChart()


def test_line_chart_valid_data(sample_dataframe, line_chart_instance, mocker):
    """Test LineChart with valid X and Y columns."""
    mock_st = mocker.patch("pages.data_visualization.st")
    line_chart_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1", "Value2"],
        chart_title="Test Line Chart",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_line_chart_missing_x_column(sample_dataframe, line_chart_instance, mocker):
    """Test LineChart when X-axis column is missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    line_chart_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Value1"],
        chart_title="Missing X Column Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a line chart.")


def test_line_chart_missing_y_columns(sample_dataframe, line_chart_instance, mocker):
    """Test LineChart when Y-axis columns are missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    line_chart_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=None,
        chart_title="Missing Y Columns Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a line chart.")


def test_line_chart_3d_valid_data(sample_dataframe, line_chart_instance, mocker):
    """Test LineChart in 3D mode with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    line_chart_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1"],
        z_column="Value2",
        chart_title="3D Line Chart Test",
        show_legend=True,
        show_labels=True,
        is_3d=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_line_chart_3d_missing_z_column(sample_dataframe, line_chart_instance, mocker):
    """Test LineChart in 3D mode with missing Z column."""
    mock_st = mocker.patch("pages.data_visualization.st")
    line_chart_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1"],
        z_column=None,
        chart_title="3D Line Chart Missing Z Test",
        show_legend=True,
        show_labels=True,
        is_3d=True
    )
    mock_st.warning.assert_called_once_with("Please select a valid Z-axis column to generate a 3D line chart.")