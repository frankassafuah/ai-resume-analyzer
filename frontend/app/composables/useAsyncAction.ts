import { ref, shallowRef } from 'vue'

import { ApiError } from '~/types'

/**
 * Wraps an async operation with reactive loading/error state and toast-friendly
 * error normalization. Use for imperative actions (submit, delete, upload):
 *
 *   const { run, pending, error } = useAsyncAction(authService.login)
 *   await run({ email, password })
 */
export function useAsyncAction<Args extends unknown[], Result>(
  fn: (...args: Args) => Promise<Result>,
  options: { onError?: (e: ApiError) => void; toastOnError?: boolean } = {},
) {
  const pending = ref(false)
  const error = shallowRef<ApiError | null>(null)

  async function run(...args: Args): Promise<Result | undefined> {
    pending.value = true
    error.value = null
    try {
      return await fn(...args)
    } catch (e) {
      const apiError = e instanceof ApiError ? e : new ApiError((e as Error).message)
      error.value = apiError
      options.onError?.(apiError)
      if (options.toastOnError !== false) useToast().error(apiError.message)
      return undefined
    } finally {
      pending.value = false
    }
  }

  return { run, pending, error }
}
