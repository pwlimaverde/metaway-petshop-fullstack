<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import DataTable, { type DataColumn } from '@/components/shared/DataTable.vue'
import DropdownMenu from '@/components/shared/DropdownMenu.vue'
import Modal from '@/components/shared/Modal.vue'
import SearchInput from '@/components/shared/SearchInput.vue'
import FormGroup from '@/components/shared/FormGroup.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import { useBreeds } from '@/composables/useBreeds'
import { useToastStore } from '@/stores/toast'
import type { Breed } from '@/types/entities'

const breedsApi = useBreeds()
const toastStore = useToastStore()

const breeds = ref<Breed[]>([])
const isLoading = ref(false)
const search = ref('')

const isModalOpen = ref(false)
const selectedBreed = ref<Breed | null>(null)
const description = ref('')

const isConfirmOpen = ref(false)
const breedPendingDelete = ref<Breed | null>(null)

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-20' },
  { key: 'descricao', label: 'Descrição', sortable: true },
]

const filteredRows = computed(() => {
  if (!search.value.trim()) {
    return breeds.value
  }
  const query = search.value.toLowerCase()
  return breeds.value.filter((breed) => breed.descricao.toLowerCase().includes(query))
})

const modalTitle = computed(() => (selectedBreed.value ? 'Editar raça' : 'Nova raça'))

async function loadBreeds() {
  isLoading.value = true
  try {
    breeds.value = await breedsApi.list()
  } finally {
    isLoading.value = false
  }
}

function openCreate() {
  selectedBreed.value = null
  description.value = ''
  isModalOpen.value = true
}

function openEdit(breed: Breed) {
  selectedBreed.value = breed
  description.value = breed.descricao
  isModalOpen.value = true
}

function requestDelete(breed: Breed) {
  breedPendingDelete.value = breed
  isConfirmOpen.value = true
}

function buildActions(breed: Breed) {
  return [
    {
      label: 'Editar',
      onClick: () => openEdit(breed),
    },
    {
      label: 'Excluir',
      danger: true,
      onClick: () => requestDelete(breed),
    },
  ]
}

async function submitBreed() {
  if (!description.value.trim()) {
    return
  }

  isLoading.value = true
  try {
    if (selectedBreed.value) {
      await breedsApi.update(selectedBreed.value.id, { descricao: description.value.trim() })
      toastStore.push({ title: 'Raça atualizada', variant: 'success' })
    } else {
      await breedsApi.create({ descricao: description.value.trim() })
      toastStore.push({ title: 'Raça criada', variant: 'success' })
    }

    isModalOpen.value = false
    await loadBreeds()
  } finally {
    isLoading.value = false
  }
}

async function confirmDelete() {
  if (!breedPendingDelete.value) {
    return
  }

  isLoading.value = true
  try {
    await breedsApi.remove(breedPendingDelete.value.id)
    toastStore.push({ title: 'Raça removida', variant: 'success' })
    isConfirmOpen.value = false
    breedPendingDelete.value = null
    await loadBreeds()
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadBreeds()
})
</script>

<template>
  <section class="space-y-4">
    <!-- Header Section -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="font-display text-2xl font-bold tracking-tight text-neutral-900">Raças</h2>
        <p class="text-neutral-500">Gerencie as raças de pets disponíveis no sistema.</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="w-full sm:w-72">
           <SearchInput v-model="search" placeholder="Buscar raça..." />
        </div>
        <Button @click="openCreate" class="shadow-lg shadow-primary-600/20">
          <Icon name="Plus" :size="18" />
          Nova
        </Button>
      </div>
    </div>

    <!-- Data Table (Glass/Card Style) -->
    <DataTable 
      :columns="columns" 
      :rows="filteredRows" 
      :page-size="8" 
      empty-text="Nenhuma raça encontrada."
      class="border-none"
    >
      <template #actions="{ row }">
        <DropdownMenu :actions="buildActions(row)" />
      </template>
    </DataTable>

    <Modal :model-value="isModalOpen" :title="modalTitle" @update:model-value="(value) => (isModalOpen = value)">
      <form class="space-y-4" @submit.prevent="submitBreed">
        <FormGroup label="Descrição" required>
          <Input v-model="description" placeholder="Ex: Poodle" />
        </FormGroup>
        <div class="flex justify-end gap-2">
          <Button variant="secondary" @click="isModalOpen = false">Cancelar</Button>
          <Button type="submit" :loading="isLoading">{{ selectedBreed ? 'Salvar alterações' : 'Criar raça' }}</Button>
        </div>
      </form>
    </Modal>

    <ConfirmDialog
      :model-value="isConfirmOpen"
      title="Excluir raça"
      :description="`Deseja excluir ${breedPendingDelete?.descricao ?? 'esta raça'}?`"
      :loading="isLoading"
      @update:model-value="(value) => (isConfirmOpen = value)"
      @confirm="confirmDelete"
    />
  </section>
</template>
