import pytest
import pandas as pd
from unittest.mock import patch
from pages.data_visualization import StreamlinePlot


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    return pd.DataFrame({
        "X": [1, 2, 3, 4, 5],
        "Y": [10, 20, 30, 40, 50],
        "Z": [100, 200, 300, 400, 500]
    })


@pytest.fixture
def streamline_plot_instance():
    """Fixture to provide a StreamlinePlot instance."""
    return StreamlinePlot()


def test_streamline_plot_valid_data(sample_dataframe, streamline_plot_instance, mocker):
    """Test 3D StreamlinePlot with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    streamline_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y"],
        z_column="Z",
        chart_title="Valid Streamline Plot",
        show_legend=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_streamline_plot_missing_columns(sample_dataframe, streamline_plot_instance, mocker):
    """Test 3D StreamlinePlot with missing or invalid columns."""
    mock_st = mocker.patch("pages.data_visualization.st")

    streamline_plot_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Y"],
        z_column="Z",
        chart_title="Missing X Column"
    )
    mock_st.warning.assert_called_once_with("Please select X, Y, and Z columns for the 3D Streamline Plot.")

    mock_st.reset_mock()
    streamline_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=None,
        z_column="Z",
        chart_title="Missing Y Columns"
    )
    mock_st.warning.assert_called_once_with("Please select X, Y, and Z columns for the 3D Streamline Plot.")

    mock_st.reset_mock()
    streamline_plot_instance.plot(
        df=sample_dataframe,
        x_column="X",
        y_columns=["Y"],
        z_column=None,
        chart_title="Missing Z Column"
    )
    mock_st.warning.assert_called_once_with("Please select X, Y, and Z columns for the 3D Streamline Plot.")


def test_streamline_plot_unmatched_columns(sample_dataframe, streamline_plot_instance, mocker):
    """Test 3D StreamlinePlot with unmatched column names."""
    mock_st = mocker.patch("pages.data_visualization.st")
    streamline_plot_instance.plot(
        df=sample_dataframe,
        x_column="InvalidX",
        y_columns=["InvalidY"],
        z_column="InvalidZ",
        chart_title="Unmatched Columns"
    )
    mock_st.warning.assert_called_once_with("The following columns are missing in the DataFrame: InvalidX, InvalidY, InvalidZ")