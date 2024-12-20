import pytest
from unittest.mock import MagicMock
import pandas as pd
from pages.data_visualization import BoxPlot 

@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame."""
    data = {
        "Category": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"],
        "Value": [10, 20, 30, 10, 20, 30, 10, 20, 30, 10]
    }
    return pd.DataFrame(data)

@pytest.fixture
def box_plot_instance():
    """Fixture to provide an instance of BoxPlot."""
    return BoxPlot()

def test_box_plot_valid_data(sample_dataframe, box_plot_instance, mocker):
    """Test BoxPlot with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    box_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value"],
        chart_title="Valid Box Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()

def test_box_plot_missing_x_column(sample_dataframe, box_plot_instance, mocker):
    """Test BoxPlot when X-axis column is missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    box_plot_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Value"],
        chart_title="Missing X Column Box Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a box plot.")

def test_box_plot_missing_y_columns(sample_dataframe, box_plot_instance, mocker):
    """Test BoxPlot when Y-axis columns are missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    box_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=None,
        chart_title="Missing Y Columns Box Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a box plot.")


def test_box_plot_multiple_y_columns(sample_dataframe, box_plot_instance, mocker):
    """Test BoxPlot with multiple Y-axis columns (uses only the first one)."""
    mock_st = mocker.patch("pages.data_visualization.st")
    box_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value", "AnotherValue"],
        chart_title="Multiple Y Columns Box Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()
