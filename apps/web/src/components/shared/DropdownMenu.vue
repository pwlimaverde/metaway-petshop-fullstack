<script setup lang="ts">
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'

import Button from '@/components/ui/Button.vue'
import Icon from '@/components/ui/Icon.vue'

interface DropdownAction {
  label: string
  danger?: boolean
  disabled?: boolean
  onClick: () => void
}

defineProps<{
  actions: DropdownAction[]
}>()
</script>

<template>
  <Menu as="div" class="relative inline-block text-left">
    <MenuButton as="template">
      <Button variant="ghost" size="sm" class="!px-2">
        <Icon name="MoreHorizontal" :size="16" />
      </Button>
    </MenuButton>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <MenuItems class="absolute right-0 z-20 mt-1 min-w-36 rounded-lg border border-neutral-200 bg-white p-1 shadow-lg">
        <MenuItem v-for="action in actions" :key="action.label" v-slot="{ active }">
          <button
            type="button"
            class="w-full rounded-md px-3 py-1.5 text-left text-sm"
            :class="[
              active ? 'bg-neutral-100' : '',
              action.danger ? 'text-error' : 'text-neutral-800',
              action.disabled ? 'cursor-not-allowed opacity-50' : '',
            ]"
            :disabled="action.disabled"
            @click="action.onClick"
          >
            {{ action.label }}
          </button>
        </MenuItem>
      </MenuItems>
    </Transition>
  </Menu>
</template>
