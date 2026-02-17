<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import Textarea from '@/components/ui/Textarea.vue'
import { toLocalDateTime } from '@/lib/format'

interface SelectOption {
  label: string
  value: number
}

interface PetSelectOption extends SelectOption {
  client_id: number
}

interface AppointmentFormValue {
  pet_id: number | null
  descricao: string
  valor: number
  data: string
  status: string
}

interface AppointmentFormState extends AppointmentFormValue {
  client_id: number | null
}

const statusOptions = [
  { label: 'Agendado', value: 'AGENDADO' },
  { label: 'Em Andamento', value: 'EM_ANDAMENTO' },
  { label: 'Concluído', value: 'CONCLUIDO' },
  { label: 'Cancelado', value: 'CANCELADO' },
]

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<AppointmentFormValue>
    clients?: SelectOption[]
    pets: PetSelectOption[]
    loading?: boolean
    submitLabel?: string
  }>(),
  {
    modelValue: () => ({}),
    clients: () => [],
    loading: false,
    submitLabel: 'Salvar',
  },
)

const emit = defineEmits<{
  submit: [payload: AppointmentFormValue]
  cancel: []
}>()

const form = reactive<AppointmentFormState>({
  client_id: null,
  pet_id: null,
  descricao: '',
  valor: 0,
  data: '',
  status: 'AGENDADO',
})

const errors = ref<Record<string, string>>({})

const filteredPets = computed(() => {
  if (form.client_id == null) {
    return []
  }

  return props.pets.filter((pet) => pet.client_id === form.client_id)
})

watch(
  () => props.modelValue,
  (value) => {
    form.pet_id = value.pet_id ?? null
    const selectedPet = props.pets.find((pet) => pet.value === form.pet_id)
    form.client_id = selectedPet?.client_id ?? null
    form.descricao = value.descricao ?? ''
    form.valor = value.valor ?? 0
    form.data = value.data ? toLocalDateTime(value.data) : ''
    form.status = value.status ?? 'AGENDADO'
    errors.value = {}
  },
  { immediate: true, deep: true },
)

watch(
  () => form.client_id,
  (clientId) => {
    if (form.pet_id == null) {
      return
    }

    const hasSelectedPetForClient = props.pets.some((pet) => pet.value === form.pet_id && pet.client_id === clientId)
    if (!hasSelectedPetForClient) {
      form.pet_id = null
    }
  },
)

function validate(): boolean {
  const e: Record<string, string> = {}
  if (form.client_id == null) e.client_id = 'Selecione um cliente.'
  if (form.pet_id == null) e.pet_id = 'Selecione um pet.'
  if (!form.descricao.trim()) e.descricao = 'Descrição é obrigatória.'
  if (Number(form.valor) <= 0) e.valor = 'Valor deve ser maior que zero.'
  if (!form.data) e.data = 'Data é obrigatória.'
  errors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  if (!validate()) return
  emit('submit', {
    pet_id: form.pet_id,
    descricao: form.descricao.trim(),
    valor: Number(form.valor),
    data: form.data,
    status: form.status,
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup label="Cliente" required :error="errors.client_id">
        <Select v-model="form.client_id" :options="clients" placeholder="Selecione um cliente" />
      </FormGroup>

      <FormGroup label="Pet" required :error="errors.pet_id">
        <Select
          v-model="form.pet_id"
          :options="filteredPets"
          :disabled="form.client_id == null"
          placeholder="Selecione um pet"
        />
      </FormGroup>
    </div>

    <FormGroup label="Descrição" required :error="errors.descricao">
      <Textarea v-model="form.descricao" :rows="3" />
    </FormGroup>

    <div class="grid gap-4 sm:grid-cols-3">
      <FormGroup label="Valor (R$)" required :error="errors.valor">
        <Input v-model="form.valor" type="number" />
      </FormGroup>
      <FormGroup label="Data" required :error="errors.data">
        <Input v-model="form.data" type="datetime-local" />
      </FormGroup>
      <FormGroup label="Status">
        <Select v-model="form.status" :options="statusOptions" />
      </FormGroup>
    </div>

    <div class="flex justify-end gap-2">
      <Button variant="secondary" @click="emit('cancel')">Cancelar</Button>
      <Button type="submit" :loading="loading">{{ submitLabel }}</Button>
    </div>
  </form>
</template>
