# Diagrama de Dados (Mermaid) — Estrutura Atual

```mermaid
erDiagram
    USERS {
        uuid id PK
        string cpf
        string role
        string password_hash
        uuid client_id FK
        string name
        datetime created_at
        datetime updated_at
    }

    CLIENTS {
        uuid id PK
        string name
        string photo_url
        datetime created_at
        datetime updated_at
    }

    ADDRESSES {
        uuid id PK
        uuid client_id FK
        string logradouro
        string numero
        string complemento
        string bairro
        string cidade
        string estado
        string cep
        string tag
        datetime created_at
        datetime updated_at
    }

    CONTACTS {
        uuid id PK
        uuid client_id FK
        string tag
        string tipo
        string valor
        datetime created_at
        datetime updated_at
    }

    BREEDS {
        uuid id PK
        string descricao
        datetime created_at
        datetime updated_at
    }

    PETS {
        uuid id PK
        uuid client_id FK
        uuid breed_id FK
        string name
        date birth_date
        string photo_url
        datetime created_at
        datetime updated_at
    }

    APPOINTMENTS {
        uuid id PK
        uuid pet_id FK
        string descricao
        decimal valor
        datetime data
        string status
        datetime created_at
        datetime updated_at
    }

    CLIENTS ||--o| USERS : "vinculo de login (0..1 por client)"
    CLIENTS ||--o{ ADDRESSES : possui
    CLIENTS ||--o{ CONTACTS : possui
    CLIENTS ||--o{ PETS : possui
    BREEDS  ||--o{ PETS : classifica
    PETS    ||--o{ APPOINTMENTS : recebe
```

## Regras de Integridade (complementares ao diagrama)
- `users.cpf`: `UNIQUE` e `NOT NULL`.
- `users.client_id`: `UNIQUE`, obrigatório para `CLIENTE`, nulo para `ADMIN`.
- `users.name`: obrigatório para `ADMIN`, nulo para `CLIENTE`.
- `breeds.descricao`: `UNIQUE`.
- `appointments.status`: enum com default `AGENDADO`.
