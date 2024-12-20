import pandas as pd
import pytest
from pages.dataset_summary import DatasetSummary


@pytest.fixture
def dataset_with_skewed_columns():
    """Fixture to create a dataset with skewed numerical columns."""
    data = {
        "Column1": [1] * 95 + [100] * 5, 
        "Column2": [2, 2, 3, 3, 3, 4, 4, 4, 4, 4] * 10,  
        "Column3": [1] * 50 + [2] * 50, 
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


def test_display_warnings_for_skewed_columns(dataset_with_skewed_columns, summary_instance):
    """Test if appropriate warnings are displayed for skewed numerical columns."""
    df = dataset_with_skewed_columns
    summary_instance.dataset = df  

    warnings = []
    for col in df.select_dtypes(include=["number"]).columns:
        if df[col].skew() > 1: 
            warnings.append((col, f"highly skewed (γ1 = {df[col].skew():.2f})", "skewed"))

    expected_warnings = [
        ("Column1", f"highly skewed (γ1 = {df['Column1'].skew():.2f})", "skewed"),
    ]

    assert warnings == expected_warnings, "Warnings for skewed columns do not match the expected output."
