export type EmploymentType =
  | 'full_time'
  | 'part_time'
  | 'contract'
  | 'internship'
  | 'temporary'
  | 'freelance'

export interface JobDescription {
  id: string
  company_name: string
  job_title: string
  description: string
  required_skills: string[]
  location: string
  employment_type: EmploymentType
  employment_type_display: string
  is_archived: boolean
  archived_at: string | null
  created_at: string
  updated_at: string
}

export interface JobDescriptionPayload {
  company_name: string
  job_title: string
  description: string
  required_skills?: string[]
  location?: string
  employment_type?: EmploymentType
}
