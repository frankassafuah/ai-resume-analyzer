import { apiGetPage, apiPost } from '~/services/http'
import type { AppNotification, Page } from '~/types'

export const notificationService = {
  list(params?: Record<string, string | number | boolean>): Promise<Page<AppNotification>> {
    return apiGetPage<AppNotification>('notifications/', params)
  },

  markRead(id: string): Promise<AppNotification> {
    return apiPost<AppNotification>(`notifications/${id}/read/`)
  },

  markAllRead(): Promise<{ marked_read: number }> {
    return apiPost<{ marked_read: number }>('notifications/read-all/')
  },
}
