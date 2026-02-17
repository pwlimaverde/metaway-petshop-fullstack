# Metaway UI — Design System Specifications
**Versão:** 2.0.0 | **Contexto:** Petshop Management System
**Stack:** Vue 3 + TailwindCSS + TypeScript

---

## 1. Fundamentos Visuais (Design Tokens)

Todos os tokens são definidos em `apps/web/tailwind.config.ts` como single source of truth.

### Paleta de Cores

| Token | Escala | Hex (referência) | Uso |
|-------|--------|-------------------|-----|
| **primary** | 50–900 | `#0d9488` (600) | Botões principais, links, navegação ativa |
| **secondary** | 50–900 | `#fb7185` (400) | Badges de pets, CTAs secundários |
| **neutral** | 50–900 | `#78716c` (500) | Surfaces, textos, bordas (tom quente Stone) |
| **success** | — | `#10b981` | Operações concluídas |
| **error** | — | `#ef4444` | Erros de validação, ações destrutivas |
| **warning** | — | `#f59e0b` | Alertas de sistema |
| **info** | — | `#3b82f6` | Status neutros |

### Tipografia

| Família | Classe Tailwind | Uso |
|---------|-----------------|-----|
| **Inter** | `font-sans` | Corpo de texto, labels, inputs |
| **Nunito** | `font-display` | Headings (H1, H2), títulos de página |

**Escala:** `text-xs`/`text-sm` (legendas), `text-base` (corpo), `text-lg`/`text-xl` (títulos de card), `text-2xl`/`text-3xl` (headings).

### Formas e Espaçamento

| Elemento | Radius | Classe |
|----------|--------|--------|
| Button, Input, Select, Textarea, Nav links | 16px | `rounded-xl` |
| Card, Modal, DataTable | 24px | `rounded-2xl` |
| Badge | 6px | `rounded-md` |

| Nível | Classe | Uso |
|-------|--------|-----|
| Sutil | `shadow-sm` | Inputs, cards em repouso |
| Padrão | `shadow-lg` | Modais, dropdowns |
| Destaque | `shadow-2xl` | Welcome card, hero sections |
| Com cor | `shadow-primary-600/20` | Botão primário |

**Espaçamento:** Múltiplos de 4 (Tailwind padrão). Layouts com respiro (`p-4` a `p-8`).

---

## 2. Biblioteca de Componentes

Todos os componentes atômicos (UI) usam **CVA** (Class Variance Authority) para definir variantes tipadas. Caminho: `src/components/ui/`.

### Átomos (`src/components/ui/`)

| Componente | CVA | Variantes | Props de variante |
|------------|-----|-----------|-------------------|
| **Button** | `variant` + `size` | `primary`, `secondary`, `ghost`, `danger` / `sm`, `md`, `lg` | `variant`, `size`, `loading`, `disabled` |
| **Input** | `size` + `state` | `sm`, `md`, `lg` / `default`, `error` | `size`, `error` (state derivado) |
| **Textarea** | `size` + `state` | `sm`, `md`, `lg` / `default`, `error` | `size`, `error` (state derivado) |
| **Select** | `size` + `state` | `sm`, `md`, `lg` / `default`, `error` | `size`, `error` (state derivado) |
| **Card** | `variant` + `padding` | `default`, `flat`, `elevated` / `none`, `sm`, `md`, `lg` | `variant`, `padding` |
| **Badge** | `variant` | `outline`, `solid`, `subtle`, `success`, `warning`, `error`, `info` | `variant` |
| **Avatar** | — | Tamanho via prop `size` (computed) | `src`, `name`, `size` |
| **Icon** | — | Wrapper dinâmico para `lucide-vue-next` | `name`, `size` |

**Padrão de implementação CVA:**
```typescript
// 1. Definir variantes com cva()
const buttonVariants = cva('classes-base...', { variants: { ... } })

// 2. Extrair tipos
type ButtonVariants = VariantProps<typeof buttonVariants>

// 3. Props tipadas
defineProps<{ variant?: ButtonVariants['variant'] }>()

// 4. Combinar com cn()
const classes = computed(() => cn(buttonVariants({ variant, size }), props.class))
```

### Moléculas (`src/components/shared/`)

| Componente | Descrição |
|------------|-----------|
| **FormGroup** | Label + Input/Select/Textarea + ErrorMessage |
| **SearchInput** | Input com ícone de lupa e botão limpar |
| **Toast** | Notificações flutuantes com auto-dismiss |
| **DropdownMenu** | Menu contextual para ações |
| **ConfirmDialog** | Modal de confirmação |

### Organismos (`src/components/shared/`)

| Componente | Descrição |
|------------|-----------|
| **DataTable** | Tabela responsiva, sort por coluna, paginação, coluna de ações |
| **Modal** | Overlay com blur, focus trap, escape key, header/body/footer |
| **Sidebar** | Navegação com ícones, estado ativo (`bg-primary-50`), perfil do usuário no footer, responsivo (drawer no mobile) |

### Componentes de Domínio (`src/components/domain/`)

| Componente | Entidade |
|------------|----------|
| **UserForm** | Criação/edição de usuário |
| **ClientForm** | Criação/edição de cliente |
| **PetForm** | Criação/edição de pet (com seleção de raça) |
| **PetCard** | Exibição de pet (usa Card, Badge, Avatar, Button) |
| **AddressForm** | Criação/edição de endereço |
| **ContactForm** | Criação/edição de contato |
| **AppointmentForm** | Criação/edição de atendimento (filtro cliente→pet) |

---

## 3. Implementação Técnica

### Dependências do Design System

| Pacote | Função |
|--------|--------|
| `class-variance-authority` | Variantes tipadas para componentes |
| `clsx` | Concatenação condicional de classes |
| `tailwind-merge` | Resolução de conflitos entre classes Tailwind |
| `lucide-vue-next` | Biblioteca de ícones SVG |
| `@headlessui/vue` | Componentes headless acessíveis |

### Utilitário `cn()`

Localização: `src/lib/utils.ts`

```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

Todos os componentes importam `cn()` para combinar classes base (CVA) com classes externas (via prop `class`).

### Padrão de Diretórios

```text
src/
├── assets/
│   └── main.css            # @config → tailwind.config.ts, fontes, resets
├── lib/
│   └── utils.ts            # cn() — clsx + twMerge
└── components/
    ├── ui/                  # Átomos (CVA) — Button, Input, Card, Badge...
    ├── shared/              # Moléculas/Organismos — DataTable, Modal, Sidebar...
    └── domain/              # Componentes de negócio — UserForm, PetCard...
```

### Fluxo de consumo

```
View → importa domain/ e shared/
  └── domain/ → importa ui/ (Button, Input, Card...)
      └── ui/ → usa cva() + cn() + tokens do tailwind.config.ts
```
