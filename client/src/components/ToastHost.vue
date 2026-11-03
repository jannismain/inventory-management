<template>
  <div class="toast-host" role="status" aria-live="polite">
    <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`toast-${toast.type}`">
      <span class="toast-message">{{ toast.message }}</span>
      <button
        type="button"
        class="toast-dismiss"
        :aria-label="t('toast.dismiss')"
        @click="dismiss(toast.id)"
      >
        ×
      </button>
    </div>
  </div>
</template>

<script>
import { useToast } from '../composables/useToast'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'ToastHost',
  setup() {
    const { toasts, dismiss } = useToast()
    const { t } = useI18n()
    return { toasts, dismiss, t }
  }
}
</script>

<style scoped>
.toast-host {
  position: fixed;
  right: var(--space-4, 1rem);
  bottom: var(--space-4, 1rem);
  z-index: 300;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: min(24rem, calc(100vw - 2rem));
}

.toast {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4, 1rem);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-danger);
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
  box-shadow: var(--shadow-md);
  font-size: 0.875rem;
}

.toast-dismiss {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.125rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
}
</style>
