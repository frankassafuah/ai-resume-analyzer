import { defineStore } from 'pinia'

import { authService } from '~/services/auth.service'
import type { LoginPayload, ProfileUpdatePayload, RegisterPayload, User } from '~/types'

const ACCESS_KEY = 'ara.access'
const REFRESH_KEY = 'ara.refresh'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  initialized: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (s): boolean => !!s.accessToken,
    initials: (s): string => {
      if (!s.user) return '?'
      const { first_name, last_name, email } = s.user
      const a = first_name?.[0] ?? email[0]
      const b = last_name?.[0] ?? ''
      return (a + b).toUpperCase()
    },
  },

  actions: {
    _persist() {
      if (import.meta.client) {
        if (this.accessToken) {
          localStorage.setItem(ACCESS_KEY, this.accessToken)
        } else {
          localStorage.removeItem(ACCESS_KEY)
        }
        if (this.refreshToken) {
          localStorage.setItem(REFRESH_KEY, this.refreshToken)
        } else {
          localStorage.removeItem(REFRESH_KEY)
        }
      }
    },

    _setTokens(access: string | null, refresh: string | null) {
      this.accessToken = access
      this.refreshToken = refresh
      this._persist()
    },

    /** Restore tokens from storage and fetch the current user (app startup). */
    async init() {
      if (this.initialized) return
      if (import.meta.client) {
        this.accessToken = localStorage.getItem(ACCESS_KEY)
        this.refreshToken = localStorage.getItem(REFRESH_KEY)
      }
      if (this.accessToken) {
        try {
          this.user = await authService.me()
        } catch {
          await this.logout()
        }
      }
      this.initialized = true
    },

    async login(payload: LoginPayload) {
      const { access, refresh, user } = await authService.login(payload)
      this._setTokens(access, refresh)
      this.user = user
    },

    async register(payload: RegisterPayload) {
      await authService.register(payload)
      await this.login({ email: payload.email, password: payload.password })
    },

    /** Returns true if a fresh access token was obtained. */
    async refreshTokens(): Promise<boolean> {
      if (!this.refreshToken) return false
      try {
        const { access, refresh } = await authService.refresh(this.refreshToken)
        this._setTokens(access, refresh ?? this.refreshToken)
        return true
      } catch {
        return false
      }
    },

    async fetchMe() {
      this.user = await authService.me()
    },

    async updateProfile(payload: ProfileUpdatePayload) {
      this.user = await authService.updateProfile(payload)
    },

    async logout(opts: { redirect?: boolean } = {}) {
      const token = this.refreshToken
      this._setTokens(null, null)
      this.user = null
      if (token) authService.logout(token).catch(() => {})
      if (opts.redirect && import.meta.client) await navigateTo('/login')
    },
  },
})
