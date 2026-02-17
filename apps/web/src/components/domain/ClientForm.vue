<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import { formatCpf, isValidCpf } from '@/lib/format'

interface ClientFormValue {
  cpf: string
  name: string
}

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<ClientFormValue>
    loading?: boolean
    submitLabel?: string
    hideCpf?: boolean
  }>(),
  {
    modelValue: () => ({}),
    loading: false,
    submitLabel: 'Salvar',
    hideCpf: false,
  },
)

const emit = defineEmits<{
  submit: [payload: ClientFormValue]
  cancel: []
}>()

const form = reactive<ClientFormValue>({
  cpf: '',
  name: '',
})

const errors = ref<Record<string, string>>({})

watch(
  () => props.modelValue,
  (value) => {
    form.cpf = value.cpf ?? ''
    form.name = value.name ?? ''
    errors.value = {}
  },
  { immediate: true, deep: true },
)

function validate(): boolean {
  const e: Record<string, string> = {}
  if (!props.hideCpf) {
    const cpfDigits = form.cpf.replace(/\D/g, '')
    if (!cpfDigits) {
      e.cpf = 'CPF é obrigatório.'
    } else if (!isValidCpf(cpfDigits)) {
      e.cpf = 'CPF inválido.'
    }
  }
  if (!form.name.trim()) e.name = 'Nome é obrigatório.'
  errors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  if (!validate()) return
  emit('submit', {
    cpf: form.cpf.replace(/\D/g, ''),
    name: form.name.trim(),
  })
}

function onCpfInput(value: string) {
  form.cpf = formatCpf(value)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <FormGroup v-if="!hideCpf" label="CPF" required :error="errors.cpf">
      <Input :model-value="form.cpf" placeholder="000.000.000-00" @update:model-value="onCpfInput" />
    </FormGroup>

    <FormGroup label="Nome" required :error="errors.name">
      <Input v-model="form.name" placeholder="Nome completo" />
    </FormGroup>

    <div class="flex justify-end gap-2">
      <Button variant="secondary" @click="emit('cancel')">Cancelar</Button>
      <Button type="submit" :loading="loading">{{ submitLabel }}</Button>
    </div>
  </form>
</template>
