<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import Toast from '@/components/shared/Toast.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const route = useRoute()

const currentLayout = computed(() => {
  if (route.meta.layout === 'auth') {
    return AuthLayout
  }
  return DefaultLayout
})
</script>

<template>
  <component :is="currentLayout">
    <RouterView />
  </component>
  <Toast />
</template>
