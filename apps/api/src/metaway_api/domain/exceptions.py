class DomainError(Exception):
    """Erro base do domínio."""


class EntityNotFoundError(DomainError):
    """Entidade não encontrada."""


class DuplicateEntityError(DomainError):
    """Entidade duplicada (violação de unicidade)."""


class AuthenticationError(DomainError):
    """Falha de autenticação (credenciais inválidas)."""


class AuthorizationError(DomainError):
    """Falha de autorização (permissão insuficiente)."""


class OwnershipError(AuthorizationError):
    """Violação de ownership (recurso pertence a outro cliente)."""
