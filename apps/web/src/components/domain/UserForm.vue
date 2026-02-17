<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import { formatCpf, isValidCpf } from '@/lib/format'
import { MIN_PASSWORD_DIGITS, MIN_PASSWORD_LENGTH } from '@/lib/password'

interface SelectOption {
  label: string
  value: number
  cpf?: string | null
}

interface UserFormValue {
  cpf: string
  name: string
  role: 'ADMIN' | 'CLIENTE'
  password: string
  client_id: number | null
}

interface UserFormSubmit {
  cpf: string
  name: string
  role: 'ADMIN' | 'CLIENTE'
  password: string
  client_id: number | null
}

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<UserFormValue>
    clients?: SelectOption[]
    loading?: boolean
    submitLabel?: string
    editing?: boolean
  }>(),
  {
    modelValue: () => ({}),
    clients: () => [],
    loading: false,
    submitLabel: 'Salvar',
    editing: false,
  },
)

const emit = defineEmits<{
  submit: [payload: UserFormSubmit]
  cancel: []
}>()

const roleOptions = [
  { label: 'Administrador', value: 'ADMIN' },
  { label: 'Cliente', value: 'CLIENTE' },
]

const form = reactive<UserFormValue>({
  cpf: '',
  name: '',
  role: 'CLIENTE',
  password: '',
  client_id: null,
})

const errors = ref<Record<string, string>>({})

const selectedClientCpf = computed(() => {
  if (form.client_id == null) {
    return null
  }
  return props.clients.find((client) => client.value === form.client_id)?.cpf ?? null
})

watch(
  () => props.modelValue,
  (value) => {
    form.cpf = value.cpf ?? ''
    form.name = value.name ?? ''
    form.role = value.role ?? 'CLIENTE'
    form.password = ''
    form.client_id = value.client_id ?? null
    errors.value = {}
  },
  { immediate: true, deep: true },
)

watch(
  () => form.role,
  (nextRole) => {
    if (nextRole === 'ADMIN') {
      form.client_id = null
    }
  },
)

function validate(): boolean {
  const e: Record<string, string> = {}
  if (!form.name.trim()) e.name = 'Nome é obrigatório.'
  const cpfDigits = form.cpf.replace(/\D/g, '')
  if (!cpfDigits) {
    e.cpf = 'CPF é obrigatório.'
  } else if (!isValidCpf(cpfDigits)) {
    e.cpf = 'CPF inválido.'
  }
  if (!props.editing && !form.password) {
    e.password = 'Senha é obrigatória.'
  } else if (form.password && form.password.length < MIN_PASSWORD_LENGTH) {
    e.password = `Senha deve ter no mínimo ${MIN_PASSWORD_LENGTH} caracteres.`
  } else if (form.password) {
    const digitsCount = (form.password.match(/\d/g) ?? []).length
    if (digitsCount < MIN_PASSWORD_DIGITS) {
      e.password = `Senha deve conter pelo menos ${MIN_PASSWORD_DIGITS} dígitos.`
    }
  }
  if (form.role === 'CLIENTE' && form.client_id == null) {
    e.client_id = 'Selecione um cliente.'
  }
  errors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  if (!validate()) return
  emit('submit', {
    cpf: form.cpf.replace(/\D/g, ''),
    name: form.name.trim(),
    role: form.role,
    password: form.password,
    client_id: form.role === 'CLIENTE' ? form.client_id : null,
  })
}

function onCpfInput(value: string) {
  form.cpf = formatCpf(value)
}

function applySelectedClientCpf() {
  if (!selectedClientCpf.value) {
    return
  }
  form.cpf = formatCpf(selectedClientCpf.value)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup label="Nome" required :error="errors.name">
        <Input v-model="form.name" />
      </FormGroup>
      <FormGroup label="CPF" required :error="errors.cpf">
        <Input :model-value="form.cpf" placeholder="000.000.000-00" @update:model-value="onCpfInput" />
        <div v-if="form.role === 'CLIENTE' && selectedClientCpf" class="mt-2 flex justify-end">
          <Button type="button" variant="ghost" @click="applySelectedClientCpf">
            Usar CPF do cliente
          </Button>
        </div>
      </FormGroup>
    </div>

    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup label="Perfil" required>
        <Select v-model="form.role" :options="roleOptions" />
      </FormGroup>
      <FormGroup label="Cliente vinculado" :required="form.role === 'CLIENTE'" :error="errors.client_id">
        <Select v-model="form.client_id" :options="clients" :disabled="form.role !== 'CLIENTE'" placeholder="Selecione um cliente" />
      </FormGroup>
    </div>

    <FormGroup :label="editing ? 'Nova senha (opcional)' : 'Senha'" :required="!editing" :error="errors.password">
      <Input v-model="form.password" type="password" placeholder="******" />
    </FormGroup>

    <div class="flex justify-end gap-2">
      <Button variant="secondary" @click="emit('cancel')">Cancelar</Button>
      <Button type="submit" :loading="loading">{{ submitLabel }}</Button>
    </div>
  </form>
</template>
