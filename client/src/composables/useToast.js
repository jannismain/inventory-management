import { ref } from 'vue'

const toasts = ref([])
let nextId = 1

export function useToast() {
  const dismiss = (id) => {
    toasts.value = toasts.value.filter(toast => toast.id !== id)
  }

  const showToast = (message, { type = 'error', duration = 5000 } = {}) => {
    const id = nextId++
    toasts.value.push({ id, message, type })
    if (duration > 0) setTimeout(() => dismiss(id), duration)
    return id
  }

  return { toasts, showToast, dismiss }
}
