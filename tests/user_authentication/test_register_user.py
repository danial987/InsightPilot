import pytest
from unittest.mock import patch, MagicMock
from auth import User


@patch("auth.User.connect_db")
def test_register_user_success(mock_connect_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.__enter__.return_value = mock_cur

    mock_connect_db.return_value = mock_conn
    user = User()
    mock_cur.fetchone.return_value = None
    mock_cur.execute.return_value = None 

    result = user.register_user("newuser", "user@example.com", "StrongPass123!")

    print(f"Mock connect_db calls: {mock_connect_db.call_args_list}")
    print(f"Mock cursor execute calls: {mock_cur.execute.call_args_list}")
    print(f"Result of registration: {result}")

    assert result is True  
    mock_connect_db.assert_called_once() 
    mock_conn.cursor.assert_called_once()  
    mock_cur.execute.assert_called_once_with(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        ("newuser", "user@example.com", user.hash_password("StrongPass123!"))
    )  


@patch("auth.User.connect_db")
def test_register_user_duplicate(mock_connect_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect_db.return_value = mock_conn

    user = User()

    def mock_execute(query, params):
        if "INSERT INTO users" in query:
            raise errors.UniqueViolation("Duplicate entry detected")

    mock_cur.execute.side_effect = mock_execute

    result = user.register_user("existinguser", "existingemail@example.com", "StrongPass123!")

    print(f"Mock connect_db calls: {mock_connect_db.call_args_list}")
    print(f"Mock cursor execute calls: {mock_cur.execute.call_args_list}")
    print(f"Result of duplicate registration: {result}")

    assert result is False 
    mock_connect_db.assert_called_once()  
    mock_conn.cursor.assert_called_once()  
    mock_cur.execute.assert_called_once_with(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        ("existinguser", "existingemail@example.com", user.hash_password("StrongPass123!"))
    ) 