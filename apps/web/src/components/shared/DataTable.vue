<script setup lang="ts" generic="T extends Record<string, unknown>">
import { computed, ref, watch } from 'vue'

import Button from '@/components/ui/Button.vue'

export interface DataColumn {
  key: string
  label: string
  sortable?: boolean
  class?: string
  formatter?: (value: unknown, row: Record<string, unknown>) => string
}

const props = withDefaults(
  defineProps<{
    columns: DataColumn[]
    rows: T[]
    pageSize?: number
    emptyText?: string
  }>(),
  {
    pageSize: 10,
    emptyText: 'Nenhum registro encontrado.',
  },
)

const currentPage = ref(1)
const sortKey = ref<string>('')
const sortDirection = ref<'asc' | 'desc'>('asc')

watch(
  () => props.rows,
  () => {
    currentPage.value = 1
  },
)

const sortedRows = computed(() => {
  if (!sortKey.value) {
    return props.rows
  }

  return [...props.rows].sort((a, b) => {
    const first = String(a[sortKey.value] ?? '')
    const second = String(b[sortKey.value] ?? '')
    const compare = first.localeCompare(second, 'pt-BR', { numeric: true, sensitivity: 'base' })
    return sortDirection.value === 'asc' ? compare : -compare
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedRows.value.length / props.pageSize)))

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  return sortedRows.value.slice(start, start + props.pageSize)
})

function toggleSort(column: DataColumn) {
  if (!column.sortable) {
    return
  }

  if (sortKey.value === column.key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    return
  }

  sortKey.value = column.key
  sortDirection.value = 'asc'
}

function resolveCell(column: DataColumn, row: T): string {
  const value = row[column.key]
  if (column.formatter) {
    return column.formatter(value, row)
  }
  return String(value ?? '-')
}
</script>

<template>
  <div class="space-y-4">
    <div class="overflow-hidden rounded-3xl bg-white shadow-xl shadow-neutral-200/40 ring-1 ring-neutral-200/50">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-neutral-100">
          <thead class="bg-neutral-50/50">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                scope="col"
                class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-neutral-500"
                :class="column.class"
                :aria-sort="column.sortable ? (sortKey === column.key ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none') : undefined"
              >
                <div v-if="!column.sortable" class="flex items-center gap-2">
                   {{ column.label }}
                </div>
                <button
                  v-else
                  type="button"
                  class="group inline-flex items-center gap-2 transition-colors hover:text-neutral-900"
                  :aria-label="`Ordenar por ${column.label}`"
                  @click="toggleSort(column)"
                >
                  {{ column.label }}
                  <span
                    class="rounded p-0.5 transition-colors group-hover:bg-neutral-200"
                    :class="{ 'opacity-0 group-hover:opacity-100': sortKey !== column.key, 'bg-neutral-100 text-primary-600': sortKey === column.key }"
                  >
                     <svg v-if="sortKey === column.key && sortDirection === 'desc'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                     <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
                  </span>
                </button>
              </th>
              <th v-if="$slots.actions" scope="col" class="px-6 py-4 text-right header-actions"><span class="sr-only">Ações</span></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100 bg-white">
            <tr v-if="!paginatedRows.length">
              <td class="px-6 py-12 text-center text-neutral-500" :colspan="columns.length + ($slots.actions ? 1 : 0)">
                <div class="flex flex-col items-center justify-center gap-2">
                  <div class="flex h-12 w-12 items-center justify-center rounded-full bg-neutral-100 text-neutral-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                  </div>
                  <p class="font-medium">{{ emptyText }}</p>
                </div>
              </td>
            </tr>
            <tr v-for="(row, rowIndex) in paginatedRows" :key="String(row.id ?? rowIndex)" class="group transition-colors hover:bg-neutral-50/80">
              <td 
                v-for="column in columns" 
                :key="column.key" 
                class="whitespace-nowrap px-6 py-4 text-sm text-neutral-600 transition-colors group-hover:text-neutral-900"
                :class="column.class"
              >
                {{ resolveCell(column, row) }}
              </td>
              <td v-if="$slots.actions" class="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <slot name="actions" :row="row" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-neutral-200 pt-4">
      <p class="text-sm text-neutral-500">
        Mostrando <span class="font-medium text-neutral-900">{{ currentPage }}</span> de <span class="font-medium text-neutral-900">{{ totalPages }}</span> páginas
      </p>
      <div class="flex gap-2">
        <Button 
          variant="secondary" 
          size="sm" 
          :disabled="currentPage <= 1" 
          @click="currentPage -= 1"
          class="gap-1 pl-2.5"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          Anterior
        </Button>
        <Button 
          variant="secondary" 
          size="sm" 
          :disabled="currentPage >= totalPages" 
          @click="currentPage += 1"
          class="gap-1 pr-2.5"
        >
          Próxima
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </Button>
      </div>
    </div>
  </div>
</template>
