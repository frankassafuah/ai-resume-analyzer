export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface AnalysisResult {
  score: number
  ats_score: number
  matching_skills: string[]
  missing_skills: string[]
  keywords: string[]
  strengths: string[]
  weaknesses: string[]
  summary: string
  recommendations: string[]
}

export interface Analysis {
  id: string
  status: AnalysisStatus
  score: number | null
  ats_score: number | null
  provider: string
  model: string
  result_json: AnalysisResult | null
  error: string
  resume: string | null
  job: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface CreateAnalysisPayload {
  resume_id: string
  job_id: string
}
