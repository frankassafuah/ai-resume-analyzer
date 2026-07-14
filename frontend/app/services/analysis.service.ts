import { apiGet, apiGetPage, apiPost } from '~/services/http'
import type { Analysis, CreateAnalysisPayload, Page } from '~/types'

export const analysisService = {
  list(params?: Record<string, string | number>): Promise<Page<Analysis>> {
    return apiGetPage<Analysis>('analysis/', params)
  },

  get(id: string): Promise<Analysis> {
    return apiGet<Analysis>(`analysis/${id}/`)
  },

  create(payload: CreateAnalysisPayload): Promise<Analysis> {
    return apiPost<Analysis>('analysis/', payload)
  },
}
