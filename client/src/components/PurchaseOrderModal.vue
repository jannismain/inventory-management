<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" role="dialog" aria-modal="true" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'view' ? t('dashboard.purchaseOrder.viewTitle') : t('dashboard.purchaseOrder.createTitle') }}
            </h3>
            <button class="close-button" :aria-label="t('dashboard.purchaseOrder.close')" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="item-header">
              <div class="item-name">{{ translateProductName(backlogItem.item_name) }}</div>
              <div class="item-meta">
                <span class="item-sku">{{ backlogItem.item_sku }}</span>
                <span class="item-shortage">
                  {{ t('dashboard.purchaseOrder.shortage') }}: {{ shortage }} {{ t('dashboard.purchaseOrder.units') }}
                </span>
              </div>
            </div>

            <!-- View mode -->
            <template v-if="mode === 'view'">
              <div v-if="loading" class="state-message">{{ t('dashboard.purchaseOrder.loading') }}</div>
              <div v-else-if="loadError" class="form-error" role="alert">{{ loadError }}</div>
              <div v-else-if="purchaseOrder" class="info-grid">
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.poId') }}</div>
                  <div class="info-value mono">{{ purchaseOrder.id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.status') }}</div>
                  <div class="info-value"><span class="badge">{{ purchaseOrder.status }}</span></div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.supplier') }}</div>
                  <div class="info-value">{{ purchaseOrder.supplier_name }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.quantity') }}</div>
                  <div class="info-value">{{ purchaseOrder.quantity }} {{ t('dashboard.purchaseOrder.units') }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.unitCost') }}</div>
                  <div class="info-value">{{ formatMoney(purchaseOrder.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.totalCost') }}</div>
                  <div class="info-value">{{ formatMoney(purchaseOrder.quantity * purchaseOrder.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.expectedDelivery') }}</div>
                  <div class="info-value">{{ formatDate(purchaseOrder.expected_delivery_date) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.createdDate') }}</div>
                  <div class="info-value">{{ formatDate(purchaseOrder.created_date) }}</div>
                </div>
                <div v-if="purchaseOrder.notes" class="info-item full">
                  <div class="info-label">{{ t('dashboard.purchaseOrder.notes') }}</div>
                  <div class="info-value notes">{{ purchaseOrder.notes }}</div>
                </div>
              </div>
            </template>

            <!-- Create mode -->
            <form v-else id="po-form" class="po-form" novalidate @submit.prevent="submit">
              <div class="form-field full">
                <label for="po-supplier">{{ t('dashboard.purchaseOrder.supplier') }}</label>
                <input id="po-supplier" v-model="form.supplier_name" type="text" maxlength="120" :class="{ invalid: errors.supplier_name }" />
                <span v-if="errors.supplier_name" class="field-error">{{ errors.supplier_name }}</span>
              </div>

              <div class="form-field">
                <label for="po-quantity">{{ t('dashboard.purchaseOrder.quantity') }}</label>
                <input id="po-quantity" v-model="form.quantity" type="number" min="1" step="1" :class="{ invalid: errors.quantity }" />
                <span v-if="errors.quantity" class="field-error">{{ errors.quantity }}</span>
              </div>

              <div class="form-field">
                <label for="po-unit-cost">{{ t('dashboard.purchaseOrder.unitCost') }}</label>
                <input id="po-unit-cost" v-model="form.unit_cost" type="number" min="0" step="0.01" :class="{ invalid: errors.unit_cost }" />
                <span v-if="errors.unit_cost" class="field-error">{{ errors.unit_cost }}</span>
              </div>

              <div class="form-field full">
                <label for="po-date">{{ t('dashboard.purchaseOrder.expectedDelivery') }}</label>
                <input id="po-date" v-model="form.expected_delivery_date" type="date" :min="today" :class="{ invalid: errors.expected_delivery_date }" />
                <span v-if="errors.expected_delivery_date" class="field-error">{{ errors.expected_delivery_date }}</span>
              </div>

              <div class="form-field full">
                <label for="po-notes">{{ t('dashboard.purchaseOrder.notes') }}</label>
                <textarea id="po-notes" v-model="form.notes" rows="3"></textarea>
              </div>

              <div v-if="submitError" class="form-error full" role="alert">{{ submitError }}</div>
            </form>
          </div>

          <div class="modal-footer">
            <template v-if="mode === 'view'">
              <button type="button" class="btn-secondary" @click="close">{{ t('dashboard.purchaseOrder.close') }}</button>
            </template>
            <template v-else>
              <button type="button" class="btn-secondary" :disabled="saving" @click="close">
                {{ t('dashboard.purchaseOrder.cancel') }}
              </button>
              <button type="submit" form="po-form" class="btn-primary" :disabled="saving">
                {{ saving ? t('dashboard.purchaseOrder.saving') : t('dashboard.purchaseOrder.submit') }}
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  backlogItem: { type: Object, default: null },
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'view'].includes(value)
  }
})

const emit = defineEmits(['close', 'po-created'])

const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

const form = reactive({
  supplier_name: '',
  quantity: 1,
  unit_cost: '',
  expected_delivery_date: '',
  notes: ''
})
const errors = reactive({})
const submitError = ref('')
const saving = ref(false)

const purchaseOrder = ref(null)
const loading = ref(false)
const loadError = ref('')

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return Math.max(props.backlogItem.quantity_needed - props.backlogItem.quantity_available, 0)
})

const toDateInput = (date) => {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

const today = computed(() => toDateInput(new Date()))

const errorDetail = (err, fallback) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d) => d.msg || String(d)).join('; ')
  }
  return fallback
}

const resetState = () => {
  form.supplier_name = ''
  form.quantity = shortage.value || 1
  form.unit_cost = ''
  form.expected_delivery_date = ''
  form.notes = ''
  Object.keys(errors).forEach((key) => delete errors[key])
  submitError.value = ''
  saving.value = false
  purchaseOrder.value = null
  loadError.value = ''
  loading.value = false
}

const loadPurchaseOrder = async () => {
  if (!props.backlogItem) return
  const itemId = props.backlogItem.id
  loading.value = true
  loadError.value = ''
  try {
    const po = await api.getPurchaseOrderByBacklogItem(itemId)
    if (props.backlogItem?.id === itemId && props.isOpen) purchaseOrder.value = po
  } catch (err) {
    console.error('Failed to load purchase order:', err)
    loadError.value = errorDetail(err, t('dashboard.purchaseOrder.loadError'))
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.isOpen, props.backlogItem?.id, props.mode],
  ([open]) => {
    resetState()
    if (open && props.backlogItem && props.mode === 'view') loadPurchaseOrder()
  },
  { immediate: true }
)

const validate = () => {
  Object.keys(errors).forEach((key) => delete errors[key])

  if (!form.supplier_name.trim()) {
    errors.supplier_name = t('dashboard.purchaseOrder.supplierRequired')
  }

  const quantity = Number(form.quantity)
  if (form.quantity === '' || !Number.isInteger(quantity) || quantity <= 0) {
    errors.quantity = t('dashboard.purchaseOrder.quantityInvalid')
  }

  const unitCost = Number(form.unit_cost)
  if (form.unit_cost === '' || !Number.isFinite(unitCost) || unitCost <= 0) {
    errors.unit_cost = t('dashboard.purchaseOrder.unitCostInvalid')
  }

  if (!form.expected_delivery_date) {
    errors.expected_delivery_date = t('dashboard.purchaseOrder.dateRequired')
  } else {
    const date = new Date(`${form.expected_delivery_date}T00:00:00`)
    if (isNaN(date.getTime())) {
      errors.expected_delivery_date = t('dashboard.purchaseOrder.dateInvalid')
    } else if (form.expected_delivery_date < today.value) {
      errors.expected_delivery_date = t('dashboard.purchaseOrder.datePast')
    }
  }

  return Object.keys(errors).length === 0
}

const submit = async () => {
  if (saving.value || !props.backlogItem) return
  submitError.value = ''
  if (!validate()) return

  saving.value = true
  try {
    const payload = {
      backlog_item_id: props.backlogItem.id,
      supplier_name: form.supplier_name.trim(),
      quantity: Number(form.quantity),
      unit_cost: Number(form.unit_cost),
      expected_delivery_date: form.expected_delivery_date
    }
    const notes = form.notes.trim()
    if (notes) payload.notes = notes

    const po = await api.createPurchaseOrder(payload)
    emit('po-created', po)
  } catch (err) {
    console.error('Failed to create purchase order:', err)
    submitError.value = errorDetail(err, t('dashboard.purchaseOrder.createError'))
  } finally {
    saving.value = false
  }
}

const close = () => {
  if (saving.value) return
  emit('close')
}

const formatMoney = (value) => {
  const amount = Number(value)
  if (!Number.isFinite(amount)) return 'N/A'
  return formatCurrency(amount, currentCurrency.value)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toLocaleDateString(currentLocale.value === 'ja' ? 'ja-JP' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: rgba(15, 23, 42, 0.45);
  z-index: 2000;
}

.modal-container {
  display: flex;
  flex-direction: column;
  width: min(600px, calc(100vw - 2rem));
  max-height: calc(100vh - 2rem);
  overflow: hidden;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-overlay);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-shrink: 0;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--color-text);
}

.close-button {
  display: inline-grid;
  place-items: center;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.close-button:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.modal-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: var(--space-6);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  flex-shrink: 0;
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
}

.item-header {
  padding-bottom: var(--space-5);
  margin-bottom: var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.item-name {
  margin-bottom: var(--space-2);
  font-size: var(--text-xl);
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--color-text);
}

.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.item-sku {
  font-family: 'Monaco', 'Courier New', monospace;
}

.item-shortage {
  color: var(--color-danger);
  font-weight: 500;
}

.info-grid,
.po-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-5);
}

.info-item,
.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 0;
}

.full {
  grid-column: 1 / -1;
}

.info-label,
.form-field label {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.info-value {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  overflow-wrap: anywhere;
}

.info-value.mono {
  font-family: 'Monaco', 'Courier New', monospace;
  color: var(--color-primary);
}

.info-value.notes {
  white-space: pre-wrap;
  font-weight: 400;
}

.form-field input,
.form-field textarea {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font: inherit;
  font-size: var(--text-sm);
  color: var(--color-text);
}

.form-field textarea {
  resize: vertical;
}

.form-field input:focus,
.form-field textarea:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -1px;
}

.form-field input.invalid {
  border-color: var(--color-danger);
}

.field-error {
  font-size: var(--text-xs);
  color: var(--color-danger);
}

.form-error {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-danger-soft);
  font-size: var(--text-sm);
  color: var(--color-danger);
}

.state-message {
  padding: var(--space-6) 0;
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 520px) {
  .info-grid,
  .po-form {
    grid-template-columns: minmax(0, 1fr);
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform var(--transition-base);
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
