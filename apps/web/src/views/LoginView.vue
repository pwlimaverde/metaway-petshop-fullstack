<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import { formatCpf } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const authStore = useAuthStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()

const cpf = ref('')
const password = ref('')
const errorMessage = ref('')

function onCpfInput(value: string) {
  cpf.value = formatCpf(value)
}

async function onSubmit() {
  errorMessage.value = ''

  try {
    await authStore.login(cpf.value, password.value)

    toastStore.push({
      title: 'Login realizado',
      description: 'Bem-vindo ao Metaway Petshop.',
      variant: 'success',
    })

    const redirectTarget = route.query.redirect
    if (typeof redirectTarget === 'string' && redirectTarget.length > 0) {
      await router.push(redirectTarget)
      return
    }

    await router.push(authStore.isAdmin ? '/dashboard' : '/client-dashboard')
  } catch {
    errorMessage.value = 'CPF ou senha inválidos.'
    toastStore.push({
      title: 'Falha na autenticação',
      description: 'Confira suas credenciais e tente novamente.',
      variant: 'error',
    })
  }
}
</script>

<template>
  <div class="w-full">
    <div class="space-y-2 text-center">
      <div class="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-600 mb-2">
         <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/></svg>
      </div>
      <h1 class="font-display text-3xl font-extrabold tracking-tight text-neutral-900">Bem-vindo de volta</h1>
      <p class="text-sm text-neutral-500">Insira suas credenciais para acessar sua conta.</p>
    </div>

    <form class="mt-8 space-y-6" @submit.prevent="onSubmit">
      <div class="space-y-4">
        <FormGroup label="CPF" required :error="errorMessage">
          <Input
            :model-value="cpf"
            placeholder="000.000.000-00"
            autocomplete="username"
            @update:model-value="onCpfInput"
          />
        </FormGroup>

        <FormGroup label="Senha" required>
          <Input
            v-model="password"
            type="password"
            placeholder="******"
            autocomplete="current-password"
          />
        </FormGroup>
      </div>

      <Button type="submit" class="w-full" size="lg" :loading="authStore.isLoading">Acessar</Button>
    </form>
  </div>
</template>
