import pytest
from unittest.mock import patch, MagicMock
from auth import User


@patch("auth.User.connect_db")
def test_authenticate_user(mock_connect_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect_db.return_value = mock_conn

    user = User()
    mock_cur.fetchone.return_value = (1,)  
    result = user.authenticate_user("validuser", "ValidPass123!")

    print(f"Mock connect_db calls: {mock_connect_db.call_args_list}")
    print(f"Mock cursor execute calls: {mock_cur.execute.call_args_list}")
    print(f"Result of authentication: {result}")

    assert result == (1,) 
    mock_connect_db.assert_called_once()  
    mock_conn.cursor.assert_called_once()
    mock_cur.execute.assert_called_once_with(
        "SELECT user_id FROM users WHERE (username = %s OR email = %s) AND password = %s",
        ("validuser", "validuser", user.hash_password("ValidPass123!"))
    )  


@patch("auth.User.connect_db")
def test_authenticate_user_invalid(mock_connect_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect_db.return_value = mock_conn

    user = User()

    mock_cur.fetchone.return_value = None 

    result = user.authenticate_user("invaliduser", "InvalidPass123!")

    print(f"Mock connect_db calls: {mock_connect_db.call_args_list}")
    print(f"Mock cursor execute calls: {mock_cur.execute.call_args_list}")
    print(f"Result of authentication: {result}")

    assert result is None  
    mock_connect_db.assert_called_once() 
    mock_conn.cursor.assert_called_once()  
    mock_cur.execute.assert_called_once_with(
        "SELECT user_id FROM users WHERE (username = %s OR email = %s) AND password = %s",
        ("invaliduser", "invaliduser", user.hash_password("InvalidPass123!"))
    ) 