from auth import is_valid_password


def test_is_valid_password():
    assert is_valid_password("Valid123!") is True
    assert is_valid_password("StrongPass@2021") is True

    assert is_valid_password("short") is False 
    assert is_valid_password("alllowercase") is False  
    assert is_valid_password("ALLUPPERCASE123") is False  
    assert is_valid_password("12345678!") is False  
    assert is_valid_password("NoSpecial123") is False 
