<script setup lang="ts">
import { computed, useSlots } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const inputVariants = cva(
  'w-full rounded-xl border bg-white text-sm text-neutral-900 shadow-sm outline-none transition-all duration-200 placeholder:text-neutral-400 disabled:pointer-events-none disabled:opacity-50',
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

type InputVariants = VariantProps<typeof inputVariants>

const props = withDefaults(
  defineProps<{
    modelValue?: string | number
    type?: string
    placeholder?: string
    disabled?: boolean
    error?: string
    size?: InputVariants['size']
    class?: string
    autocomplete?: string
    name?: string
  }>(),
  {
    modelValue: '',
    type: 'text',
    placeholder: '',
    disabled: false,
    error: '',
    size: 'md',
    class: '',
    autocomplete: 'off',
    name: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const slots = useSlots()

const inputClass = computed(() =>
  cn(
    inputVariants({ size: props.size, state: props.error ? 'error' : 'default' }),
    slots.icon ? 'pl-11' : '',
    props.class,
  ),
)

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="relative">
    <span v-if="$slots.icon" class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-400">
      <slot name="icon" />
    </span>
    <input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClass"
      :autocomplete="autocomplete"
      :name="name"
      @input="onInput"
    />
  </div>
</template>
