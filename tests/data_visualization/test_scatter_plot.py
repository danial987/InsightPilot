import pytest
import pandas as pd
from pages.data_visualization import ScatterPlot


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Category": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"],
        "Value1": [10, 20, 30, 10, 20, 30, 10, 20, 30, 10],
        "Value2": [5, 15, 25, 5, 15, 25, 5, 15, 25, 5],
        "Value3": [1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
    })

@pytest.fixture
def scatter_plot_instance():
    return ScatterPlot()


def test_scatter_plot_valid_data(sample_dataframe, scatter_plot_instance, mocker):
    """Test ScatterPlot with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    scatter_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1"],
        chart_title="Valid Scatter Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_scatter_plot_missing_x_column(sample_dataframe, scatter_plot_instance, mocker):
    """Test ScatterPlot when X-axis column is missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    scatter_plot_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Value1"],
        chart_title="Missing X Column Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a scatter plot.")


def test_scatter_plot_missing_y_columns(sample_dataframe, scatter_plot_instance, mocker):
    """Test ScatterPlot when Y-axis columns are missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    scatter_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=None,
        chart_title="Missing Y Columns Test",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select an X-axis column and at least one Y-axis column to generate a scatter plot.")


def test_scatter_plot_3d_valid_data(sample_dataframe, scatter_plot_instance, mocker):
    """Test ScatterPlot in 3D mode with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    scatter_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1"],
        z_column="Value3",
        chart_title="3D Valid Scatter Plot",
        show_legend=True,
        show_labels=True,
        is_3d=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_scatter_plot_3d_missing_z_column(sample_dataframe, scatter_plot_instance, mocker):
    """Test ScatterPlot in 3D mode with missing Z column."""
    mock_st = mocker.patch("pages.data_visualization.st")
    scatter_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Value1"],
        z_column=None,
        chart_title="3D Scatter Plot Missing Z Column",
        show_legend=True,
        show_labels=True,
        is_3d=True
    )
    mock_st.warning.assert_called_once_with("Please select valid X, Y, and Z columns for the 3D scatter plot.")