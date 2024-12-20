import pytest
import pandas as pd
from pages.data_visualization import TreeMap


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    return pd.DataFrame({
        "Category": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"],
        "Subcategory": ["X", "Y", "Z", "X", "Y", "Z", "X", "Y", "Z", "X"],
        "Values": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })


@pytest.fixture
def tree_map_instance():
    """Fixture to provide a TreeMap instance."""
    return TreeMap()


def test_tree_map_valid_data(sample_dataframe, tree_map_instance, mocker):
    """Test TreeMap with valid data."""
    mock_st = mocker.patch("pages.data_visualization.st")
    tree_map_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Subcategory"],
        chart_title="Valid Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_tree_map_missing_columns(sample_dataframe, tree_map_instance, mocker):
    """Test TreeMap with missing x_column or y_columns."""
    mock_st = mocker.patch("pages.data_visualization.st")

    tree_map_instance.plot(
        df=sample_dataframe,
        x_column=None,
        y_columns=["Subcategory"],
        chart_title="Missing X Column Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select valid X and Y columns for the Tree Map.")

    mock_st.reset_mock()
    tree_map_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=None,
        chart_title="Missing Y Columns Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select valid X and Y columns for the Tree Map.")


def test_tree_map_invalid_grouping(sample_dataframe, tree_map_instance, mocker):
    """Test TreeMap with grouping error."""
    mock_st = mocker.patch("pages.data_visualization.st")

    sample_dataframe["Count"] = [1] * len(sample_dataframe)  

    tree_map_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Subcategory"],
        chart_title="Grouping Error Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.error.assert_called_once_with(
        "Error: cannot insert Count, already exists. Please ensure columns for grouping don't conflict with existing column names."
    )


def test_tree_map_filtered_top_n(sample_dataframe, tree_map_instance, mocker):
    """Test TreeMap filters top N values correctly."""
    mock_st = mocker.patch("pages.data_visualization.st")
    tree_map_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Subcategory"],
        chart_title="Filtered Top N Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.plotly_chart.assert_called_once()


def test_tree_map_y_column_same_as_x(sample_dataframe, tree_map_instance, mocker):
    """Test TreeMap when a Y-axis column is the same as the X-axis column."""
    mock_st = mocker.patch("pages.data_visualization.st")
    tree_map_instance.plot(
        df=sample_dataframe,
        x_column="Category",
        y_columns=["Category"],
        chart_title="Same X and Y Columns Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with("Please select at least one Y-axis column that is different from the X-axis column.")


def test_tree_map_unmatched_columns(sample_dataframe, tree_map_instance, mocker):
    """Test TreeMap with unmatched column names."""
    mock_st = mocker.patch("pages.data_visualization.st")

    tree_map_instance.plot(
        df=sample_dataframe,
        x_column="InvalidCategory",
        y_columns=["InvalidSubcategory"],
        chart_title="Unmatched Columns Tree Map",
        show_legend=True,
        show_labels=True
    )
    mock_st.warning.assert_called_once_with(
        "The following columns are missing in the DataFrame: InvalidCategory, InvalidSubcategory"
    )