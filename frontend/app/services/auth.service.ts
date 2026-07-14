import { apiGet, apiPatch, apiPost, apiPostForm, rawApi } from '~/services/http'
import type {
  ApiSuccess,
  AuthTokens,
  LoginPayload,
  LoginResponse,
  ProfileUpdatePayload,
  RegisterPayload,
  User,
} from '~/types'

export const authService = {
  register(payload: RegisterPayload): Promise<User> {
    return apiPost<User>('accounts/auth/register/', payload)
  },

  async login(payload: LoginPayload): Promise<LoginResponse> {
    // Uses the bare client (no refresh interceptor).
    const body = await rawApi()
      .post('accounts/auth/login/', { json: payload })
      .json<ApiSuccess<LoginResponse>>()
    return body.data
  },

  async refresh(refreshToken: string): Promise<AuthTokens> {
    const body = await rawApi()
      .post('accounts/auth/refresh/', { json: { refresh: refreshToken } })
      .json<ApiSuccess<AuthTokens>>()
    return body.data
  },

  logout(refreshToken: string): Promise<unknown> {
    return apiPost('accounts/auth/logout/', { refresh: refreshToken })
  },

  me(): Promise<User> {
    return apiGet<User>('accounts/profile/')
  },

  updateProfile(payload: ProfileUpdatePayload): Promise<User> {
    if (payload.profile_image) {
      const form = new FormData()
      if (payload.first_name !== undefined) form.append('first_name', payload.first_name)
      if (payload.last_name !== undefined) form.append('last_name', payload.last_name)
      form.append('profile_image', payload.profile_image)
      return apiPostForm<User>('accounts/profile/', form)
    }
    return apiPatch<User>('accounts/profile/', payload)
  },

  forgotPassword(email: string): Promise<unknown> {
    return apiPost('accounts/auth/password/forgot/', { email })
  },

  resetPassword(uid: string, token: string, password: string): Promise<unknown> {
    return apiPost('accounts/auth/password/reset/', { uid, token, password })
  },
}
