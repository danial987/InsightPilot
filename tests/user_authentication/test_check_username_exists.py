import pytest
from unittest.mock import patch, MagicMock
from auth import User


@patch("auth.User.connect_db")
def test_check_username_exists_found(mock_connect_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect_db.return_value = mock_conn

    user = User()
    mock_cur.fetchone.return_value = ("existinguser",)  
    result = user.check_username_exists("existinguser")

    print(f"Mock connect_db calls: {mock_connect_db.call_args_list}")
    print(f"Mock cursor execute calls: {mock_cur.execute.call_args_list}")
    print(f"Result of check_username_exists: {result}")

    assert result is True 
    mock_connect_db.assert_called_once() 
    mock_conn.cursor.assert_called_once()  
    mock_cur.execute.assert_called_once_with(
        "SELECT username FROM users WHERE username = %s",
        ("existinguser",)
    )  
    

@patch("auth.User.connect_db")
def test_check_username_exists_not_found(mock_connect_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect_db.return_value = mock_conn

    user = User()
    mock_cur.fetchone.return_value = None  
    result = user.check_username_exists("nonexistentuser")

    print(f"Mock connect_db calls: {mock_connect_db.call_args_list}")
    print(f"Mock cursor execute calls: {mock_cur.execute.call_args_list}")
    print(f"Result of check_username_exists: {result}")

    assert result is False  
    mock_connect_db.assert_called_once() 
    mock_conn.cursor.assert_called_once()  
    mock_cur.execute.assert_called_once_with(
        "SELECT username FROM users WHERE username = %s",
        ("nonexistentuser",)
    )  
