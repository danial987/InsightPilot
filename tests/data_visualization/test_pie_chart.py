import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_visualization import PieChart

@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    return pd.DataFrame({
        'Category1': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'B', 'C', 'A'],
        'Category2': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'X', 'Y', 'Z', 'X']
    })

@pytest.fixture
def pie_chart_instance():
    """Fixture to provide a PieChart instance."""
    return PieChart()


def test_pie_chart_valid_data(sample_dataframe, pie_chart_instance, mocker):
    """Test PieChart with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    pie_chart_instance.plot(
        df=sample_dataframe,
        y_columns=['Category1'],
        chart_title="Test Pie Chart",
        show_legend=True,
        show_labels=True
    )
    assert mock_st.plotly_chart.called, "Plotly chart was not rendered."


def test_pie_chart_missing_y_columns(sample_dataframe, pie_chart_instance, mocker):
    """Test PieChart when y_columns are missing."""
    mock_st = mocker.patch("pages.data_visualization.st")
    pie_chart_instance.plot(
        df=sample_dataframe,
        y_columns=None,
        chart_title="Test Pie Chart",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()
    args, kwargs = mock_st.plotly_chart.call_args
    assert "No features selected for Pie Chart." in args[0].layout.annotations[0].text


def test_pie_chart_combined_column(sample_dataframe, pie_chart_instance, mocker):
    """Test PieChart combining multiple categorical columns."""
    mock_st = mocker.patch("pages.data_visualization.st")
    pie_chart_instance.plot(
        df=sample_dataframe,
        y_columns=['Category1', 'Category2'],
        chart_title="Combined Categories Pie Chart",
        show_legend=True,
        show_labels=True
    )
    assert 'Category1_Category2' in sample_dataframe.columns, "Combined column was not created."