<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ClientForm from '@/components/domain/ClientForm.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import DataTable, { type DataColumn } from '@/components/shared/DataTable.vue'
import DropdownMenu from '@/components/shared/DropdownMenu.vue'
import Modal from '@/components/shared/Modal.vue'
import SearchInput from '@/components/shared/SearchInput.vue'
import Button from '@/components/ui/Button.vue'
import { useClients } from '@/composables/useClients'
import { extractApiError } from '@/lib/api-error'
import { formatDate } from '@/lib/format'
import { useToastStore } from '@/stores/toast'
import type { Client } from '@/types/entities'

const clientsApi = useClients()
const toastStore = useToastStore()

const clients = ref<Client[]>([])
const isLoading = ref(false)
const search = ref('')

const isModalOpen = ref(false)
const selectedClient = ref<Client | null>(null)
const selectedPhotoFile = ref<File | null>(null)

const isConfirmOpen = ref(false)
const clientPendingDelete = ref<Client | null>(null)

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-20' },
  { key: 'name', label: 'Nome', sortable: true },
  { key: 'cpf', label: 'CPF', sortable: true },
  {
    key: 'created_at',
    label: 'Cadastro',
    sortable: true,
    formatter: (value) => formatDate(String(value ?? '')),
  },
]

const filteredRows = computed(() => {
  if (!search.value.trim()) {
    return clients.value
  }
  const query = search.value.toLowerCase()
  return clients.value.filter((client) => {
    return [client.name, client.cpf ?? ''].join(' ').toLowerCase().includes(query)
  })
})

const modalTitle = computed(() => (selectedClient.value ? 'Editar cliente' : 'Novo cliente'))

async function loadClients() {
  isLoading.value = true
  try {
    clients.value = await clientsApi.list()
  } finally {
    isLoading.value = false
  }
}

function openCreate() {
  selectedClient.value = null
  selectedPhotoFile.value = null
  isModalOpen.value = true
}

function openEdit(client: Client) {
  selectedClient.value = client
  selectedPhotoFile.value = null
  isModalOpen.value = true
}

function requestDelete(client: Client) {
  clientPendingDelete.value = client
  isConfirmOpen.value = true
}

function buildActions(client: Client) {
  return [
    {
      label: 'Editar',
      onClick: () => openEdit(client),
    },
    {
      label: 'Excluir',
      danger: true,
      onClick: () => requestDelete(client),
    },
  ]
}

function onPhotoSelected(event: Event) {
  const target = event.target as HTMLInputElement
  selectedPhotoFile.value = target.files?.[0] ?? null
}

async function submitClient(payload: { cpf: string; name: string }) {
  isLoading.value = true
  try {
    let persistedClient: Client
    if (selectedClient.value) {
      persistedClient = await clientsApi.update(selectedClient.value.id, {
        cpf: payload.cpf,
        name: payload.name,
      })
      toastStore.push({ title: 'Cliente atualizado', variant: 'success' })
    } else {
      persistedClient = await clientsApi.create({
        cpf: payload.cpf,
        name: payload.name,
      })
      toastStore.push({ title: 'Cliente criado', variant: 'success' })
    }

    if (selectedPhotoFile.value) {
      await clientsApi.uploadPhoto(persistedClient.id, selectedPhotoFile.value)
    }

    selectedPhotoFile.value = null
    isModalOpen.value = false
    await loadClients()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao salvar cliente.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

async function confirmDelete() {
  if (!clientPendingDelete.value) {
    return
  }

  isLoading.value = true
  try {
    await clientsApi.remove(clientPendingDelete.value.id)
    toastStore.push({ title: 'Cliente removido', variant: 'success' })
    isConfirmOpen.value = false
    clientPendingDelete.value = null
    await loadClients()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao excluir cliente.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadClients()
})
</script>

<template>
  <section class="space-y-6">
    <!-- Header Section -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="font-display text-2xl font-bold tracking-tight text-neutral-900">Clientes</h2>
        <p class="text-neutral-500">Gerencie o cadastro completo de seus clientes.</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="w-full sm:w-72">
           <SearchInput v-model="search" placeholder="Buscar cliente..." />
        </div>
        <Button @click="openCreate" class="shadow-lg shadow-primary-600/20">
          <Icon name="Plus" :size="18" />
          Novo
        </Button>
      </div>
    </div>

    <!-- Data Table (Glass/Card Style) -->
    <DataTable 
      :columns="columns" 
      :rows="filteredRows" 
      :page-size="8" 
      empty-text="Nenhum cliente encontrado."
      class="border-none"
    >
      <template #actions="{ row }">
        <DropdownMenu :actions="buildActions(row)" />
      </template>
    </DataTable>

    <!-- Modals -->
    <Modal
      :model-value="isModalOpen"
      :title="modalTitle"
      @update:model-value="(value) => (isModalOpen = value)"
    >
      <ClientForm
        :model-value="
          selectedClient
            ? {
                cpf: selectedClient.cpf ?? '',
                name: selectedClient.name,
              }
            : undefined
        "
        :loading="isLoading"
        :submit-label="selectedClient ? 'Salvar alterações' : 'Criar cliente'"
        @submit="submitClient"
        @cancel="isModalOpen = false"
      />
      <div class="mt-4 rounded-lg border border-dashed border-neutral-300 p-4">
        <label class="text-sm font-medium text-neutral-700" for="client-photo-upload">Foto do cliente (opcional)</label>
        <input
          id="client-photo-upload"
          type="file"
          accept="image/png,image/jpeg"
          class="mt-2 block w-full text-sm"
          :disabled="isLoading"
          @change="onPhotoSelected"
        />
      </div>
    </Modal>

    <ConfirmDialog
      :model-value="isConfirmOpen"
      title="Excluir cliente"
      :description="`Deseja excluir ${clientPendingDelete?.name ?? 'este cliente'}?`"
      :loading="isLoading"
      @update:model-value="(value) => (isConfirmOpen = value)"
      @confirm="confirmDelete"
    />
  </section>
</template>
