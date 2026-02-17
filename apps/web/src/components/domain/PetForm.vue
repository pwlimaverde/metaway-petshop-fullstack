<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

interface SelectOption {
  label: string
  value: number
}

interface PetFormValue {
  client_id: number | null
  breed_id: number | null
  name: string
  birth_date: string
}

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<PetFormValue>
    clients?: SelectOption[]
    breeds: SelectOption[]
    loading?: boolean
    submitLabel?: string
    hideClient?: boolean
  }>(),
  {
    modelValue: () => ({}),
    clients: () => [],
    loading: false,
    submitLabel: 'Salvar',
    hideClient: false,
  },
)

const emit = defineEmits<{
  submit: [payload: PetFormValue]
  cancel: []
}>()

const form = reactive<PetFormValue>({
  client_id: null,
  breed_id: null,
  name: '',
  birth_date: '',
})

const errors = ref<Record<string, string>>({})

watch(
  () => props.modelValue,
  (value) => {
    form.client_id = value.client_id ?? null
    form.breed_id = value.breed_id ?? null
    form.name = value.name ?? ''
    form.birth_date = value.birth_date ?? ''
    errors.value = {}
  },
  { immediate: true, deep: true },
)

function validate(): boolean {
  const e: Record<string, string> = {}
  if (!props.hideClient && form.client_id == null) e.client_id = 'Selecione um cliente.'
  if (form.breed_id == null) e.breed_id = 'Selecione uma raça.'
  if (!form.name.trim()) e.name = 'Nome é obrigatório.'
  if (!form.birth_date) e.birth_date = 'Data de nascimento é obrigatória.'
  errors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  if (!validate()) return
  emit('submit', {
    client_id: form.client_id,
    breed_id: form.breed_id,
    name: form.name.trim(),
    birth_date: form.birth_date,
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup v-if="!hideClient" label="Cliente" required :error="errors.client_id">
        <Select v-model="form.client_id" :options="clients" placeholder="Selecione um cliente" />
      </FormGroup>
      <FormGroup label="Raça" required :error="errors.breed_id">
        <Select v-model="form.breed_id" :options="breeds" placeholder="Selecione uma raça" />
      </FormGroup>
    </div>

    <div class="grid gap-4 sm:grid-cols-2">
      <FormGroup label="Nome" required :error="errors.name">
        <Input v-model="form.name" />
      </FormGroup>
      <FormGroup label="Nascimento" required :error="errors.birth_date">
        <Input v-model="form.birth_date" type="date" />
      </FormGroup>
    </div>

    <div class="flex justify-end gap-2">
      <Button variant="secondary" @click="emit('cancel')">Cancelar</Button>
      <Button type="submit" :loading="loading">{{ submitLabel }}</Button>
    </div>
  </form>
</template>
