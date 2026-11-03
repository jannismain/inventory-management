import { computed } from 'vue'
import { useRoute } from 'vue-router'

const ALL = ['period', 'location', 'category', 'status']

// Mirrors which filters each view actually applies (see the view's data loading
// and the matching API endpoint). Update when a view starts honoring a filter.
const ROUTE_FILTERS = {
  '/': ALL,
  '/orders': ALL,
  '/inventory': ['location', 'category'],
  '/demand': ['location', 'category'],
  '/spending': ['period'],
  '/restocking': [],
  '/reports': []
}

export function useFilterScope() {
  const route = useRoute()

  const applicable = computed(() => ROUTE_FILTERS[route.path] ?? ALL)

  const isApplicable = (name) => applicable.value.includes(name)

  return { isApplicable }
}
