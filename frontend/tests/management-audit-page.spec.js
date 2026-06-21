import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ManagementAuditPage from '../src/pages/ManagementAuditPage.vue'

function mockFetchWithRows(rows, transitionState = 'In Review') {
  return vi.fn(async (url, options = {}) => {
    if (String(url).includes('list_management_change_requests')) {
      return {
        ok: true,
        json: async () => ({ message: { items: rows, total: rows.length } }),
      }
    }
    if (String(url).includes('get_management_audit_logs')) {
      return {
        ok: true,
        json: async () => ({ message: { items: [] } }),
      }
    }
    if (String(url).includes('transition_management_change_request')) {
      return {
        ok: true,
        json: async () => ({ message: { change_request: { state: transitionState } } }),
      }
    }
    if (String(url).includes('get_management_change_request_detail')) {
      return {
        ok: true,
        json: async () => ({ message: { change_request: rows[0] || null } }),
      }
    }
    return {
      ok: true,
      json: async () => ({ message: {} }),
    }
  })
}

describe('ManagementAuditPage', () => {
  beforeEach(() => {
    window.csrf_token = 'test-token'
    window.management_boot = {}
  })

  it('shows only permitted draft actions for content editor', async () => {
    window.__managementAccess = {
      allowed: true,
      capabilities: ['management.access', 'content.edit', 'audit.view'],
    }
    global.fetch = mockFetchWithRows([
      {
        name: 'CR-0001',
        module_key: 'content',
        target_type: 'page_config',
        target_key: '/mysite',
        state: 'Draft',
      },
    ])

    const wrapper = mount(ManagementAuditPage)
    await flushPromises()

    expect(wrapper.text()).toContain('ارسال برای بازبینی')
    expect(wrapper.text()).toContain('لغو')
    expect(wrapper.text()).not.toContain('تایید')
    expect(wrapper.text()).not.toContain('انتشار')
  })

  it('runs transition action and shows success message', async () => {
    window.__managementAccess = {
      allowed: true,
      capabilities: ['management.access', 'content.review', 'audit.view'],
    }
    const fetchMock = mockFetchWithRows([
      {
        name: 'CR-0002',
        module_key: 'content',
        target_type: 'page_content_override',
        target_key: '/about',
        state: 'In Review',
      },
    ])
    global.fetch = fetchMock

    const wrapper = mount(ManagementAuditPage)
    await flushPromises()

    const approveButton = wrapper.findAll('button').find((node) => node.text() === 'تایید')
    expect(approveButton).toBeTruthy()
    await approveButton.trigger('click')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalled()
    expect(wrapper.text()).toContain('با موفقیت ثبت شد')
  })
})
