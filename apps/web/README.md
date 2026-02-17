# Metaway Petshop Web

Frontend Vue 3 + TypeScript do sistema Metaway Petshop.

## Stack

- Vue 3 (Composition API)
- Vue Router
- Pinia
- TailwindCSS + CVA
- Vitest + Vue Test Utils

## Scripts

```bash
npm install
npm run dev
npm run lint
npm run test
npm run build
```

## Estrutura

```text
src/
  assets/              # estilos globais
  components/
    ui/                # átomos do design system
    shared/            # moléculas/organismos reutilizáveis
    domain/            # formulários e cards de domínio
  composables/         # acesso à API por entidade
  layouts/             # AuthLayout e DefaultLayout
  lib/                 # axios, formatações e utilitários JWT
  router/              # rotas + guards
  stores/              # auth e toast
  types/               # contratos TypeScript
  views/
    admin/             # telas administrativas (CRUD)
    client/            # telas do perfil cliente (read + update)
```

## Design System

- Tokens no `tailwind.config.ts`:
  - `primary`, `secondary`, `neutral`, `success`, `error`, `warning`, `info`
  - radius `lg` (8px), `xl` (12px)
  - shadows `sm`, `lg`
- Componentes base em `src/components/ui`.
- Variantes com `class-variance-authority` (`Button`, `Badge`).

## Regras de navegação

- Login em `/login` com CPF + senha.
- Guard de autenticação para rotas protegidas.
- Guard de perfil para rotas admin.
- Em rotas de cliente, UI sem ações de criar/excluir.

## Testes implementados

- `tests/stores/auth.store.spec.ts`: login, falha, persistência e logout.
- `tests/router/router.guards.spec.ts`: proteção por auth e role.
- `tests/components/ui/Button.spec.ts`: render de variante padrão.
