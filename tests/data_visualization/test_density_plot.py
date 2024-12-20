import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pages.data_visualization import DensityPlot


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    return pd.DataFrame({
        "X": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Y": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "Z": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    })


@pytest.fixture
def density_plot_instance():
    """Fixture to provide a DensityPlot instance."""
    return DensityPlot()


def test_density_plot_valid_2d(sample_dataframe, density_plot_instance, mocker):
    """Test 2D DensityPlot with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    density_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y"],
        chart_title="Valid 2D Density Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_density_plot_valid_3d(sample_dataframe, density_plot_instance, mocker):
    """Test 3D DensityPlot with valid data and color scheme."""
    mock_st = mocker.patch("pages.data_visualization.st")
    density_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y"],
        z_column="Z",
        chart_title="Valid 3D Density Plot",
        color_scheme="viridis",
        is_3d=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_density_plot_missing_columns(sample_dataframe, density_plot_instance, mocker):
    """Test DensityPlot with missing or invalid columns."""
    mock_st = mocker.patch("pages.data_visualization.st")

    density_plot_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Y"],
        chart_title="Missing X Column",
    )
    mock_st.warning.assert_called_once_with("Please select valid X, Y, and optionally Z columns for the density plot.")

    mock_st.reset_mock()
    density_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=None,
        chart_title="Missing Y Columns",
    )
    mock_st.warning.assert_called_once_with("Please select valid X, Y, and optionally Z columns for the density plot.")


def test_density_plot_multiple_y_columns(sample_dataframe, density_plot_instance, mocker):
    """Test DensityPlot with multiple Y-axis columns."""
    mock_st = mocker.patch("pages.data_visualization.st")
    density_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y", "Z"],
        chart_title="Multiple Y Columns"
    )
    mock_st.warning.assert_called_once_with("Density plots only support a single Y-axis feature. Please select one Y-axis feature.")


def test_density_plot_unmatched_columns(sample_dataframe, density_plot_instance, mocker):
    """Test DensityPlot with unmatched column names."""
    mock_st = mocker.patch("pages.data_visualization.st")
    density_plot_instance.plot(
        df=sample_dataframe,
        x_column="InvalidX",
        y_columns=["InvalidY"],
        chart_title="Unmatched Columns"
    )
    mock_st.warning.assert_called_once_with("The following columns are missing in the DataFrame: InvalidX, InvalidY")