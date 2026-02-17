<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

interface ContactFormValue {
  tag: string
  tipo: 'EMAIL' | 'TELEFONE'
  valor: string
}

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<ContactFormValue>
    loading?: boolean
    submitLabel?: string
  }>(),
  {
    modelValue: () => ({}),
    loading: false,
    submitLabel: 'Salvar',
  },
)

const emit = defineEmits<{
  submit: [payload: ContactFormValue]
  cancel: []
}>()

const contactTypeOptions = [
  { label: 'Email', value: 'EMAIL' },
  { label: 'Telefone', value: 'TELEFONE' },
]

const form = reactive<ContactFormValue>({
  tag: '',
  tipo: 'EMAIL',
  valor: '',
})

const errors = ref<Record<string, string>>({})

watch(
  () => props.modelValue,
  (value) => {
    form.tag = value.tag ?? ''
    form.tipo = value.tipo ?? 'EMAIL'
    form.valor = value.valor ?? ''
    errors.value = {}
  },
  { immediate: true, deep: true },
)

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PHONE_RE = /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/

function validate(): boolean {
  const e: Record<string, string> = {}
  if (!form.tag.trim()) e.tag = 'Tag é obrigatória.'
  if (!form.valor.trim()) {
    e.valor = 'Valor é obrigatório.'
  } else if (form.tipo === 'EMAIL' && !EMAIL_RE.test(form.valor.trim())) {
    e.valor = 'Email inválido.'
  } else if (form.tipo === 'TELEFONE' && !PHONE_RE.test(form.valor.trim())) {
    e.valor = 'Telefone inválido. Ex: (11) 99999-9999'
  }
  errors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  if (!validate()) return
  emit('submit', {
    tag: form.tag.trim(),
    tipo: form.tipo,
    valor: form.valor.trim(),
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup label="Tag" required :error="errors.tag">
        <Input v-model="form.tag" placeholder="Pessoal, Comercial..." />
      </FormGroup>
      <FormGroup label="Tipo" required>
        <Select v-model="form.tipo" :options="contactTypeOptions" />
      </FormGroup>
    </div>

    <FormGroup label="Valor" required :error="errors.valor">
      <Input v-model="form.valor" :placeholder="form.tipo === 'EMAIL' ? 'email@dominio.com' : '(11) 99999-9999'" />
    </FormGroup>

    <div class="flex justify-end gap-2">
      <Button variant="secondary" @click="emit('cancel')">Cancelar</Button>
      <Button type="submit" :loading="loading">{{ submitLabel }}</Button>
    </div>
  </form>
</template>
