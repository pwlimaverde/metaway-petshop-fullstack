import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  it('aplica variante primary por padrão', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Salvar',
      },
    })

    expect(wrapper.text()).toContain('Salvar')
    expect(wrapper.classes().join(' ')).toContain('bg-primary-600')
  })

  it('aplica variante secondary', () => {
    const wrapper = mount(Button, {
      props: { variant: 'secondary' },
      slots: { default: 'Cancelar' },
    })

    expect(wrapper.classes().join(' ')).toContain('border-neutral-200')
  })

  it('aplica variante ghost', () => {
    const wrapper = mount(Button, {
      props: { variant: 'ghost' },
      slots: { default: 'Limpar' },
    })

    expect(wrapper.classes().join(' ')).toContain('bg-transparent')
  })

  it('aplica variante danger', () => {
    const wrapper = mount(Button, {
      props: { variant: 'danger' },
      slots: { default: 'Excluir' },
    })

    expect(wrapper.classes().join(' ')).toContain('bg-error')
  })

  it('aplica tamanho sm', () => {
    const wrapper = mount(Button, {
      props: { size: 'sm' },
      slots: { default: 'OK' },
    })

    expect(wrapper.classes().join(' ')).toContain('h-9')
  })

  it('aplica tamanho lg', () => {
    const wrapper = mount(Button, {
      props: { size: 'lg' },
      slots: { default: 'OK' },
    })

    expect(wrapper.classes().join(' ')).toContain('h-14')
  })

  it('renderiza como disabled quando prop disabled é true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true },
      slots: { default: 'Salvar' },
    })

    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('renderiza como disabled quando loading é true', () => {
    const wrapper = mount(Button, {
      props: { loading: true },
      slots: { default: 'Salvar' },
    })

    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.attributes('aria-busy')).toBe('true')
  })

  it('mostra spinner quando loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true },
      slots: { default: 'Salvar' },
    })

    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('não mostra spinner quando não está loading', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Salvar' },
    })

    expect(wrapper.find('svg').exists()).toBe(false)
  })

  it('emite click event', async () => {
    const wrapper = mount(Button, {
      slots: { default: 'Salvar' },
    })

    await wrapper.trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('usa type button por padrão', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Salvar' },
    })

    expect(wrapper.attributes('type')).toBe('button')
  })

  it('aceita type submit', () => {
    const wrapper = mount(Button, {
      props: { type: 'submit' },
      slots: { default: 'Salvar' },
    })

    expect(wrapper.attributes('type')).toBe('submit')
  })
})
