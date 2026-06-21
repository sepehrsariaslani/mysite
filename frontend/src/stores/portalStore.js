import { ref } from 'vue'

const SELECTED_CUSTOMER_KEY = 'mysite_selected_customer'

function loadSelectedCustomer() {
  try {
    return localStorage.getItem(SELECTED_CUSTOMER_KEY) || ''
  } catch (e) {
    return ''
  }
}

const selectedCustomer = ref(loadSelectedCustomer())

function persistSelectedCustomer(value) {
  try {
    if (!value) {
      localStorage.removeItem(SELECTED_CUSTOMER_KEY)
      return
    }
    localStorage.setItem(SELECTED_CUSTOMER_KEY, value)
  } catch (e) {
    // Ignore storage failures to avoid breaking UI.
  }
}

export const usePortalStore = () => {
  const setSelectedCustomer = (customerName) => {
    selectedCustomer.value = customerName || ''
    persistSelectedCustomer(selectedCustomer.value)
  }

  const clearSelectedCustomer = () => {
    setSelectedCustomer('')
  }

  return {
    selectedCustomer,
    setSelectedCustomer,
    clearSelectedCustomer
  }
}
