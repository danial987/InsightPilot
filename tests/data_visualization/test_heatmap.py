import pytest
import pandas as pd
from pages.data_visualization import HeatMap


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample dataframe for testing."""
    return pd.DataFrame({
        "Numeric1": [1, 2, 3, 4, 5],
        "Numeric2": [5, 4, 3, 2, 1],
        "Numeric3": [2, 3, 4, 5, 6],
        "Category": ["A", "B", "C", "A", "B"]
    })


@pytest.fixture
def heatmap_instance():
    """Fixture to provide a HeatMap instance."""
    return HeatMap()


def test_heatmap_valid_data(sample_dataframe, heatmap_instance, mocker):
    """Test HeatMap with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    heatmap_instance.plot(
        df=sample_dataframe,
        y_columns=["Numeric1", "Numeric2"],
        chart_title="Valid HeatMap",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_heatmap_missing_y_columns(sample_dataframe, heatmap_instance, mocker):
    """Test HeatMap with missing y_columns."""
    mock_st = mocker.patch("pages.data_visualization.st")
    heatmap_instance.plot(
        df=sample_dataframe,
        y_columns=None,
        chart_title="Missing Y Columns HeatMap",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select at least two numeric columns to generate a heatmap.")


def test_heatmap_not_enough_columns(sample_dataframe, heatmap_instance, mocker):
    """Test HeatMap with less than two numeric columns."""
    mock_st = mocker.patch("pages.data_visualization.st")
    heatmap_instance.plot(
        df=sample_dataframe,
        y_columns=["Numeric1"],
        chart_title="Not Enough Columns HeatMap",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select at least two numeric columns to generate a heatmap.")


def test_heatmap_invalid_column_names(sample_dataframe, heatmap_instance, mocker):
    """Test HeatMap with invalid column names."""
    mock_st = mocker.patch("pages.data_visualization.st")
    heatmap_instance.plot(
        df=sample_dataframe,
        y_columns=["InvalidColumn1", "InvalidColumn2"],
        chart_title="Invalid Column Names HeatMap",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with(
        "Some columns specified were not found in the DataFrame: \"None of [Index(['InvalidColumn1', 'InvalidColumn2'], dtype='object')] are in the [columns]\""
    )


def test_heatmap_3d_valid_data(sample_dataframe, heatmap_instance, mocker):
    """Test HeatMap in 3D mode with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    heatmap_instance.plot(
        df=sample_dataframe,
        y_columns=["Numeric1", "Numeric2"],
        chart_title="Valid 3D HeatMap",
        show_legend=True,
        show_labels=True,
        is_3d=True
    )
    mock_st.plotly_chart.assert_called_once()
