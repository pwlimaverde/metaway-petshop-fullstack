<script setup lang="ts">
import { computed } from 'vue'

import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

function variantClasses(variant: string): string {
  if (variant === 'success') {
    return 'border-success/30 bg-emerald-50 text-emerald-900'
  }
  if (variant === 'error') {
    return 'border-error/30 bg-rose-50 text-rose-900'
  }
  if (variant === 'warning') {
    return 'border-warning/30 bg-amber-50 text-amber-900'
  }
  return 'border-info/30 bg-sky-50 text-sky-900'
}

const items = computed(() => toastStore.items)
</script>

<template>
  <Teleport to="body">
    <TransitionGroup
      name="toast"
      tag="div"
      aria-live="polite"
      role="status"
      class="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2"
    >
      <div
        v-for="item in items"
        :key="item.id"
        class="pointer-events-auto rounded-lg border px-4 py-3 shadow-lg"
        :class="variantClasses(item.variant)"
        @mouseenter="toastStore.pause(item.id)"
        @mouseleave="toastStore.resume(item.id)"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-sm font-semibold">{{ item.title }}</p>
            <p v-if="item.description" class="mt-1 text-xs opacity-90">{{ item.description }}</p>
          </div>
          <button aria-label="Fechar notificação" class="text-xs font-semibold opacity-70 hover:opacity-100" @click="toastStore.remove(item.id)">X</button>
        </div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
