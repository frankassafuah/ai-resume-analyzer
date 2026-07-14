// Shapes mirroring the backend's standard response envelope.

export interface Pagination {
  count: number
  page: number
  pages: number
  page_size: number
  next: string | null
  previous: string | null
}

export interface ApiSuccess<T> {
  success: true
  data: T
  meta?: { pagination?: Pagination }
}

export interface ApiErrorBody {
  success: false
  error: {
    code: string
    message: string
    details?: unknown
  }
}

/** A page of results plus its pagination metadata. */
export interface Page<T> {
  results: T[]
  pagination?: Pagination
}

/** Normalized error thrown by the API client (see services/http.ts). */
export class ApiError extends Error {
  code: string
  status: number
  details?: unknown

  constructor(message: string, code = 'error', status = 0, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }

  /** Field-level validation errors, if the backend returned any. */
  get fieldErrors(): Record<string, string[]> {
    return (this.details && typeof this.details === 'object'
      ? (this.details as Record<string, string[]>)
      : {})
  }
}
