def test_input_validation():
    from validators import validate_email, validate_price, validate_name, validate_id

    assert validate_email("test@example.com")   
    assert not validate_email("invalid-email")
    assert validate_price(100)
    assert not validate_price(-50)  
    assert not validate_price("not-a-number")
    assert validate_name("Valid Name")
    assert not validate_name("")
    assert not validate_name("A"*50)  
    assert validate_id(123)
    assert not validate_id(-1)
    assert not validate_id("abc")