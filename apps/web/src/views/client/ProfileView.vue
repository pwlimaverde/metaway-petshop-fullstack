<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import AddressForm from '@/components/domain/AddressForm.vue'
import ClientForm from '@/components/domain/ClientForm.vue'
import ContactForm from '@/components/domain/ContactForm.vue'
import Modal from '@/components/shared/Modal.vue'
import Avatar from '@/components/ui/Avatar.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { useAddresses } from '@/composables/useAddresses'
import { useClients } from '@/composables/useClients'
import { useContacts } from '@/composables/useContacts'
import { useUsers } from '@/composables/useUsers'
import { extractApiError } from '@/lib/api-error'
import { MIN_PASSWORD_DIGITS, MIN_PASSWORD_LENGTH } from '@/lib/password'
import { useToastStore } from '@/stores/toast'
import type { Address, Client, Contact } from '@/types/entities'

const clientsApi = useClients()
const usersApi = useUsers()
const addressesApi = useAddresses()
const contactsApi = useContacts()
const toastStore = useToastStore()

const client = ref<Client | null>(null)
const addresses = ref<Address[]>([])
const contacts = ref<Contact[]>([])
const isLoading = ref(false)
const isUploading = ref(false)

// Profile edit modal
const isProfileModalOpen = ref(false)
const formValue = computed(() => ({
  name: client.value?.name ?? '',
}))

// Password change
const isChangingPassword = ref(false)
const passwordForm = ref({ current_password: '', new_password: '' })
const passwordError = ref('')

// Address edit modal
const isAddressModalOpen = ref(false)
const selectedAddress = ref<Address | null>(null)
const isAddressLoading = ref(false)

// Contact edit modal
const isContactModalOpen = ref(false)
const selectedContact = ref<Contact | null>(null)
const isContactLoading = ref(false)

async function loadAll() {
  isLoading.value = true
  try {
    const [loadedClient, loadedAddresses, loadedContacts] = await Promise.all([
      clientsApi.getMe(),
      addressesApi.listMine(),
      contactsApi.listMine(),
    ])
    client.value = loadedClient
    addresses.value = loadedAddresses
    contacts.value = loadedContacts
  } finally {
    isLoading.value = false
  }
}

async function submitProfile(payload: { name: string }) {
  if (!client.value) return
  isLoading.value = true
  try {
    client.value = await clientsApi.updateMe({ name: payload.name })
    isProfileModalOpen.value = false
    toastStore.push({ title: 'Perfil atualizado', variant: 'success' })
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao atualizar perfil.'), variant: 'error' })
  } finally {
    isLoading.value = false
  }
}

async function onPhotoChange(event: Event) {
  if (!client.value) return
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  isUploading.value = true
  try {
    await clientsApi.uploadPhoto(client.value.id, file)
    client.value = await clientsApi.getMe()
    toastStore.push({ title: 'Foto atualizada', variant: 'success' })
  } finally {
    isUploading.value = false
    target.value = ''
  }
}

async function submitPasswordChange() {
  passwordError.value = ''
  const next = passwordForm.value.new_password
  const digits = (next.match(/\d/g) ?? []).length
  if (next.length < MIN_PASSWORD_LENGTH) {
    passwordError.value = `A nova senha deve ter no mínimo ${MIN_PASSWORD_LENGTH} caracteres.`
    return
  }
  if (digits < MIN_PASSWORD_DIGITS) {
    passwordError.value = `A nova senha deve conter ao menos ${MIN_PASSWORD_DIGITS} dígitos.`
    return
  }
  isChangingPassword.value = true
  try {
    await usersApi.changeMyPassword({
      current_password: passwordForm.value.current_password,
      new_password: next,
    })
    passwordForm.value = { current_password: '', new_password: '' }
    toastStore.push({ title: 'Senha atualizada', variant: 'success' })
  } catch {
    passwordError.value = 'Não foi possível alterar a senha. Verifique a senha atual.'
  } finally {
    isChangingPassword.value = false
  }
}

// Address create / edit
const isNewAddressModalOpen = ref(false)

function openAddressEdit(address: Address) {
  selectedAddress.value = address
  isAddressModalOpen.value = true
}

async function submitAddress(payload: { logradouro: string; numero: string; complemento: string; bairro: string; cidade: string; estado: string; cep: string; tag: string }) {
  if (!selectedAddress.value) return
  isAddressLoading.value = true
  try {
    await addressesApi.update(selectedAddress.value.id, { ...payload, complemento: payload.complemento || null })
    toastStore.push({ title: 'Endereço atualizado', variant: 'success' })
    isAddressModalOpen.value = false
    addresses.value = await addressesApi.listMine()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao salvar endereço.'), variant: 'error' })
  } finally {
    isAddressLoading.value = false
  }
}

async function createAddress(payload: { logradouro: string; numero: string; complemento: string; bairro: string; cidade: string; estado: string; cep: string; tag: string }) {
  isAddressLoading.value = true
  try {
    await addressesApi.createMine({ ...payload, complemento: payload.complemento || null })
    toastStore.push({ title: 'Endereço criado', variant: 'success' })
    isNewAddressModalOpen.value = false
    addresses.value = await addressesApi.listMine()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao criar endereço.'), variant: 'error' })
  } finally {
    isAddressLoading.value = false
  }
}

// Contact create / edit
const isNewContactModalOpen = ref(false)

function openContactEdit(contact: Contact) {
  selectedContact.value = contact
  isContactModalOpen.value = true
}

async function submitContact(payload: { tag: string; tipo: 'EMAIL' | 'TELEFONE'; valor: string }) {
  if (!selectedContact.value) return
  isContactLoading.value = true
  try {
    await contactsApi.update(selectedContact.value.id, payload)
    toastStore.push({ title: 'Contato atualizado', variant: 'success' })
    isContactModalOpen.value = false
    contacts.value = await contactsApi.listMine()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao salvar contato.'), variant: 'error' })
  } finally {
    isContactLoading.value = false
  }
}

async function createContact(payload: { tag: string; tipo: 'EMAIL' | 'TELEFONE'; valor: string }) {
  isContactLoading.value = true
  try {
    await contactsApi.createMine(payload)
    toastStore.push({ title: 'Contato criado', variant: 'success' })
    isNewContactModalOpen.value = false
    contacts.value = await contactsApi.listMine()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao criar contato.'), variant: 'error' })
  } finally {
    isContactLoading.value = false
  }
}

async function deleteAddress(address: Address) {
  if (!confirm('Tem certeza que deseja excluir este endereço?')) return
  isAddressLoading.value = true
  try {
    await addressesApi.remove(address.id)
    toastStore.push({ title: 'Endereço excluído', variant: 'success' })
    addresses.value = await addressesApi.listMine()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao excluir endereço.'), variant: 'error' })
  } finally {
    isAddressLoading.value = false
  }
}

async function deleteContact(contact: Contact) {
  if (!confirm('Tem certeza que deseja excluir este contato?')) return
  isContactLoading.value = true
  try {
    await contactsApi.remove(contact.id)
    toastStore.push({ title: 'Contato excluído', variant: 'success' })
    contacts.value = await contactsApi.listMine()
  } catch (error: unknown) {
    toastStore.push({ title: extractApiError(error, 'Erro ao excluir contato.'), variant: 'error' })
  } finally {
    isContactLoading.value = false
  }
}

onMounted(() => {
  loadAll()
})
</script>

<template>
  <section class="space-y-6">
    <!-- Perfil -->
    <Card v-if="client" class="space-y-5">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <Avatar :src="client.photo_url" :name="client.name" size="lg" />
          <div>
            <h2 class="text-xl font-semibold text-neutral-900">{{ client.name }}</h2>
            <p class="text-sm text-neutral-500">CPF: {{ client.cpf || '-' }}</p>
          </div>
        </div>
        <Button variant="secondary" @click="isProfileModalOpen = true">Editar perfil</Button>
      </div>

      <div class="rounded-lg border border-dashed border-neutral-300 p-4">
        <label class="text-sm font-medium text-neutral-700" for="client-photo">Atualizar foto</label>
        <div class="mt-2 flex items-center gap-2">
          <input id="client-photo" type="file" accept="image/png,image/jpeg" class="text-sm" :disabled="isUploading" @change="onPhotoChange" />
          <span v-if="isUploading" class="text-xs text-neutral-500">Enviando...</span>
        </div>
      </div>
    </Card>

    <Card v-else-if="isLoading">
      <p class="text-sm text-neutral-500">Carregando perfil...</p>
    </Card>

    <!-- Trocar Senha -->
    <Card class="space-y-3">
      <h3 class="text-base font-semibold text-neutral-900">Trocar senha</h3>
      <form class="space-y-3" @submit.prevent="submitPasswordChange">
        <div>
          <label class="mb-1 block text-sm font-medium text-neutral-700" for="current-password">Senha atual</label>
          <input
            id="current-password"
            v-model="passwordForm.current_password"
            type="password"
            class="w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm"
            autocomplete="current-password"
            required
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-neutral-700" for="new-password">Nova senha</label>
          <input
            id="new-password"
            v-model="passwordForm.new_password"
            type="password"
            class="w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm"
            autocomplete="new-password"
            required
          />
        </div>
        <p v-if="passwordError" class="text-sm text-red-600">{{ passwordError }}</p>
        <Button type="submit" :loading="isChangingPassword">Atualizar senha</Button>
      </form>
    </Card>

    <!-- Meus Endereços -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-neutral-900">Meus Endereços</h3>
        <Button size="sm" @click="isNewAddressModalOpen = true">Novo endereço</Button>
      </div>
      <div v-if="addresses.length" class="grid gap-4 md:grid-cols-2">
        <Card v-for="address in addresses" :key="address.id" class="space-y-3">
          <div class="flex items-start justify-between gap-2">
            <p class="text-sm font-semibold uppercase tracking-wide text-primary-600">{{ address.tag }}</p>
            <div class="flex gap-2">
              <Button variant="danger" size="sm" @click="deleteAddress(address)">Excluir</Button>
              <Button variant="secondary" size="sm" @click="openAddressEdit(address)">Editar</Button>
            </div>
          </div>
          <p class="text-sm text-neutral-700">{{ address.logradouro }}, {{ address.numero }}</p>
          <p v-if="address.complemento" class="text-sm text-neutral-500">{{ address.complemento }}</p>
          <p class="text-sm text-neutral-500">{{ address.bairro }} - {{ address.cidade }}/{{ address.estado }}</p>
          <p class="text-sm text-neutral-500">CEP: {{ address.cep }}</p>
        </Card>
      </div>
      <Card v-else-if="!isLoading">
        <p class="text-sm text-neutral-500">Nenhum endereço cadastrado.</p>
      </Card>
    </div>

    <!-- Meus Contatos -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-neutral-900">Meus Contatos</h3>
        <Button size="sm" @click="isNewContactModalOpen = true">Novo contato</Button>
      </div>
      <div v-if="contacts.length" class="grid gap-4 md:grid-cols-2">
        <Card v-for="contact in contacts" :key="contact.id" class="space-y-3">
          <div class="flex items-start justify-between gap-2">
            <p class="text-sm font-semibold uppercase tracking-wide text-primary-600">{{ contact.tag }}</p>
            <div class="flex gap-2">
              <Button variant="danger" size="sm" @click="deleteContact(contact)">Excluir</Button>
              <Button variant="secondary" size="sm" @click="openContactEdit(contact)">Editar</Button>
            </div>
          </div>
          <p class="text-sm text-neutral-700">{{ contact.valor }}</p>
          <p class="text-sm text-neutral-500">{{ contact.tipo }}</p>
        </Card>
      </div>
      <Card v-else-if="!isLoading">
        <p class="text-sm text-neutral-500">Nenhum contato cadastrado.</p>
      </Card>
    </div>

    <!-- Modal: Editar Perfil -->
    <Modal
      :model-value="isProfileModalOpen"
      title="Editar perfil"
      description="Atualize seus dados pessoais."
      @update:model-value="(v) => (isProfileModalOpen = v)"
    >
      <ClientForm :model-value="formValue" :loading="isLoading" :hide-cpf="true" submit-label="Salvar alterações" @submit="submitProfile" @cancel="isProfileModalOpen = false" />
    </Modal>

    <!-- Modal: Editar Endereço -->
    <Modal
      :model-value="isAddressModalOpen"
      title="Editar endereço"
      @update:model-value="(v) => (isAddressModalOpen = v)"
    >
      <AddressForm
        :model-value="
          selectedAddress
            ? { logradouro: selectedAddress.logradouro, numero: selectedAddress.numero, complemento: selectedAddress.complemento ?? '', bairro: selectedAddress.bairro, cidade: selectedAddress.cidade, estado: selectedAddress.estado, cep: selectedAddress.cep, tag: selectedAddress.tag }
            : undefined
        "
        :loading="isAddressLoading"
        submit-label="Salvar alterações"
        @submit="submitAddress"
        @cancel="isAddressModalOpen = false"
      />
    </Modal>

    <!-- Modal: Editar Contato -->
    <Modal
      :model-value="isContactModalOpen"
      title="Editar contato"
      @update:model-value="(v) => (isContactModalOpen = v)"
    >
      <ContactForm
        :model-value="selectedContact ?? undefined"
        :loading="isContactLoading"
        submit-label="Salvar alterações"
        @submit="submitContact"
        @cancel="isContactModalOpen = false"
      />
    </Modal>

    <!-- Modal: Novo Endereço -->
    <Modal
      :model-value="isNewAddressModalOpen"
      title="Novo endereço"
      @update:model-value="(v) => (isNewAddressModalOpen = v)"
    >
      <AddressForm
        :loading="isAddressLoading"
        submit-label="Criar endereço"
        @submit="createAddress"
        @cancel="isNewAddressModalOpen = false"
      />
    </Modal>

    <!-- Modal: Novo Contato -->
    <Modal
      :model-value="isNewContactModalOpen"
      title="Novo contato"
      @update:model-value="(v) => (isNewContactModalOpen = v)"
    >
      <ContactForm
        :loading="isContactLoading"
        submit-label="Criar contato"
        @submit="createContact"
        @cancel="isNewContactModalOpen = false"
      />
    </Modal>
  </section>
</template>
