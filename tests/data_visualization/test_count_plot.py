import pytest
import pandas as pd
from pages.data_visualization import CountPlot

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Category": ["A", "B", "A", "C", "B", "C", "C", "A", "B", "C"]
    })

@pytest.fixture
def count_plot_instance():
    return CountPlot()

def test_count_plot_valid_data(sample_dataframe, count_plot_instance, mocker):
    mock_st_plotly_chart = mocker.patch("streamlit.plotly_chart")

    count_plot_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        chart_title="Valid Count Plot",
        color_scheme="Plotly",
        font_family="Arial",
        font_size=14
    )

    mock_st_plotly_chart.assert_called_once()

def test_count_plot_missing_x_column(sample_dataframe, count_plot_instance, mocker):
    mock_st_warning = mocker.patch("streamlit.warning")

    count_plot_instance.plot(
        df=sample_dataframe,
        x_column=None,
        chart_title="Missing X Column",
        color_scheme="Plotly",
        font_family="Arial",
        font_size=14
    )

    mock_st_warning.assert_called_once_with("Please select a valid column for the Count Plot.")