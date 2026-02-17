<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import DataTable, { type DataColumn } from '@/components/shared/DataTable.vue'
import Card from '@/components/ui/Card.vue'
import { useAppointments } from '@/composables/useAppointments'
import { usePets } from '@/composables/usePets'
import { formatCurrency, formatDate } from '@/lib/format'
import type { Appointment, Pet } from '@/types/entities'

const appointmentsApi = useAppointments()
const petsApi = usePets()

const appointments = ref<Appointment[]>([])
const pets = ref<Pet[]>([])
const isLoading = ref(false)

const petMap = computed(() => {
  const entries = pets.value.map((pet) => [pet.id, pet.name])
  return Object.fromEntries(entries)
})

const tableRows = computed(() =>
  appointments.value.map((appointment) => ({
    ...appointment,
    pet_name: petMap.value[appointment.pet_id] ?? `Pet #${appointment.pet_id}`,
  })),
)

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-20' },
  { key: 'pet_name', label: 'Pet', sortable: true },
  { key: 'descricao', label: 'Descrição' },
  {
    key: 'valor',
    label: 'Valor',
    sortable: true,
    formatter: (value) => formatCurrency(Number(value ?? 0)),
  },
  {
    key: 'data',
    label: 'Data',
    sortable: true,
    formatter: (value) => formatDate(String(value ?? '')),
  },
  { key: 'status', label: 'Status', sortable: true },
]

async function loadData() {
  isLoading.value = true
  try {
    const [loadedAppointments, loadedPets] = await Promise.all([appointmentsApi.list(), petsApi.list()])
    appointments.value = loadedAppointments
    pets.value = loadedPets
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
    <Card>
      <h2 class="text-lg font-semibold text-neutral-900">Meus Atendimentos</h2>
      <p class="mt-1 text-sm text-neutral-600">Histórico de atendimentos dos seus pets.</p>
    </Card>

    <DataTable :columns="columns" :rows="tableRows" :page-size="8" empty-text="Nenhum atendimento encontrado." />
  </section>
</template>
