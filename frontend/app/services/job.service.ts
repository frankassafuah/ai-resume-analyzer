import { apiDelete, apiGet, apiGetPage, apiPatch, apiPost } from '~/services/http'
import type { JobDescription, JobDescriptionPayload, Page } from '~/types'

export const jobService = {
  list(params?: Record<string, string | number | boolean>): Promise<Page<JobDescription>> {
    return apiGetPage<JobDescription>('jobs/', params)
  },

  get(id: string): Promise<JobDescription> {
    return apiGet<JobDescription>(`jobs/${id}/`)
  },

  create(payload: JobDescriptionPayload): Promise<JobDescription> {
    return apiPost<JobDescription>('jobs/', payload)
  },

  update(id: string, payload: Partial<JobDescriptionPayload>): Promise<JobDescription> {
    return apiPatch<JobDescription>(`jobs/${id}/`, payload)
  },

  remove(id: string): Promise<void> {
    return apiDelete(`jobs/${id}/`)
  },

  archive(id: string): Promise<JobDescription> {
    return apiPost<JobDescription>(`jobs/${id}/archive/`)
  },

  unarchive(id: string): Promise<JobDescription> {
    return apiPost<JobDescription>(`jobs/${id}/unarchive/`)
  },
}
