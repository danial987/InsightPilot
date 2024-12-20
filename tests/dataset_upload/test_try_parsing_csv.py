import pytest
from io import StringIO
from dataset import Dataset
import pandas as pd


def test_try_parsing_csv_success():
    csv_content = "name,age,city\nAlice,30,New York\nBob,25,Los Angeles"
    uploaded_file = StringIO(csv_content)

    result = Dataset.try_parsing_csv(uploaded_file)

    assert result is not None  
    assert len(result) == 2 
    assert list(result.columns) == ["name", "age", "city"]  
    

def test_try_parsing_csv_failure():
    invalid_csv_content = "name,age,city\nAlice,30,New York\nBob,25"
    uploaded_file = StringIO(invalid_csv_content)

    result = Dataset.try_parsing_csv(uploaded_file)

    assert result is not None
    assert result.isnull().values.any()  