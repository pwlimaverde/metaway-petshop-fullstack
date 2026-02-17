import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Badge from '@/components/ui/Badge.vue'

describe('Badge', () => {
  it('usa variante subtle por padrão', () => {
    const wrapper = mount(Badge, {
      slots: { default: 'Novo' },
    })

    expect(wrapper.text()).toContain('Novo')
    expect(wrapper.classes().join(' ')).toContain('bg-primary-50')
  })

  it('aplica variante informada', () => {
    const wrapper = mount(Badge, {
      props: { variant: 'warning' },
      slots: { default: 'Atenção' },
    })

    expect(wrapper.classes().join(' ')).toContain('bg-amber-50')
    expect(wrapper.classes().join(' ')).toContain('text-amber-700')
  })

  it('mescla classe customizada', () => {
    const wrapper = mount(Badge, {
      props: { class: 'uppercase' },
    })

    expect(wrapper.classes().join(' ')).toContain('uppercase')
  })
})
