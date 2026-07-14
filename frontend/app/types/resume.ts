export type ParseStatus = 'pending' | 'parsing' | 'parsed' | 'failed'

export interface ResumeVersion {
  id: string
  version: number
  original_filename: string
  file_type: 'pdf' | 'docx'
  size_bytes: number
  parse_status: ParseStatus
  parse_error: string
  parsed_json: { raw_text?: string; char_count?: number } | null
  created_at: string
  download_url: string | null
}

export interface Resume {
  id: string
  title: string
  status: ParseStatus | 'empty'
  current_version: ResumeVersion | null
  versions_count: number
  created_at: string
  updated_at: string
}
