<script setup lang="ts">
import Avatar from '@/components/ui/Avatar.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { formatDate } from '@/lib/format'
import type { Pet } from '@/types/entities'

const props = defineProps<{
  pet: Pet
  breedLabel?: string
}>()

const emit = defineEmits<{
  edit: []
  delete: []
}>()
</script>

<template>
  <Card class="flex h-full flex-col gap-3">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <Avatar :src="props.pet.photo_url" :name="props.pet.name" size="lg" />
        <div>
          <h3 class="text-base font-semibold text-neutral-900">{{ props.pet.name }}</h3>
          <p class="text-sm text-neutral-500">Nascimento: {{ formatDate(props.pet.birth_date) }}</p>
        </div>
      </div>
      <Badge variant="outline">{{ props.breedLabel ?? `Raça #${props.pet.breed_id}` }}</Badge>
    </div>

    <div class="mt-auto flex justify-end gap-2">
      <Button variant="danger" size="sm" @click="emit('delete')">Excluir</Button>
      <Button variant="secondary" size="sm" @click="emit('edit')">Editar</Button>
    </div>
  </Card>
</template>
