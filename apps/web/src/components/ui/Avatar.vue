<script setup lang="ts">
import { computed } from 'vue'

import Icon from '@/components/ui/Icon.vue'
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{
    src?: string | null
    alt?: string
    name?: string
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    src: null,
    alt: 'Avatar',
    name: '',
    size: 'md',
  },
)

const sizeClass = computed(() => {
  if (props.size === 'sm') {
    return 'h-8 w-8 text-xs'
  }
  if (props.size === 'lg') {
    return 'h-14 w-14 text-lg'
  }
  return 'h-10 w-10 text-sm'
})

const iconSize = computed(() => {
  if (props.size === 'sm') return 14
  if (props.size === 'lg') return 24
  return 18
})

const initials = computed(() => {
  if (!props.name) return ''
  const parts = props.name.trim().split(/\s+/).slice(0, 2)
  return parts.map((value) => value[0]?.toUpperCase() ?? '').join('')
})

const API_BASE_URL = ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '/api/v1').replace(/\/$/, '')

const resolvedSrc = computed(() => {
  if (!props.src) return null
  if (/^(https?:|data:|blob:)/.test(props.src) || props.src.startsWith('/')) {
    return props.src
  }
  return `${API_BASE_URL}/files/${props.src}`
})
</script>

<template>
  <div
    :title="name || alt"
    :class="cn('inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary-100 font-semibold text-primary-700', sizeClass)"
  >
    <img v-if="resolvedSrc" :src="resolvedSrc" :alt="alt" class="h-full w-full object-cover" />
    <span v-else-if="initials">{{ initials }}</span>
    <Icon v-else name="User" :size="iconSize" />
  </div>
</template>
