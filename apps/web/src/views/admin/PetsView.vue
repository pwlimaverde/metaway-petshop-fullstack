<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import PetForm from '@/components/domain/PetForm.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import DataTable, { type DataColumn } from '@/components/shared/DataTable.vue'
import DropdownMenu from '@/components/shared/DropdownMenu.vue'
import Modal from '@/components/shared/Modal.vue'
import SearchInput from '@/components/shared/SearchInput.vue'
import Button from '@/components/ui/Button.vue'
import { useBreeds } from '@/composables/useBreeds'
import { useClients } from '@/composables/useClients'
import { usePets } from '@/composables/usePets'
import { formatDate } from '@/lib/format'
import { useToastStore } from '@/stores/toast'
import type { Breed, Client, Pet } from '@/types/entities'

const petsApi = usePets()
const clientsApi = useClients()
const breedsApi = useBreeds()
const toastStore = useToastStore()

const pets = ref<Pet[]>([])
const clients = ref<Client[]>([])
const breeds = ref<Breed[]>([])
const isLoading = ref(false)
const search = ref('')

const isModalOpen = ref(false)
const selectedPet = ref<Pet | null>(null)
const selectedPhotoFile = ref<File | null>(null)

const isConfirmOpen = ref(false)
const petPendingDelete = ref<Pet | null>(null)

const clientMap = computed(() => {
  const entries = clients.value.map((client) => [client.id, client.name])
  return Object.fromEntries(entries)
})

const breedMap = computed(() => {
  const entries = breeds.value.map((breed) => [breed.id, breed.descricao])
  return Object.fromEntries(entries)
})

const rows = computed(() =>
  pets.value.map((pet) => ({
    ...pet,
    client_name: clientMap.value[pet.client_id] ?? `Cliente #${pet.client_id}`,
    breed_name: breedMap.value[pet.breed_id] ?? `Raça #${pet.breed_id}`,
  })),
)

const filteredRows = computed(() => {
  if (!search.value.trim()) {
    return rows.value
  }
  const query = search.value.toLowerCase()
  return rows.value.filter((pet) => [pet.name, pet.client_name, pet.breed_name].join(' ').toLowerCase().includes(query))
})

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-20' },
  { key: 'name', label: 'Nome', sortable: true },
  { key: 'client_name', label: 'Cliente', sortable: true },
  { key: 'breed_name', label: 'Raça', sortable: true },
  {
    key: 'birth_date',
    label: 'Nascimento',
    sortable: true,
    formatter: (value) => formatDate(String(value ?? '')),
  },
]

const clientOptions = computed(() => clients.value.map((client) => ({ label: client.name, value: client.id })))
const breedOptions = computed(() => breeds.value.map((breed) => ({ label: breed.descricao, value: breed.id })))

const modalTitle = computed(() => (selectedPet.value ? 'Editar pet' : 'Novo pet'))

async function loadData() {
  isLoading.value = true
  try {
    const [loadedPets, loadedClients, loadedBreeds] = await Promise.all([
      petsApi.list(),
      clientsApi.list(),
      breedsApi.list(),
    ])
    pets.value = loadedPets
    clients.value = loadedClients
    breeds.value = loadedBreeds
  } finally {
    isLoading.value = false
  }
}

function openCreate() {
  selectedPet.value = null
  selectedPhotoFile.value = null
  isModalOpen.value = true
}

function openEdit(pet: Pet) {
  selectedPet.value = pet
  selectedPhotoFile.value = null
  isModalOpen.value = true
}

function requestDelete(pet: Pet) {
  petPendingDelete.value = pet
  isConfirmOpen.value = true
}

function buildActions(pet: Pet) {
  return [
    {
      label: 'Editar',
      onClick: () => openEdit(pet),
    },
    {
      label: 'Excluir',
      danger: true,
      onClick: () => requestDelete(pet),
    },
  ]
}

function onPhotoSelected(event: Event) {
  const target = event.target as HTMLInputElement
  selectedPhotoFile.value = target.files?.[0] ?? null
}

async function submitPet(payload: {
  client_id: number | null
  breed_id: number | null
  name: string
  birth_date: string
}) {
  if (!payload.client_id || !payload.breed_id) {
    return
  }

  isLoading.value = true
  try {
    let persistedPet: Pet
    if (selectedPet.value) {
      persistedPet = await petsApi.update(selectedPet.value.id, {
        client_id: payload.client_id,
        breed_id: payload.breed_id,
        name: payload.name,
        birth_date: payload.birth_date,
      })
      toastStore.push({ title: 'Pet atualizado', variant: 'success' })
    } else {
      persistedPet = await petsApi.create({
        client_id: payload.client_id,
        breed_id: payload.breed_id,
        name: payload.name,
        birth_date: payload.birth_date,
      })
      toastStore.push({ title: 'Pet criado', variant: 'success' })
    }

    if (selectedPhotoFile.value) {
      await petsApi.uploadPhoto(persistedPet.id, selectedPhotoFile.value)
    }

    selectedPhotoFile.value = null
    isModalOpen.value = false
    await loadData()
  } finally {
    isLoading.value = false
  }
}

async function confirmDelete() {
  if (!petPendingDelete.value) {
    return
  }

  isLoading.value = true
  try {
    await petsApi.remove(petPendingDelete.value.id)
    toastStore.push({ title: 'Pet removido', variant: 'success' })
    isConfirmOpen.value = false
    petPendingDelete.value = null
    await loadData()
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <section class="space-y-6">
    <!-- Header Section -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="font-display text-2xl font-bold tracking-tight text-neutral-900">Pets</h2>
        <p class="text-neutral-500">Gerencie todos os pets cadastrados no sistema.</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="w-full sm:w-72">
           <SearchInput v-model="search" placeholder="Buscar pet, cliente ou raça..." />
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
      empty-text="Nenhum pet encontrado."
      class="border-none"
    >
      <template #actions="{ row }">
        <DropdownMenu :actions="buildActions(row)" />
      </template>
    </DataTable>

    <Modal :model-value="isModalOpen" :title="modalTitle" @update:model-value="(value) => (isModalOpen = value)">
      <PetForm
        :model-value="
          selectedPet
            ? {
                client_id: selectedPet.client_id,
                breed_id: selectedPet.breed_id,
                name: selectedPet.name,
                birth_date: selectedPet.birth_date,
              }
            : undefined
        "
        :clients="clientOptions"
        :breeds="breedOptions"
        :loading="isLoading"
        :submit-label="selectedPet ? 'Salvar alterações' : 'Criar pet'"
        @submit="submitPet"
        @cancel="isModalOpen = false"
      />
      <div class="mt-4 rounded-lg border border-dashed border-neutral-300 p-4">
        <label class="text-sm font-medium text-neutral-700" for="pet-photo-upload">Foto do pet (opcional)</label>
        <input
          id="pet-photo-upload"
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
      title="Excluir pet"
      :description="`Deseja excluir ${petPendingDelete?.name ?? 'este pet'}?`"
      :loading="isLoading"
      @update:model-value="(value) => (isConfirmOpen = value)"
      @confirm="confirmDelete"
    />
  </section>
</template>
