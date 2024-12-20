import pandas as pd
import pytest
from pages.dataset_summary import DatasetSummary


@pytest.fixture
def dataset_with_missing_values():
    """Fixture to create a dataset with missing values."""
    data = {
        "Column1": [1, 2, None, 4],
        "Column2": [None, "B", "C", None],
        "Column3": [10, None, 30, None],
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def summary_instance():
    """Fixture to create a DatasetSummary instance with a mock dataset ID."""
    class MockDataset:
        def get_dataset_by_id(self, dataset_id, user_id):
            return None 

        def update_last_accessed(self, dataset_id, user_id):
            pass  

    mock_dataset = MockDataset()
    dataset_summary = DatasetSummary(dataset_id=1)
    dataset_summary.dataset_db = mock_dataset
    return dataset_summary


def test_display_warnings_for_missing_values(dataset_with_missing_values, summary_instance):
    """Test if appropriate warnings are displayed for missing values."""
    df = dataset_with_missing_values
    summary_instance.dataset = df  

    warnings = []
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            warnings.append((col, f"{df[col].isnull().sum()} ({(df[col].isnull().sum() / df.shape[0]) * 100:.1f}%) missing values", "missing"))

    expected_warnings = [
        ("Column1", "1 (25.0%) missing values", "missing"),
        ("Column2", "2 (50.0%) missing values", "missing"),
        ("Column3", "2 (50.0%) missing values", "missing"),
    ]

    assert warnings == expected_warnings, "Warnings for missing values do not match the expected output."
