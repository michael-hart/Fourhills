from fourhills.utils.dnd_beyond_credentials import (
    save_password, get_password, clear_password
)


def test_password_roundtrip():
    testuser = "testuser"
    testpass = "testing1234$!"
    save_password(testuser, testpass)
    result = get_password(testuser)
    assert result == testpass
    clear_password(testuser)


def test_no_password_gives_none():
    testuser = "testuser"
    result = get_password(testuser)
    assert result is None


def test_clear_password_clears_password():
    testuser = "testuser"
    testpass = "testing1234$!"
    save_password(testuser, testpass)
    clear_password(testuser)
    result = get_password(testuser)
    assert result is None
