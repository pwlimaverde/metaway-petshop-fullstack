<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva('inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold tracking-wide transition-colors focus:outline-none focus:ring-2 focus:ring-neutral-950 focus:ring-offset-2', {
  variants: {
    variant: {
      outline: 'border-neutral-200 text-neutral-900 bg-white',
      solid: 'border-transparent bg-primary-600 text-white shadow hover:bg-primary-700',
      subtle: 'border-transparent bg-primary-50 text-primary-700 ring-1 ring-inset ring-primary-700/10',
      success: 'border-transparent bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-600/20',
      warning: 'border-transparent bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-600/20',
      error: 'border-transparent bg-rose-50 text-rose-700 ring-1 ring-inset ring-rose-600/20',
      info: 'border-transparent bg-sky-50 text-sky-700 ring-1 ring-inset ring-sky-700/20',
    },
  },
  defaultVariants: {
    variant: 'subtle',
  },
})

type BadgeVariants = VariantProps<typeof badgeVariants>

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariants['variant']
    class?: string
  }>(),
  {
    variant: 'subtle',
    class: '',
  },
)

const classes = computed(() => cn(badgeVariants({ variant: props.variant }), props.class))
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
