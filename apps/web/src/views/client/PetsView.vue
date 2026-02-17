<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import PetCard from '@/components/domain/PetCard.vue'
import PetForm from '@/components/domain/PetForm.vue'
import Modal from '@/components/shared/Modal.vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { useBreeds } from '@/composables/useBreeds'
import { usePets } from '@/composables/usePets'
import { extractApiError } from '@/lib/api-error'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import type { Breed, Pet } from '@/types/entities'

const petsApi = usePets()
const breedsApi = useBreeds()
const authStore = useAuthStore()
const toastStore = useToastStore()

const pets = ref<Pet[]>([])
const breeds = ref<Breed[]>([])
const isLoading = ref(false)

// Pet edit
const selectedPet = ref<Pet | null>(null)
const isPetModalOpen = ref(false)
const selectedPhotoFile = ref<File | null>(null)

// Pet create
const isNewPetModalOpen = ref(false)
const newPetPhotoFile = ref<File | null>(null)

const breedOptions = computed(() => breeds.value.map((b) => ({ label: b.descricao, value: b.id })))
const breedNameMap = computed(() => Object.fromEntries(breeds.value.map((b) => [b.id, b.descricao])))

async function loadData() {
  isLoading.value = true
  try {
    const [loadedPets, loadedBreeds] = await Promise.all([petsApi.list(), breedsApi.list()])
    pets.value = loadedPets
    breeds.value = loadedBreeds
  } finally {
    isLoading.value = false
  }
}

function openPetEdit(pet: Pet) {
  selectedPet.value = pet
  selectedPhotoFile.value = null
  isPetModalOpen.value = true
}

function onPetPhotoSelected(event: Event) {
  const target = event.target as HTMLInputElement
  selectedPhotoFile.value = target.files?.[0] ?? null
}

async function submitPet(payload: { client_id: number | null; breed_id: number | null; name: string; birth_date: string }) {
  if (!selectedPet.value || !payload.breed_id || !payload.client_id) return
  isLoading.value = true
  try {
    const updatedPet = await petsApi.update(selectedPet.value.id, {
      client_id: payload.client_id,
      breed_id: payload.breed_id,
      name: payload.name,
      birth_date: payload.birth_date,
    })
    if (selectedPhotoFile.value) {
      await petsApi.uploadPhoto(updatedPet.id, selectedPhotoFile.value)
    }
    toastStore.push({ title: 'Pet atualizado', variant: 'success' })
    selectedPhotoFile.value = null
    isPetModalOpen.value = false
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao salvar pet.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

// Pet creation
function onNewPetPhotoSelected(event: Event) {
  const target = event.target as HTMLInputElement
  newPetPhotoFile.value = target.files?.[0] ?? null
}

async function createPet(payload: { client_id: number | null; breed_id: number | null; name: string; birth_date: string }) {
  if (!payload.breed_id) return
  const clientId = authStore.user?.client_id
  if (!clientId) return
  isLoading.value = true
  try {
    const createdPet = await petsApi.create({
      client_id: clientId,
      breed_id: payload.breed_id,
      name: payload.name,
      birth_date: payload.birth_date,
    })
    if (newPetPhotoFile.value) {
      await petsApi.uploadPhoto(createdPet.id, newPetPhotoFile.value)
    }
    toastStore.push({ title: 'Pet criado', variant: 'success' })
    newPetPhotoFile.value = null
    isNewPetModalOpen.value = false
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao criar pet.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

async function deletePet(pet: Pet) {
  if (!confirm('Tem certeza que deseja excluir este pet?')) return
  isLoading.value = true
  try {
    await petsApi.remove(pet.id)
    toastStore.push({ title: 'Pet excluído', variant: 'success' })
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao excluir pet.'), variant: 'error' })
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
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-neutral-900">Meus Pets</h2>
        <Button size="sm" @click="isNewPetModalOpen = true">Novo pet</Button>
      </div>
      <div v-if="pets.length" class="grid gap-4 md:grid-cols-2">
        <PetCard
          v-for="pet in pets"
          :key="pet.id"
          :pet="pet"
          :breed-label="breedNameMap[pet.breed_id]"
          @edit="openPetEdit(pet)"
          @delete="deletePet(pet)"
        />
      </div>
      <Card v-else-if="!isLoading">
        <p class="text-sm text-neutral-500">Nenhum pet cadastrado.</p>
      </Card>
    </div>

    <!-- Modal: Editar Pet -->
    <Modal
      :model-value="isPetModalOpen"
      title="Editar pet"
      @update:model-value="(v) => (isPetModalOpen = v)"
    >
      <PetForm
        :model-value="
          selectedPet
            ? { client_id: selectedPet.client_id, breed_id: selectedPet.breed_id, name: selectedPet.name, birth_date: selectedPet.birth_date }
            : undefined
        "
        :breeds="breedOptions"
        :hide-client="true"
        :loading="isLoading"
        submit-label="Salvar alterações"
        @submit="submitPet"
        @cancel="isPetModalOpen = false"
      />
      <div class="mt-4 rounded-lg border border-dashed border-neutral-300 p-4">
        <label class="text-sm font-medium text-neutral-700" for="my-pet-photo-upload">Foto do pet (opcional)</label>
        <input
          id="my-pet-photo-upload"
          type="file"
          accept="image/png,image/jpeg"
          class="mt-2 block w-full text-sm"
          :disabled="isLoading"
          @change="onPetPhotoSelected"
        />
      </div>
    </Modal>

    <!-- Modal: Novo Pet -->
    <Modal
      :model-value="isNewPetModalOpen"
      title="Novo pet"
      @update:model-value="(v) => (isNewPetModalOpen = v)"
    >
      <PetForm
        :breeds="breedOptions"
        :hide-client="true"
        :loading="isLoading"
        submit-label="Criar pet"
        @submit="createPet"
        @cancel="isNewPetModalOpen = false"
      />
      <div class="mt-4 rounded-lg border border-dashed border-neutral-300 p-4">
        <label class="text-sm font-medium text-neutral-700" for="new-pet-photo-upload">Foto do pet (opcional)</label>
        <input
          id="new-pet-photo-upload"
          type="file"
          accept="image/png,image/jpeg"
          class="mt-2 block w-full text-sm"
          :disabled="isLoading"
          @change="onNewPetPhotoSelected"
        />
      </div>
    </Modal>
  </section>
</template>
