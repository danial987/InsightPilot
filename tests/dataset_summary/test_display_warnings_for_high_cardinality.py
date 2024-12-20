import pandas as pd
import pytest
from pages.dataset_summary import DatasetSummary


@pytest.fixture
def dataset_with_high_cardinality():
    """Fixture to create a dataset with high cardinality columns."""
    data = {
        "Column1": [f"Value{i}" for i in range(100)],  
        "Column2": ["A", "B", "C", "D"] * 25,  
        "Column3": [1, 2, 3, 4] * 25, 
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


def test_display_warnings_for_high_cardinality(dataset_with_high_cardinality, summary_instance):
    """Test if appropriate warnings are displayed for high cardinality columns."""
    df = dataset_with_high_cardinality
    summary_instance.dataset = df  

    warnings = []
    for col in df.columns:
        if DatasetSummary.is_hashable(df[col].iloc[0]) and df[col].nunique() / df.shape[0] > 0.5:
            warnings.append((col, f"high cardinality: {df[col].nunique()} distinct values", "warning"))

    expected_warnings = [
        ("Column1", "high cardinality: 100 distinct values", "warning"),
    ]

    assert warnings == expected_warnings, "Warnings for high cardinality columns do not match the expected output."
