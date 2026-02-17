<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    forId?: string
    error?: string
    required?: boolean
  }>(),
  {
    forId: '',
    error: '',
    required: false,
  },
)

const errorId = useId()
const labelText = computed(() => (props.required ? `${props.label} *` : props.label))
</script>

<template>
  <div class="space-y-1.5">
    <label :for="forId" class="block text-sm font-medium text-neutral-800">{{ labelText }}</label>
    <slot :error-id="error ? errorId : undefined" />
    <p v-if="error" :id="errorId" role="alert" aria-live="polite" class="text-xs font-medium text-error">{{ error }}</p>
  </div>
</template>
