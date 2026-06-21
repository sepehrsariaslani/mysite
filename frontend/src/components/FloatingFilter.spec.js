import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import FloatingFilter from './FloatingFilter.vue'

function setViewport(width) {
  Object.defineProperty(window, 'innerWidth', {
    configurable: true,
    writable: true,
    value: width,
  })
  window.dispatchEvent(new Event('resize'))
}

function createWrapper() {
  return mount(FloatingFilter, {
    props: {
      availableModels: ['مدل آ', 'مدل ب'],
      availableColors: ['مشکی', 'بژ'],
      minBound: 1000000,
      maxBound: 9000000,
      step: 1000000,
    },
  })
}

describe('FloatingFilter', () => {
  it('opens and closes as desktop sidebar', async () => {
    setViewport(1280)
    const wrapper = createWrapper()

    await wrapper.get('.ff-trigger').trigger('click')
    await nextTick()
    const drawer = document.body.querySelector('.ff-drawer')
    expect(drawer).toBeTruthy()
    expect(drawer.classList.contains('is-desktop')).toBe(true)

    const overlay = document.body.querySelector('.ff-overlay')
    overlay.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()
    expect(document.body.querySelector('.ff-drawer')).toBeNull()
  })

  it('opens as mobile bottom sheet', async () => {
    setViewport(480)
    const wrapper = createWrapper()

    await wrapper.get('.ff-trigger').trigger('click')
    await nextTick()
    const drawer = document.body.querySelector('.ff-drawer')
    expect(drawer).toBeTruthy()
    expect(drawer.classList.contains('is-mobile')).toBe(true)
  })

  it('emits apply payload', async () => {
    setViewport(1280)
    const wrapper = createWrapper()

    await wrapper.get('.ff-trigger').trigger('click')
    await nextTick()
    document.body.querySelector('.ff-radio-row').dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()
    document.body.querySelector('.ff-color-item').dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()
    document.body.querySelector('.ff-apply-btn').dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()

    const payload = wrapper.emitted('apply')?.[0]?.[0]
    expect(payload.models).toEqual(['مدل آ'])
    expect(payload.colors).toEqual(['مشکی'])
    expect(payload.sort).toBe('default')
    expect(payload.priceActive).toBe(false)
  })

  it('resets selected options and emits reset', async () => {
    setViewport(1280)
    const wrapper = createWrapper()

    await wrapper.get('.ff-trigger').trigger('click')
    await nextTick()
    document.body.querySelector('.ff-radio-row').dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()
    document.body.querySelector('.ff-reset-btn').dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()

    expect(wrapper.emitted('reset')).toHaveLength(1)

    await wrapper.get('.ff-trigger').trigger('click')
    await nextTick()
    expect(document.body.querySelectorAll('.ff-radio-row.selected')).toHaveLength(0)
  })
})
