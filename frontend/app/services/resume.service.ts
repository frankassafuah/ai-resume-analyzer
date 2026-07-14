import { apiDelete, apiDownload, apiGet, apiGetPage, apiPostForm } from '~/services/http'
import type { Page, Resume, ResumeVersion } from '~/types'

export const resumeService = {
  list(params?: Record<string, string | number>): Promise<Page<Resume>> {
    return apiGetPage<Resume>('resumes/', params)
  },

  get(id: string): Promise<Resume> {
    return apiGet<Resume>(`resumes/${id}/`)
  },

  upload(file: File, title?: string): Promise<Resume> {
    const form = new FormData()
    form.append('file', file)
    if (title) form.append('title', title)
    return apiPostForm<Resume>('resumes/', form)
  },

  addVersion(id: string, file: File): Promise<ResumeVersion> {
    const form = new FormData()
    form.append('file', file)
    return apiPostForm<ResumeVersion>(`resumes/${id}/versions/`, form)
  },

  versions(id: string): Promise<ResumeVersion[]> {
    return apiGet<ResumeVersion[]>(`resumes/${id}/versions/`)
  },

  remove(id: string): Promise<void> {
    return apiDelete(`resumes/${id}/`)
  },

  download(id: string): Promise<Blob> {
    return apiDownload(`resumes/${id}/download/`)
  },
}
