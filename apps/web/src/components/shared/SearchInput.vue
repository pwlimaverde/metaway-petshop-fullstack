<script setup lang="ts">
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Icon from '@/components/ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    placeholder?: string
  }>(),
  {
    placeholder: 'Buscar...',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function clear() {
  emit('update:modelValue', '')
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.modelValue) {
    clear()
  }
}
</script>

<template>
  <div class="flex items-center gap-2">
    <Input
      :model-value="props.modelValue"
      :placeholder="placeholder"
      class="max-w-sm"
      @update:model-value="(value: string) => emit('update:modelValue', value)"
      @keydown="onKeydown"
    >
      <template #icon>
        <Icon name="Search" :size="16" />
      </template>
    </Input>
    <Button v-if="props.modelValue" variant="ghost" size="sm" aria-label="Limpar busca" @click="clear">Limpar</Button>
  </div>
</template>
