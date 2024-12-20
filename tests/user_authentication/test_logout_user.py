import warnings
from unittest.mock import patch, MagicMock
import streamlit as st
from auth import logout_user


warnings.filterwarnings("ignore", category=RuntimeWarning)

@patch.object(st, "session_state", new_callable=MagicMock)
def test_logout_user(mock_session_state):
    mock_session_state.user_id = 1
    mock_session_state.authenticated = True

    logout_user()

    assert mock_session_state.user_id is None
    assert mock_session_state.authenticated is False
