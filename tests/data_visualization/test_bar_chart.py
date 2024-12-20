import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from pages.data_visualization import BarChart


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    return pd.DataFrame({
        "X": ["A", "B", "C", "D"],
        "Y1": [10, 20, 30, 40],
        "Y2": [15, 25, 35, 45],
        "Z": [100, 200, 300, 400]
    })


@pytest.fixture
def bar_chart_instance():
    """Fixture to provide a BarChart instance."""
    return BarChart()


def test_bar_chart_valid_data_2d(sample_dataframe, bar_chart_instance, mocker):
    """Test 2D BarChart with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    bar_chart_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y1", "Y2"],
        chart_title="Valid 2D Bar Chart",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_bar_chart_valid_data_3d(sample_dataframe, bar_chart_instance, mocker):
    """Test 3D BarChart with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    bar_chart_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y1"],
        z_column="Z",
        chart_title="Valid 3D Bar Chart",
        is_3d=True,
        show_legend=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_bar_chart_missing_columns(sample_dataframe, bar_chart_instance, mocker):
    """Test BarChart with missing or invalid columns."""
    mock_st = mocker.patch("pages.data_visualization.st")

    bar_chart_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Y1"],
        chart_title="Missing X Column"
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a bar chart.")

    mock_st.reset_mock()
    bar_chart_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=None,
        chart_title="Missing Y Columns"
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a bar chart.")



def test_bar_chart_unmatched_columns(sample_dataframe, bar_chart_instance, mocker):
    """Test BarChart with unmatched column names."""
    mock_st = mocker.patch("pages.data_visualization.st")
    bar_chart_instance.plot(
        df=sample_dataframe,
        x_column="InvalidX",
        y_columns=["InvalidY"],
        z_column="InvalidZ",
        chart_title="Unmatched Columns"
    )
    mock_st.warning.assert_called_once_with("The following columns are missing in the DataFrame: InvalidX, InvalidY, InvalidZ")