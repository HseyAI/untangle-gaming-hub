import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '../services/api'
import type { User, LoginCredentials } from '../types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token')
    if (token) {
      authApi
        .getMe()
        .then((userData) => setUser(userData))
        .catch((error) => {
          // Clear invalid tokens
          console.log('Auto-login failed, clearing tokens:', error.message)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          setUser(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (credentials: LoginCredentials) => {
    const tokens = await authApi.login(credentials)
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)

    const userData = await authApi.getMe()
    setUser(userData)
  }

  const logout = async () => {
    await authApi.logout()
    setUser(null)
  }

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
