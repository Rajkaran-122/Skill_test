import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  token: string | null
  login: (password: string, username?: string) => Promise<boolean>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: localStorage.getItem('isAuthenticated') === 'true',
  token: localStorage.getItem('access_token'),
  
  login: async (password: string, username = 'admin') => {
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch('/api/v1/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('isAuthenticated', 'true')
        localStorage.setItem('access_token', data.access_token)
        set({ isAuthenticated: true, token: data.access_token })
        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  },
  
  logout: () => {
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('access_token')
    set({ isAuthenticated: false, token: null })
  }
}))
