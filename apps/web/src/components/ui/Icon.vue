<script setup lang="ts">
import { computed } from 'vue'
import * as icons from 'lucide-vue-next'

import { cn } from '@/lib/utils'

const iconRegistry = icons as Record<string, unknown>

const props = withDefaults(
  defineProps<{
    name?: string
    size?: number
    strokeWidth?: number
    class?: string
  }>(),
  {
    name: 'Circle',
    size: 18,
    strokeWidth: 2,
    class: '',
  },
)

const iconComponent = computed(() => (iconRegistry[props.name] ?? iconRegistry.Circle) as object)
</script>

<template>
  <component :is="iconComponent" :size="size" :stroke-width="strokeWidth" :class="cn('shrink-0', props.class)" />
</template>
