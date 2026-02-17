<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const textareaVariants = cva(
  'w-full resize-y rounded-xl border bg-white text-sm text-neutral-900 shadow-sm outline-none transition-all duration-200 placeholder:text-neutral-400 disabled:pointer-events-none disabled:opacity-50',
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

type TextareaVariants = VariantProps<typeof textareaVariants>

const props = withDefaults(
  defineProps<{
    modelValue?: string
    rows?: number
    placeholder?: string
    disabled?: boolean
    error?: string
    size?: TextareaVariants['size']
    class?: string
    name?: string
    maxlength?: number
  }>(),
  {
    modelValue: '',
    rows: 4,
    placeholder: '',
    disabled: false,
    error: '',
    size: 'md',
    class: '',
    name: '',
    maxlength: undefined,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const textareaClass = computed(() =>
  cn(
    textareaVariants({ size: props.size, state: props.error ? 'error' : 'default' }),
    props.class,
  ),
)

function onInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <textarea
    :value="modelValue"
    :rows="rows"
    :placeholder="placeholder"
    :disabled="disabled"
    :name="name || undefined"
    :maxlength="maxlength"
    :class="textareaClass"
    @input="onInput"
  />
</template>
