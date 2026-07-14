import { defineStore } from 'pinia'

import { notificationService } from '~/services/notification.service'
import type { AppNotification } from '~/types'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    items: [] as AppNotification[],
    loading: false,
  }),

  getters: {
    unreadCount: (s): number => s.items.filter((n) => !n.is_read).length,
  },

  actions: {
    async fetch() {
      this.loading = true
      try {
        const page = await notificationService.list()
        this.items = page.results
      } finally {
        this.loading = false
      }
    },

    async markRead(id: string) {
      const updated = await notificationService.markRead(id)
      const i = this.items.findIndex((n) => n.id === id)
      if (i !== -1) this.items[i] = updated
    },

    async markAllRead() {
      await notificationService.markAllRead()
      this.items = this.items.map((n) => ({ ...n, is_read: true }))
    },
  },
})
