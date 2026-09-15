from app.security.sql_guard import validate_sql

def test_select_is_allowed():
    assert validate_sql("SELECT * FROM customers").valid

def test_mutation_is_blocked():
    result = validate_sql("DROP TABLE customers")
    assert not result.valid

def test_injection_is_blocked():
    result = validate_sql("SELECT * FROM customers; DELETE FROM customers")
    assert not result.valid
    assert any("Multiple" in error for error in result.errors)

def test_comments_are_blocked():
    assert not validate_sql("SELECT * FROM customers -- bypass").valid
