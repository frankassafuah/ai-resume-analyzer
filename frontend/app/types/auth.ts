export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  profile_image: string | null
  email_verified: boolean
  created_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginResponse extends AuthTokens {
  user: User
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  first_name?: string
  last_name?: string
}

export interface ProfileUpdatePayload {
  first_name?: string
  last_name?: string
  profile_image?: File
}
