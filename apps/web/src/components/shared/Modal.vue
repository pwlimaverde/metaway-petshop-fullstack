<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, useId, watch } from 'vue'

import Icon from '@/components/ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title: string
    description?: string
  }>(),
  {
    description: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

const titleId = useId()
const dialogRef = ref<HTMLElement | null>(null)
let previouslyFocused: HTMLElement | null = null

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function onEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.modelValue) {
    close()
  }
}

function trapFocus(event: KeyboardEvent) {
  if (event.key !== 'Tab' || !dialogRef.value) return

  const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  )
  if (!focusable.length) return

  const first = focusable[0] as HTMLElement | undefined
  const last = focusable[focusable.length - 1] as HTMLElement | undefined
  if (!first || !last) return

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(
  () => props.modelValue,
  async (isOpen) => {
    document.body.style.overflow = isOpen ? 'hidden' : ''

    if (isOpen) {
      previouslyFocused = document.activeElement as HTMLElement | null
      await nextTick()
      dialogRef.value?.focus()
    } else if (previouslyFocused) {
      previouslyFocused.focus()
      previouslyFocused = null
    }
  },
)

onMounted(() => {
  window.addEventListener('keydown', onEscape)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onEscape)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto overflow-x-hidden bg-neutral-900/60 p-4 text-center backdrop-blur-sm sm:p-0" @click.self="close">
        <div
          ref="dialogRef"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          tabindex="-1"
          class="relative w-full max-w-2xl transform overflow-hidden rounded-2xl border border-neutral-100 bg-white text-left shadow-2xl transition-all sm:my-8"
          @keydown="trapFocus"
        >
          <div class="flex items-center justify-between border-b border-neutral-100 px-6 py-5 bg-neutral-50/50">
            <div>
              <h2 :id="titleId" class="text-lg font-bold leading-6 text-neutral-900">{{ title }}</h2>
              <p v-if="description" class="mt-1 text-sm text-neutral-500">{{ description }}</p>
            </div>
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-400 hover:bg-neutral-100 hover:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              @click="close"
            >
              <span class="sr-only">Fechar</span>
              <Icon name="X" :size="20" />
            </button>
          </div>
          
          <div class="px-6 py-6">
            <slot />
          </div>
          
          <div v-if="$slots.footer" class="border-t border-neutral-100 bg-neutral-50 px-6 py-4 flex justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
