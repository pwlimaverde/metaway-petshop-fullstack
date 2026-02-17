import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Card from '@/components/ui/Card.vue'

describe('Card', () => {
  it('renderiza slot padrão com estilo base', () => {
    const wrapper = mount(Card, {
      slots: { default: 'Conteúdo do card' },
    })

    expect(wrapper.text()).toContain('Conteúdo do card')
    expect(wrapper.classes().join(' ')).toContain('rounded-2xl')
    expect(wrapper.classes().join(' ')).toContain('border-neutral-100')
  })

  it('aceita classe customizada', () => {
    const wrapper = mount(Card, {
      props: { class: 'bg-neutral-50 p-10' },
    })

    expect(wrapper.classes().join(' ')).toContain('bg-neutral-50')
    expect(wrapper.classes().join(' ')).toContain('p-10')
  })
})
