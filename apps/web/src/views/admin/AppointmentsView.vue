<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import AppointmentForm from '@/components/domain/AppointmentForm.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import DataTable, { type DataColumn } from '@/components/shared/DataTable.vue'
import DropdownMenu from '@/components/shared/DropdownMenu.vue'
import Modal from '@/components/shared/Modal.vue'
import SearchInput from '@/components/shared/SearchInput.vue'
import Button from '@/components/ui/Button.vue'
import { useAppointments } from '@/composables/useAppointments'
import { useClients } from '@/composables/useClients'
import { usePets } from '@/composables/usePets'
import { extractApiError } from '@/lib/api-error'
import { formatCurrency, formatDate, toIsoDateTime } from '@/lib/format'
import { useToastStore } from '@/stores/toast'
import type { Appointment, AppointmentStatus, Client, Pet } from '@/types/entities'

const appointmentsApi = useAppointments()
const clientsApi = useClients()
const petsApi = usePets()
const toastStore = useToastStore()

const appointments = ref<Appointment[]>([])
const clients = ref<Client[]>([])
const pets = ref<Pet[]>([])
const isLoading = ref(false)
const search = ref('')

const isModalOpen = ref(false)
const selectedAppointment = ref<Appointment | null>(null)

const isConfirmOpen = ref(false)
const appointmentPendingDelete = ref<Appointment | null>(null)

const petMap = computed(() => {
  const entries = pets.value.map((pet) => [pet.id, pet.name])
  return Object.fromEntries(entries)
})

const rows = computed(() =>
  appointments.value.map((appointment) => ({
    ...appointment,
    pet_name: petMap.value[appointment.pet_id] ?? `Pet #${appointment.pet_id}`,
  })),
)

const filteredRows = computed(() => {
  if (!search.value.trim()) {
    return rows.value
  }
  const query = search.value.toLowerCase()
  return rows.value.filter((appointment) => {
    return [appointment.pet_name, appointment.descricao].join(' ').toLowerCase().includes(query)
  })
})

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

const clientOptions = computed(() => clients.value.map((client) => ({ label: client.name, value: client.id })))
const petOptions = computed(() => pets.value.map((pet) => ({ label: pet.name, value: pet.id, client_id: pet.client_id })))

const modalTitle = computed(() => (selectedAppointment.value ? 'Editar atendimento' : 'Novo atendimento'))

async function loadData() {
  isLoading.value = true
  try {
    const [loadedAppointments, loadedClients, loadedPets] = await Promise.all([
      appointmentsApi.list(),
      clientsApi.list(),
      petsApi.list(),
    ])
    appointments.value = loadedAppointments
    clients.value = loadedClients
    pets.value = loadedPets
  } finally {
    isLoading.value = false
  }
}

function openCreate() {
  selectedAppointment.value = null
  isModalOpen.value = true
}

function openEdit(appointment: Appointment) {
  selectedAppointment.value = appointment
  isModalOpen.value = true
}

function requestDelete(appointment: Appointment) {
  appointmentPendingDelete.value = appointment
  isConfirmOpen.value = true
}

function buildActions(appointment: Appointment) {
  return [
    {
      label: 'Editar',
      onClick: () => openEdit(appointment),
    },
    {
      label: 'Excluir',
      danger: true,
      onClick: () => requestDelete(appointment),
    },
  ]
}

async function submitAppointment(payload: {
  pet_id: number | null
  descricao: string
  valor: number
  data: string
  status: string
}) {
  if (!payload.pet_id) {
    return
  }

  isLoading.value = true
  try {
    if (selectedAppointment.value) {
      await appointmentsApi.update(selectedAppointment.value.id, {
        pet_id: payload.pet_id,
        descricao: payload.descricao,
        valor: payload.valor,
        data: toIsoDateTime(payload.data),
        status: payload.status as AppointmentStatus,
      })
      toastStore.push({ title: 'Atendimento atualizado', variant: 'success' })
    } else {
      await appointmentsApi.create({
        pet_id: payload.pet_id,
        descricao: payload.descricao,
        valor: payload.valor,
        data: toIsoDateTime(payload.data),
        status: payload.status as AppointmentStatus,
      })
      toastStore.push({ title: 'Atendimento criado', variant: 'success' })
    }

    isModalOpen.value = false
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao salvar atendimento.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

async function confirmDelete() {
  if (!appointmentPendingDelete.value) {
    return
  }

  isLoading.value = true
  try {
    await appointmentsApi.remove(appointmentPendingDelete.value.id)
    toastStore.push({ title: 'Atendimento removido', variant: 'success' })
    isConfirmOpen.value = false
    appointmentPendingDelete.value = null
    await loadData()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao excluir atendimento.'), variant: 'error' })
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
        <h2 class="font-display text-2xl font-bold tracking-tight text-neutral-900">Atendimentos</h2>
        <p class="text-neutral-500">Gerencie todos os agendamentos e atendimentos realizados.</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="w-full sm:w-72">
           <SearchInput v-model="search" placeholder="Buscar por pet ou descrição..." />
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
      empty-text="Nenhum atendimento encontrado."
      class="border-none"
    >
      <template #actions="{ row }">
        <DropdownMenu :actions="buildActions(row)" />
      </template>
    </DataTable>

    <Modal :model-value="isModalOpen" :title="modalTitle" @update:model-value="(value) => (isModalOpen = value)">
      <AppointmentForm
        :model-value="selectedAppointment ?? undefined"
        :clients="clientOptions"
        :pets="petOptions"
        :loading="isLoading"
        :submit-label="selectedAppointment ? 'Salvar alterações' : 'Criar atendimento'"
        @submit="submitAppointment"
        @cancel="isModalOpen = false"
      />
    </Modal>

    <ConfirmDialog
      :model-value="isConfirmOpen"
      title="Excluir atendimento"
      :description="`Deseja excluir o atendimento #${appointmentPendingDelete?.id ?? ''}?`"
      :loading="isLoading"
      @update:model-value="(value) => (isConfirmOpen = value)"
      @confirm="confirmDelete"
    />
  </section>
</template>
