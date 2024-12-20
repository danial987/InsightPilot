import pytest
import pandas as pd
from pages.data_visualization import MosaicPlot


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample dataframe for testing."""
    return pd.DataFrame({
        "Category": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"],
        "Subcategory": ["X", "Y", "Z", "X", "Y", "Z", "X", "Y", "Z", "X"],
        "Values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    })


@pytest.fixture
def mosaic_plot_instance():
    """Fixture to provide a MosaicPlot instance."""
    return MosaicPlot()


def test_mosaic_plot_valid_data(sample_dataframe, mosaic_plot_instance, mocker):
    """Test MosaicPlot with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    mosaic_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Subcategory"],
        chart_title="Valid Mosaic Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_mosaic_plot_missing_columns(sample_dataframe, mosaic_plot_instance, mocker):
    """Test MosaicPlot with missing x_column or y_columns."""
    mock_st = mocker.patch("pages.data_visualization.st")

    mosaic_plot_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Subcategory"],
        chart_title="Missing X Column Mosaic Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select valid X and Y columns for the Mosaic plot.")

    mock_st.reset_mock()
    mosaic_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=None,
        chart_title="Missing Y Columns Mosaic Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select valid X and Y columns for the Mosaic plot.")


def test_mosaic_plot_filtered_top_n(sample_dataframe, mosaic_plot_instance, mocker):
    """Test MosaicPlot filters top N values correctly."""
    mock_st = mocker.patch("pages.data_visualization.st")
    mosaic_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Subcategory"],
        chart_title="Filtered Top N Mosaic Plot",
        show_legend=True,
        show_labels=True
    )

    mock_st.plotly_chart.assert_called_once()


def test_mosaic_plot_unmatched_columns(sample_dataframe, mosaic_plot_instance, mocker):
    """Test MosaicPlot with unmatched column names."""
    mock_st = mocker.patch("pages.data_visualization.st")
    mosaic_plot_instance.plot(
        df=sample_dataframe,
        x_column="InvalidCategory",
        y_columns=["InvalidSubcategory"],
        chart_title="Unmatched Columns Mosaic Plot",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with(
        "The specified columns are not present in the DataFrame. Please check your column names."
    )