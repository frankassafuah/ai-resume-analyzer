import ky, { HTTPError, type KyInstance, type Options } from 'ky'

import { ApiError, type ApiErrorBody, type ApiSuccess, type Page } from '~/types'

function baseUrl(): string {
  // Trailing slash so relative inputs ("resumes/") resolve correctly.
  return `${useRuntimeConfig().public.apiBase}/api/v1/`
}

/** Bare client for auth-token endpoints — no refresh interceptor, so a 401 on
 *  login/refresh never recurses. */
export function rawApi(): KyInstance {
  return ky.create({ prefixUrl: baseUrl(), retry: 0 })
}

// Coalesce concurrent 401s into a single refresh call.
let refreshing: Promise<boolean> | null = null

/** Authenticated client: injects the access token, and on a 401 refreshes once
 *  and retries the original request. */
export function api(): KyInstance {
  const auth = useAuthStore()
  return ky.create({
    prefixUrl: baseUrl(),
    retry: 0,
    hooks: {
      beforeRequest: [
        (req) => {
          if (auth.accessToken) {
            req.headers.set('Authorization', `Bearer ${auth.accessToken}`)
          }
        },
      ],
      afterResponse: [
        async (req, options, res) => {
          if (res.status !== 401 || req.headers.get('x-retried')) return res
          refreshing ??= auth.refreshTokens().finally(() => (refreshing = null))
          const ok = await refreshing
          if (!ok) {
            await auth.logout({ redirect: true })
            return res
          }
          req.headers.set('Authorization', `Bearer ${auth.accessToken}`)
          req.headers.set('x-retried', '1')
          return ky(req, options)
        },
      ],
    },
  })
}

async function normalizeError(err: unknown): Promise<ApiError> {
  if (err instanceof ApiError) return err
  if (err instanceof HTTPError) {
    const status = err.response.status
    try {
      const body = (await err.response.json()) as ApiErrorBody
      if (body?.error) {
        return new ApiError(body.error.message, body.error.code, status, body.error.details)
      }
    } catch {
      /* non-JSON error body */
    }
    return new ApiError(err.message || 'Request failed', 'http_error', status)
  }
  return new ApiError((err as Error)?.message || 'Network error', 'network_error', 0)
}

async function envelope<T>(run: () => Promise<Response>): Promise<ApiSuccess<T>> {
  try {
    const res = await run()
    return (await res.json()) as ApiSuccess<T>
  } catch (err) {
    throw await normalizeError(err)
  }
}

// --- typed helpers used by the domain services ---------------------------
export async function apiGet<T>(url: string, searchParams?: Options['searchParams']): Promise<T> {
  return (await envelope<T>(() => api().get(url, { searchParams }))).data
}

export async function apiGetPage<T>(
  url: string,
  searchParams?: Options['searchParams'],
): Promise<Page<T>> {
  const body = await envelope<T[]>(() => api().get(url, { searchParams }))
  return { results: body.data, pagination: body.meta?.pagination }
}

export async function apiPost<T>(url: string, json?: unknown): Promise<T> {
  return (await envelope<T>(() => api().post(url, json === undefined ? undefined : { json }))).data
}

export async function apiPatch<T>(url: string, json: unknown): Promise<T> {
  return (await envelope<T>(() => api().patch(url, { json }))).data
}

export async function apiPostForm<T>(url: string, form: FormData): Promise<T> {
  return (await envelope<T>(() => api().post(url, { body: form }))).data
}

export async function apiDelete(url: string): Promise<void> {
  try {
    await api().delete(url)
  } catch (err) {
    throw await normalizeError(err)
  }
}

export async function apiDownload(url: string): Promise<Blob> {
  try {
    return await api().get(url).blob()
  } catch (err) {
    throw await normalizeError(err)
  }
}
