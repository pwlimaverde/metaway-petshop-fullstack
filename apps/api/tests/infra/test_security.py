from metaway_api.infra.security import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    plain = "MySecurePassword1!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True


def test_verify_wrong_password() -> None:
    hashed = hash_password("CorrectPassword1!")
    assert verify_password("WrongPassword1!", hashed) is False


def test_hash_produces_different_hashes() -> None:
    plain = "SamePassword1!"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)
    assert hash1 != hash2  # bcrypt uses random salt
    assert verify_password(plain, hash1) is True
    assert verify_password(plain, hash2) is True
