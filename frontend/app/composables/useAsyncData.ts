import { onMounted, ref, shallowRef } from 'vue'

import { ApiError } from '~/types'

/**
 * Fetch-on-mount helper with loading/error/data state for list & detail views.
 * (Named useLoader to avoid clashing with Nuxt's built-in useAsyncData.)
 *
 *   const { data, pending, error, refresh } = useLoader(() => resumeService.list())
 */
export function useLoader<T>(fetcher: () => Promise<T>, options: { immediate?: boolean } = {}) {
  const data = shallowRef<T | null>(null)
  const pending = ref(false)
  const error = shallowRef<ApiError | null>(null)

  async function refresh() {
    pending.value = true
    error.value = null
    try {
      data.value = await fetcher()
    } catch (e) {
      error.value = e instanceof ApiError ? e : new ApiError((e as Error).message)
    } finally {
      pending.value = false
    }
  }

  if (options.immediate !== false) onMounted(refresh)

  return { data, pending, error, refresh }
}
