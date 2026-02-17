<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const cardVariants = cva(
  'rounded-2xl border bg-white transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'border-neutral-100 shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)] hover:shadow-[0_4px_16px_-4px_rgba(0,0,0,0.1)] hover:border-neutral-200',
        flat: 'border-neutral-200 shadow-none',
        elevated: 'border-neutral-100 shadow-lg',
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'md',
    },
  },
)

type CardVariants = VariantProps<typeof cardVariants>

const props = withDefaults(
  defineProps<{
    variant?: CardVariants['variant']
    padding?: CardVariants['padding']
    class?: string
  }>(),
  {
    variant: 'default',
    padding: 'md',
    class: '',
  },
)

const classes = computed(() => cn(cardVariants({ variant: props.variant, padding: props.padding }), props.class))
</script>

<template>
  <div :class="classes">
    <slot />
  </div>
</template>
