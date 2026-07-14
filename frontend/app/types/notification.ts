export type NotificationType =
  | 'analysis_complete'
  | 'analysis_failed'
  | 'system'

export interface AppNotification {
  id: string
  type: NotificationType
  title: string
  message: string
  data: Record<string, unknown>
  is_read: boolean
  created_at: string
}
