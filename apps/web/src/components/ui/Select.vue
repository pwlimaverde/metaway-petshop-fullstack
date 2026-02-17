<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

interface SelectOption {
  label: string
  value: string | number
}

const selectVariants = cva(
  'w-full rounded-xl border bg-white text-sm text-neutral-900 shadow-sm outline-none transition-all duration-200 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      size: {
        sm: 'px-3 py-2 text-xs',
        md: 'px-4 py-3 text-sm',
        lg: 'px-5 py-4 text-base',
      },
      state: {
        default: 'border-neutral-200 hover:border-neutral-300 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10',
        error: 'border-error ring-2 ring-error/20 focus:border-error focus:ring-error/40',
      },
    },
    defaultVariants: {
      size: 'md',
      state: 'default',
    },
  },
)

type SelectVariantProps = VariantProps<typeof selectVariants>

const props = withDefaults(
  defineProps<{
    modelValue?: string | number | null
    options: SelectOption[]
    placeholder?: string
    disabled?: boolean
    error?: string
    size?: SelectVariantProps['size']
    class?: string
    name?: string
  }>(),
  {
    modelValue: '',
    placeholder: 'Selecione',
    disabled: false,
    error: '',
    size: 'md',
    class: '',
    name: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const selectClass = computed(() =>
  cn(
    selectVariants({ size: props.size, state: props.error ? 'error' : 'default' }),
    props.class,
  ),
)

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const selectedOption = props.options.find((option) => String(option.value) === target.value)
  emit('update:modelValue', selectedOption ? selectedOption.value : target.value)
}
</script>

<template>
  <select :value="modelValue" :disabled="disabled" :class="selectClass" :name="name" @change="onChange">
    <option value="" disabled>{{ placeholder }}</option>
    <option v-for="option in options" :key="option.value" :value="option.value">
      {{ option.label }}
    </option>
  </select>
</template>
