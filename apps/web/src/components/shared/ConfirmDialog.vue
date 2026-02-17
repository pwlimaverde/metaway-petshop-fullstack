<script setup lang="ts">
import Modal from '@/components/shared/Modal.vue'
import Button from '@/components/ui/Button.vue'

withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    description?: string
    loading?: boolean
  }>(),
  {
    title: 'Confirmação',
    description: 'Deseja realmente continuar?',
    loading: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()
</script>

<template>
  <Modal :model-value="modelValue" :title="title" :description="description" @update:model-value="(value) => emit('update:modelValue', value)">
    <template #footer>
      <div class="flex justify-end gap-2">
        <Button variant="secondary" @click="emit('update:modelValue', false)">Cancelar</Button>
        <Button variant="danger" :loading="loading" @click="emit('confirm')">Confirmar</Button>
      </div>
    </template>
  </Modal>
</template>
