import pytest
import pandas as pd
from unittest.mock import MagicMock
from pages.data_preprocessing import RemoveDuplicates


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Column1": [1, 2, 2, 3, 4],
        "Column2": ["A", "B", "B", "C", "D"]
    })


def test_remove_duplicates_no_duplicates(mocker):
    df = pd.DataFrame({
        "Column1": [1, 2, 3, 4],
        "Column2": ["A", "B", "C", "D"]
    })
    mock_st = mocker.patch("pages.data_preprocessing.st")
    remove_duplicates_strategy = RemoveDuplicates()
    processed_df = remove_duplicates_strategy.apply(df)

    assert processed_df.equals(df)
    mock_st.warning.assert_called_once_with("This dataset has no duplicates.")
    mock_st.success.assert_not_called()


def test_remove_duplicates_with_duplicates(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)

    remove_duplicates_strategy = RemoveDuplicates()
    processed_df = remove_duplicates_strategy.apply(sample_dataframe)

    assert len(processed_df) == 4
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['duplicates_removed']
    assert not mock_st.session_state.get('show_duplicates_dialog', False)


def test_remove_duplicates_integration(mocker, sample_dataframe):
    mock_st = mocker.patch("pages.data_preprocessing.st")
    mock_st.session_state = {}

    def mock_dialog_decorator(title):
        def decorator(func):
            func()  
            return func
        return decorator

    mock_st.dialog = MagicMock(side_effect=mock_dialog_decorator)
    mock_st.button = MagicMock(return_value=True)

    remove_duplicates_strategy = RemoveDuplicates()
    processed_df = remove_duplicates_strategy.apply(sample_dataframe)

    assert len(processed_df) == 4
    assert mock_st.success.call_count == 1
    assert mock_st.session_state['duplicates_removed']
