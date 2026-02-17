# Relatório de Melhorias na Modelagem de Dados

## Contexto
Durante o desenvolvimento do backend, a modelagem inicial recebida apresentava alguns pontos de ambiguidade e risco de inconsistência. Com autorização para resolver inconsistências, a estrutura foi ajustada e documentada.

## Melhorias Aplicadas
1. CPF como fonte única de identidade de login
- Antes: CPF em `Usuario` e possibilidade de também existir em `Cliente`.
- Agora: CPF somente em `users.cpf` (`UNIQUE` e `NOT NULL`).
- Ganho: elimina duplicidade de identidade e risco de divergência de CPF entre tabelas.

2. Vínculo explícito entre usuário e cliente
- Antes: vínculo implícito, sem regra relacional forte.
- Agora: `users.client_id` como FK para `clients.id`, com `UNIQUE`.
- Ganho: garante integridade referencial e no máximo um login por cliente.

3. Regras de consistência por perfil
- Agora:
  - `role = CLIENTE` exige `client_id` preenchido.
  - `role = ADMIN` exige `client_id = NULL`.
  - `role = CLIENTE` exige `users.name = NULL`.
  - `role = ADMIN` exige `users.name` preenchido.
- Ganho: evita estados inválidos no banco e simplifica validações de negócio.

4. Separação clara entre autenticação e cadastro
- Antes: risco de duplicar dados pessoais entre `Usuario` e `Cliente`.
- Agora: autenticação em `users`; dados cadastrais em `clients`.
- Ganho: menor acoplamento, menos anomalias de atualização e manutenção mais simples.

5. Cadeia de ownership formalizada por FKs
- Agora: ownership derivado de `user -> client -> pet -> appointment`.
- Ganho: reforça controle de acesso com base em integridade relacional e reduz chance de acesso indevido.

6. Restrições de domínio e padronização semântica
- Agora:
  - `contact.tipo` com enum (`EMAIL`, `TELEFONE`).
  - `appointment.status` com enum e default `AGENDADO`.
  - `breed.descricao` com `UNIQUE`.
- Ganho: reduz valores inválidos e duplicidade lógica.

7. Auditoria padronizada em todas as entidades
- Agora: todas as tabelas principais com `created_at` e `updated_at`.
- Ganho: rastreabilidade e governança de mudanças.

## Resultado
A modelagem evoluiu para um modelo relacional mais consistente, com regras explícitas de integridade (`PK`, `FK`, `UNIQUE`, `NOT NULL`, `ENUM` e regras por perfil). Isso reduz inconsistências de dados, melhora manutenção e sustenta corretamente as regras de negócio do sistema.

## Referência
- `docs/PRD.md` (Seção 8 — Modelo de Dados)
- `docs/PRD.md` (Seção 20 — Riscos e Decisões)
