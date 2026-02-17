import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'

import AppointmentForm from '@/components/domain/AppointmentForm.vue'

const clients = [
  { label: 'Cliente A', value: 1 },
  { label: 'Cliente B', value: 2 },
]

const pets = [
  { label: 'Rex', value: 10, client_id: 1 },
  { label: 'Luna', value: 11, client_id: 1 },
  { label: 'Mimi', value: 20, client_id: 2 },
]

describe('AppointmentForm', () => {
  it('filtra pets pelo cliente selecionado', async () => {
    const wrapper = mount(AppointmentForm, {
      props: { clients, pets },
    })

    let selects = wrapper.findAll('select')
    expect(selects[1].attributes('disabled')).toBeDefined()

    await selects[0].setValue('1')
    await nextTick()

    selects = wrapper.findAll('select')
    const petOptionsText = selects[1]
      .findAll('option')
      .map((option) => option.text())
      .join(' ')

    expect(selects[1].attributes('disabled')).toBeUndefined()
    expect(petOptionsText).toContain('Rex')
    expect(petOptionsText).toContain('Luna')
    expect(petOptionsText).not.toContain('Mimi')
  })

  it('limpa pet ao trocar para outro cliente', async () => {
    const wrapper = mount(AppointmentForm, {
      props: { clients, pets },
    })

    let selects = wrapper.findAll('select')
    await selects[0].setValue('1')
    await nextTick()

    selects = wrapper.findAll('select')
    await selects[1].setValue('10')
    await nextTick()
    expect((selects[1].element as HTMLSelectElement).value).toBe('10')

    await selects[0].setValue('2')
    await nextTick()

    selects = wrapper.findAll('select')
    expect((selects[1].element as HTMLSelectElement).value).toBe('')
  })

  it('preenche cliente automaticamente ao editar com pet existente', async () => {
    const wrapper = mount(AppointmentForm, {
      props: {
        clients,
        pets,
        modelValue: { pet_id: 20 },
      },
    })

    await nextTick()

    const selects = wrapper.findAll('select')
    expect((selects[0].element as HTMLSelectElement).value).toBe('2')

    const petOptionsText = selects[1]
      .findAll('option')
      .map((option) => option.text())
      .join(' ')
    expect(petOptionsText).toContain('Mimi')
    expect(petOptionsText).not.toContain('Rex')
  })
})
