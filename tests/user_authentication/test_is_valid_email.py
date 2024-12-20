from auth import is_valid_email


def test_is_valid_email():
    assert is_valid_email("test@example.com") is True
    assert is_valid_email("user.name@domain.co.in") is True
    assert is_valid_email("user+alias@domain.com") is True
    assert is_valid_email("email@sub.domain.com") is True  
    assert is_valid_email("firstname-lastname@domain.com") is True  

    assert is_valid_email("plainaddress") is False  
    assert is_valid_email("@missingusername.com") is False 
    assert is_valid_email("user@.com") is False  
    assert is_valid_email("user@com") is False 
    assert is_valid_email("user@domain..com") is False 
    assert is_valid_email(".email@domain.com") is False  
    assert is_valid_email("email.@domain.com") is False  
