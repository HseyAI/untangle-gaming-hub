import axios, { AxiosError, AxiosResponse } from 'axios'
import type {
  LoginCredentials,
  TokenResponse,
  User,
  Member,
  MemberCreate,
  Purchase,
  PurchaseCreate,
  GamingSession,
  SessionStart,
  DashboardStats,
  RevenueStats,
} from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token: new_refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', new_refresh_token)

          // Retry original request
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`
            return axios(error.config)
          }
        } catch {
          // Refresh failed, logout
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    // OAuth2PasswordRequestForm expects form data
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response: AxiosResponse<TokenResponse> = await axios.post(
      `${API_URL}/auth/login`,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    )
    return response.data
  },

  getMe: async (): Promise<User> => {
    const response: AxiosResponse<User> = await apiClient.get('/auth/me')
    return response.data
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken })
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}

// Members API
export const membersApi = {
  list: async (params?: { search?: string; page?: number; page_size?: number }) => {
    const response = await apiClient.get('/members/', { params })
    return response.data
  },

  get: async (id: string): Promise<Member> => {
    const response: AxiosResponse<Member> = await apiClient.get(`/members/${id}`)
    return response.data
  },

  create: async (data: MemberCreate): Promise<Member> => {
    const response: AxiosResponse<Member> = await apiClient.post('/members/', data)
    return response.data
  },

  update: async (id: string, data: Partial<MemberCreate>): Promise<Member> => {
    const response: AxiosResponse<Member> = await apiClient.put(`/members/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/members/${id}`)
  },

  searchByMobile: async (mobile: string): Promise<Member> => {
    const response: AxiosResponse<Member> = await apiClient.get(`/members/mobile/${mobile}`)
    return response.data
  },
}

// Purchases API
export const purchasesApi = {
  list: async (params?: { member_id?: string; page?: number; page_size?: number }) => {
    const response = await apiClient.get('/purchases/', { params })
    return response.data
  },

  get: async (id: string): Promise<Purchase> => {
    const response: AxiosResponse<Purchase> = await apiClient.get(`/purchases/${id}`)
    return response.data
  },

  create: async (data: PurchaseCreate): Promise<Purchase> => {
    const response: AxiosResponse<Purchase> = await apiClient.post('/purchases/', data)
    return response.data
  },

  getMemberHistory: async (memberId: string) => {
    const response = await apiClient.get(`/purchases/member/${memberId}/history`)
    return response.data
  },
}

// Sessions API
export const sessionsApi = {
  list: async (params?: { member_id?: string; active_only?: boolean; page?: number }) => {
    const response = await apiClient.get('/sessions/', { params })
    return response.data
  },

  get: async (id: string): Promise<GamingSession> => {
    const response: AxiosResponse<GamingSession> = await apiClient.get(`/sessions/${id}`)
    return response.data
  },

  start: async (data: SessionStart): Promise<GamingSession> => {
    const response: AxiosResponse<GamingSession> = await apiClient.post('/sessions/start', data)
    return response.data
  },

  end: async (id: string, manual_hours?: number): Promise<GamingSession> => {
    const response: AxiosResponse<GamingSession> = await apiClient.put(
      `/sessions/${id}/end`,
      { manual_hours }
    )
    return response.data
  },

  getActive: async (): Promise<GamingSession[]> => {
    const response: AxiosResponse<GamingSession[]> = await apiClient.get('/sessions/active')
    return response.data
  },

  getMemberSessions: async (memberId: string, params?: { page?: number }) => {
    const response = await apiClient.get(`/sessions/member/${memberId}`, { params })
    return response.data
  },
}

// Dashboard API
export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const response: AxiosResponse<DashboardStats> = await apiClient.get('/dashboard/stats')
    return response.data
  },

  getRevenue: async (): Promise<RevenueStats> => {
    const response: AxiosResponse<RevenueStats> = await apiClient.get('/dashboard/revenue')
    return response.data
  },

  getExpiringMembers: async (days: number = 30) => {
    const response = await apiClient.get('/dashboard/members/expiring', { params: { days } })
    return response.data
  },

  exportData: async (format: 'csv' | 'json' = 'csv') => {
    const response = await apiClient.get(`/dashboard/export/${format}`, {
      responseType: 'blob',
    })
    return response.data
  },
}

export default apiClient
