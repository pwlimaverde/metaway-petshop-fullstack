<script setup lang="ts">
import { onMounted, ref } from 'vue'

import AddressForm from '@/components/domain/AddressForm.vue'
import Modal from '@/components/shared/Modal.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { useAddresses } from '@/composables/useAddresses'
import type { Address } from '@/types/entities'
import { useToastStore } from '@/stores/toast'

const addressesApi = useAddresses()
const toastStore = useToastStore()

const addresses = ref<Address[]>([])
const isLoading = ref(false)
const isModalOpen = ref(false)
const selectedAddress = ref<Address | null>(null)

async function loadAddresses() {
  isLoading.value = true
  try {
    addresses.value = await addressesApi.listMine()
  } finally {
    isLoading.value = false
  }
}

function openEdit(address: Address) {
  selectedAddress.value = address
  isModalOpen.value = true
}

async function submitAddress(payload: {
  logradouro: string
  cidade: string
  bairro: string
  complemento: string
  tag: string
}) {
  if (!selectedAddress.value) {
    return
  }

  isLoading.value = true
  try {
    await addressesApi.update(selectedAddress.value.id, {
      ...payload,
      complemento: payload.complemento || null,
    })
    toastStore.push({ title: 'Endereço atualizado', variant: 'success' })
    isModalOpen.value = false
    await loadAddresses()
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadAddresses()
})
</script>

<template>
  <section class="space-y-4">
    <Card>
      <h2 class="text-lg font-semibold text-neutral-900">Meus Endereços</h2>
      <p class="mt-1 text-sm text-neutral-600">Você pode visualizar e editar seus endereços cadastrados.</p>
    </Card>

    <div class="grid gap-4 md:grid-cols-2">
      <Card v-for="address in addresses" :key="address.id" class="space-y-3">
        <div class="flex items-start justify-between gap-2">
          <p class="text-sm font-semibold uppercase tracking-wide text-primary-600">{{ address.tag }}</p>
          <Button variant="secondary" size="sm" @click="openEdit(address)">Editar</Button>
        </div>
        <p class="text-sm text-neutral-700">{{ address.logradouro }}</p>
        <p class="text-sm text-neutral-500">{{ address.bairro }} - {{ address.cidade }}</p>
        <p v-if="address.complemento" class="text-sm text-neutral-500">{{ address.complemento }}</p>
      </Card>
    </div>

    <Card v-if="!addresses.length && !isLoading">
      <p class="text-sm text-neutral-500">Nenhum endereço encontrado.</p>
    </Card>

    <Modal
      :model-value="isModalOpen"
      title="Editar endereço"
      description="Clientes podem apenas editar seus registros."
      @update:model-value="(value) => (isModalOpen = value)"
    >
      <AddressForm
        :model-value="
          selectedAddress
            ? {
                logradouro: selectedAddress.logradouro,
                cidade: selectedAddress.cidade,
                bairro: selectedAddress.bairro,
                complemento: selectedAddress.complemento ?? '',
                tag: selectedAddress.tag,
              }
            : undefined
        "
        :loading="isLoading"
        submit-label="Salvar alterações"
        @submit="submitAddress"
        @cancel="isModalOpen = false"
      />
    </Modal>
  </section>
</template>
