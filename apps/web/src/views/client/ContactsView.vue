<script setup lang="ts">
import { onMounted, ref } from 'vue'

import ContactForm from '@/components/domain/ContactForm.vue'
import Modal from '@/components/shared/Modal.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { useContacts } from '@/composables/useContacts'
import type { Contact } from '@/types/entities'
import { useToastStore } from '@/stores/toast'

const contactsApi = useContacts()
const toastStore = useToastStore()

const contacts = ref<Contact[]>([])
const isLoading = ref(false)
const isModalOpen = ref(false)
const selectedContact = ref<Contact | null>(null)

async function loadContacts() {
  isLoading.value = true
  try {
    contacts.value = await contactsApi.listMine()
  } finally {
    isLoading.value = false
  }
}

function openEdit(contact: Contact) {
  selectedContact.value = contact
  isModalOpen.value = true
}

async function submitContact(payload: {
  tag: string
  tipo: 'EMAIL' | 'TELEFONE'
  valor: string
}) {
  if (!selectedContact.value) {
    return
  }

  isLoading.value = true
  try {
    await contactsApi.update(selectedContact.value.id, payload)
    toastStore.push({ title: 'Contato atualizado', variant: 'success' })
    isModalOpen.value = false
    await loadContacts()
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadContacts()
})
</script>

<template>
  <section class="space-y-4">
    <Card>
      <h2 class="text-lg font-semibold text-neutral-900">Meus Contatos</h2>
      <p class="mt-1 text-sm text-neutral-600">Você pode editar seus contatos, sem criar ou excluir registros.</p>
    </Card>

    <div class="grid gap-4 md:grid-cols-2">
      <Card v-for="contact in contacts" :key="contact.id" class="space-y-3">
        <div class="flex items-start justify-between gap-2">
          <p class="text-sm font-semibold uppercase tracking-wide text-primary-600">{{ contact.tag }}</p>
          <Button variant="secondary" size="sm" @click="openEdit(contact)">Editar</Button>
        </div>
        <p class="text-sm text-neutral-700">{{ contact.valor }}</p>
        <p class="text-sm text-neutral-500">{{ contact.tipo }}</p>
      </Card>
    </div>

    <Card v-if="!contacts.length && !isLoading">
      <p class="text-sm text-neutral-500">Nenhum contato encontrado.</p>
    </Card>

    <Modal
      :model-value="isModalOpen"
      title="Editar contato"
      description="Clientes podem apenas editar seus registros."
      @update:model-value="(value) => (isModalOpen = value)"
    >
      <ContactForm
        :model-value="selectedContact ?? undefined"
        :loading="isLoading"
        submit-label="Salvar alterações"
        @submit="submitContact"
        @cancel="isModalOpen = false"
      />
    </Modal>
  </section>
</template>
