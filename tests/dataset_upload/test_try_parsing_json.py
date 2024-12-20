import pytest
from io import BytesIO
from dataset import Dataset


def test_try_parsing_json_success():
    """
    Test that valid JSON is successfully parsed.
    """
    json_content = '{"name": "Alice", "age": 30, "city": "New York"}\n' \
                   '{"name": "Bob", "age": 25, "city": "Los Angeles"}'
    uploaded_file = BytesIO(json_content.encode('utf-8'))  

    result = Dataset.try_parsing_json(uploaded_file)

    assert result is not None, "Result should not be None for valid JSON input"
    assert len(result) == 2, "There should be two records in the result"
    assert result.iloc[0]["name"] == "Alice", "First record name should be Alice"
    assert result.iloc[1]["city"] == "Los Angeles", "Second record city should be Los Angeles"

def test_try_parsing_json_failure():
    """
    Test that invalid JSON raises an error and returns None.
    """
    invalid_json_content = '{"name": "Alice", "age": 30, "city": "New York",}\n' \
                           '{"name": "Bob", "age": "twenty-five", "city": "Los Angeles"'
    uploaded_file = BytesIO(invalid_json_content.encode('utf-8'))  

    result = Dataset.try_parsing_json(uploaded_file)

    assert result is None, "Result should be None for invalid JSON input"
