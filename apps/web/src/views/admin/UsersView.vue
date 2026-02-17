<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import UserForm from '@/components/domain/UserForm.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import DataTable, { type DataColumn } from '@/components/shared/DataTable.vue'
import DropdownMenu from '@/components/shared/DropdownMenu.vue'
import Modal from '@/components/shared/Modal.vue'
import SearchInput from '@/components/shared/SearchInput.vue'
import Button from '@/components/ui/Button.vue'
import { useClients } from '@/composables/useClients'
import { useUsers } from '@/composables/useUsers'
import { extractApiError } from '@/lib/api-error'
import { useToastStore } from '@/stores/toast'
import type { Client, UserEntity } from '@/types/entities'

const usersApi = useUsers()
const clientsApi = useClients()
const toastStore = useToastStore()

const users = ref<UserEntity[]>([])
const clients = ref<Client[]>([])
const isLoading = ref(false)
const search = ref('')

const isModalOpen = ref(false)
const selectedUser = ref<UserEntity | null>(null)

const isConfirmOpen = ref(false)
const userPendingDelete = ref<UserEntity | null>(null)

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-20' },
  { key: 'name', label: 'Nome', sortable: true },
  { key: 'cpf', label: 'CPF', sortable: true },
  { key: 'role', label: 'Perfil', sortable: true },
  { key: 'client_name', label: 'Cliente vinculado', sortable: true },
]

const clientMap = computed(() => {
  const entries = clients.value.map((client) => [client.id, client.name])
  return Object.fromEntries(entries)
})

const rows = computed(() =>
  users.value.map((user) => ({
    ...user,
    client_name: user.client_id ? clientMap.value[user.client_id] ?? `Cliente #${user.client_id}` : '-',
  })),
)

const filteredRows = computed(() => {
  if (!search.value.trim()) {
    return rows.value
  }
  const query = search.value.toLowerCase()
  return rows.value.filter((user) => [user.name, user.cpf, user.role].join(' ').toLowerCase().includes(query))
})

const clientOptions = computed(() =>
  clients.value.map((client) => ({
    label: client.name,
    value: client.id,
    cpf: client.cpf,
  })),
)

const modalTitle = computed(() => (selectedUser.value ? 'Editar usuário' : 'Novo usuário'))

async function loadData() {
  isLoading.value = true
  try {
    const [loadedUsers, loadedClients] = await Promise.all([usersApi.list(), clientsApi.list()])
    users.value = loadedUsers
    clients.value = loadedClients
  } finally {
    isLoading.value = false
  }
}

function openCreate() {
  selectedUser.value = null
  isModalOpen.value = true
}

function openEdit(user: UserEntity) {
  selectedUser.value = user
  isModalOpen.value = true
}

function requestDelete(user: UserEntity) {
  userPendingDelete.value = user
  isConfirmOpen.value = true
}

function buildActions(user: UserEntity) {
  return [
    {
      label: 'Editar',
      onClick: () => openEdit(user),
    },
    {
      label: 'Excluir',
      danger: true,
      onClick: () => requestDelete(user),
    },
  ]
}

async function submitUser(payload: {
  cpf: string
  name: string
  role: 'ADMIN' | 'CLIENTE'
  password: string
  client_id: number | null
}) {
  isLoading.value = true
  try {
    if (selectedUser.value) {
      await usersApi.update(selectedUser.value.id, {
        cpf: payload.cpf,
        name: payload.name,
        role: payload.role,
        client_id: payload.client_id,
        ...(payload.password ? { password: payload.password } : {}),
      })
      toastStore.push({ title: 'Usuário atualizado', variant: 'success' })
    } else {
      await usersApi.create({
        cpf: payload.cpf,
        name: payload.name,
        role: payload.role,
        client_id: payload.client_id,
        password: payload.password,
      })
      toastStore.push({ title: 'Usuário criado', variant: 'success' })
    }

    isModalOpen.value = false
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao salvar usuário.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

async function confirmDelete() {
  if (!userPendingDelete.value) {
    return
  }

  isLoading.value = true
  try {
    await usersApi.remove(userPendingDelete.value.id)
    toastStore.push({ title: 'Usuário removido', variant: 'success' })
    isConfirmOpen.value = false
    userPendingDelete.value = null
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao excluir usuário.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <section class="space-y-4">
    <!-- Header Section -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="font-display text-2xl font-bold tracking-tight text-neutral-900">Usuários</h2>
        <p class="text-neutral-500">Gestão de acesso e perfis de usuários.</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="w-full sm:w-72">
           <SearchInput v-model="search" placeholder="Buscar usuário..." />
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
      empty-text="Nenhum usuário encontrado."
      class="border-none"
    >
      <template #actions="{ row }">
        <DropdownMenu :actions="buildActions(row)" />
      </template>
    </DataTable>

    <Modal :model-value="isModalOpen" :title="modalTitle" @update:model-value="(value) => (isModalOpen = value)">
      <UserForm
        :model-value="selectedUser ?? undefined"
        :clients="clientOptions"
        :editing="Boolean(selectedUser)"
        :loading="isLoading"
        :submit-label="selectedUser ? 'Salvar alterações' : 'Criar usuário'"
        @submit="submitUser"
        @cancel="isModalOpen = false"
      />
    </Modal>

    <ConfirmDialog
      :model-value="isConfirmOpen"
      title="Excluir usuário"
      :description="`Deseja excluir ${userPendingDelete?.name ?? 'este usuário'}?`"
      :loading="isLoading"
      @update:model-value="(value) => (isConfirmOpen = value)"
      @confirm="confirmDelete"
    />
  </section>
</template>
