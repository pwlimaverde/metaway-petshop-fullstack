from metaway_api.domain.enums import ContactType, UserRole


def test_user_role_values() -> None:
    assert UserRole.ADMIN == "ADMIN"
    assert UserRole.CLIENTE == "CLIENTE"
    assert len(UserRole) == 2


def test_contact_type_values() -> None:
    assert ContactType.EMAIL == "EMAIL"
    assert ContactType.TELEFONE == "TELEFONE"
    assert len(ContactType) == 2
