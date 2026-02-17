# Metaway Petshop Web

Frontend Vue 3 + TypeScript do sistema Metaway Petshop.

> Versionamento do monorepo: fonte única em `VERSION` (raiz).
> Para sincronizar este frontend com a versão global: `make sync-version`.

## Stack

- Vue 3 (Composition API)
- TypeScript
- Pinia
- Vue Router
- TailwindCSS
- Axios
- Vitest + Vue Test Utils

## Scripts

```bash
npm install
npm run dev
npm run lint
npm run format
npm run test
npm run build
```

## Configuração

A API padrão é `/api/v1` (via gateway Nginx). Para ambiente local customizado:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1 npm run dev
```

## Estrutura principal

```text
src/
  assets/
  components/
    ui/
    shared/
    domain/
  composables/
  layouts/
  lib/
  router/
  stores/
  types/
  views/
    admin/
    client/
```

## Regras de navegação

- Login em `/login` com CPF + senha.
- Guard de autenticação para rotas protegidas.
- Guard por role para rotas admin.
- Cliente não acessa rotas de administração.

## Testes implementados

- `tests/stores/auth.store.spec.ts`
- `tests/router/router.guards.spec.ts`
- `tests/components/ui/Button.spec.ts`
- `tests/components/ui/Badge.spec.ts`
- `tests/components/ui/Card.spec.ts`
- `tests/components/ui/Input.spec.ts`
- `tests/components/domain/AppointmentForm.spec.ts`

## Build de produção

```bash
npm run build
```

O build gerado é servido pelo container `web` atrás do Nginx em `http://localhost/`.
