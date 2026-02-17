from metaway_api.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    OwnershipError,
)


def test_domain_error_hierarchy() -> None:
    assert issubclass(EntityNotFoundError, DomainError)
    assert issubclass(DuplicateEntityError, DomainError)
    assert issubclass(AuthenticationError, DomainError)
    assert issubclass(AuthorizationError, DomainError)
    assert issubclass(OwnershipError, AuthorizationError)


def test_domain_error_message() -> None:
    err = EntityNotFoundError("Usuário não encontrado.")
    assert str(err) == "Usuário não encontrado."


def test_ownership_error_is_authorization() -> None:
    err = OwnershipError("Recurso pertence a outro cliente.")
    assert isinstance(err, AuthorizationError)
    assert isinstance(err, DomainError)
