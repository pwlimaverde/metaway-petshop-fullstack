<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

interface AddressFormValue {
  logradouro: string
  numero: string
  complemento: string
  bairro: string
  cidade: string
  estado: string
  cep: string
  tag: string
}

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<AddressFormValue>
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
  submit: [payload: AddressFormValue]
  cancel: []
}>()

const form = reactive<AddressFormValue>({
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  cep: '',
  tag: '',
})

const errors = ref<Record<string, string>>({})

watch(
  () => props.modelValue,
  (value) => {
    form.logradouro = value.logradouro ?? ''
    form.numero = value.numero ?? ''
    form.complemento = value.complemento ?? ''
    form.bairro = value.bairro ?? ''
    form.cidade = value.cidade ?? ''
    form.estado = value.estado ?? ''
    form.cep = value.cep ?? ''
    form.tag = value.tag ?? ''
    errors.value = {}
  },
  { immediate: true, deep: true },
)

function validate(): boolean {
  const e: Record<string, string> = {}
  if (!form.logradouro.trim()) e.logradouro = 'Logradouro é obrigatório.'
  if (!form.numero.trim()) e.numero = 'Número é obrigatório.'
  if (!form.bairro.trim()) e.bairro = 'Bairro é obrigatório.'
  if (!form.cidade.trim()) e.cidade = 'Cidade é obrigatória.'
  if (!form.estado.trim() || form.estado.trim().length !== 2) e.estado = 'UF deve ter 2 caracteres.'
  if (!form.cep.trim()) e.cep = 'CEP é obrigatório.'
  if (!form.tag.trim()) e.tag = 'Tag é obrigatória.'
  errors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  if (!validate()) return
  emit('submit', {
    logradouro: form.logradouro.trim(),
    numero: form.numero.trim(),
    complemento: form.complemento.trim(),
    bairro: form.bairro.trim(),
    cidade: form.cidade.trim(),
    estado: form.estado.trim().toUpperCase(),
    cep: form.cep.trim(),
    tag: form.tag.trim(),
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <div class="grid gap-4 sm:grid-cols-3">
      <FormGroup label="Logradouro" required :error="errors.logradouro" class="sm:col-span-2">
        <Input v-model="form.logradouro" />
      </FormGroup>
      <FormGroup label="Número" required :error="errors.numero">
        <Input v-model="form.numero" />
      </FormGroup>
    </div>

    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup label="Complemento">
        <Input v-model="form.complemento" />
      </FormGroup>
      <FormGroup label="Bairro" required :error="errors.bairro">
        <Input v-model="form.bairro" />
      </FormGroup>
    </div>

    <div class="grid gap-4 sm:grid-cols-3">
      <FormGroup label="Cidade" required :error="errors.cidade">
        <Input v-model="form.cidade" />
      </FormGroup>
      <FormGroup label="UF" required :error="errors.estado">
        <Input v-model="form.estado" maxlength="2" placeholder="SP" />
      </FormGroup>
      <FormGroup label="CEP" required :error="errors.cep">
        <Input v-model="form.cep" placeholder="01001000" />
      </FormGroup>
    </div>

    <FormGroup label="Tag" required :error="errors.tag">
      <Input v-model="form.tag" placeholder="Casa, Trabalho..." />
    </FormGroup>

    <div class="flex justify-end gap-2">
      <Button variant="secondary" @click="emit('cancel')">Cancelar</Button>
      <Button type="submit" :loading="loading">{{ submitLabel }}</Button>
    </div>
  </form>
</template>
