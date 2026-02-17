import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Input from '@/components/ui/Input.vue'

describe('Input', () => {
  it('renderiza valor e placeholder', () => {
    const wrapper = mount(Input, {
      props: { modelValue: 'Rex', placeholder: 'Nome do pet' },
    })

    const input = wrapper.get('input')
    expect((input.element as HTMLInputElement).value).toBe('Rex')
    expect(input.attributes('placeholder')).toBe('Nome do pet')
  })

  it('emite update:modelValue no input', async () => {
    const wrapper = mount(Input, {
      props: { modelValue: '' },
    })

    await wrapper.get('input').setValue('Bolt')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['Bolt'])
  })

  it('aplica estilo de erro quando error é informado', () => {
    const wrapper = mount(Input, {
      props: { error: 'Campo obrigatório' },
    })

    expect(wrapper.get('input').classes().join(' ')).toContain('border-error')
  })

  it('aplica padding para ícone quando slot icon existe', () => {
    const wrapper = mount(Input, {
      slots: {
        icon: '<svg data-testid="search-icon" />',
      },
    })

    expect(wrapper.get('[data-testid="search-icon"]').exists()).toBe(true)
    expect(wrapper.get('input').classes().join(' ')).toContain('pl-11')
  })
})
