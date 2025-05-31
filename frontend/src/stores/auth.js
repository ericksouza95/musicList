import { defineStore } from 'pinia'
import { authAPI, usersAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refreshToken'),
    isLoading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.is_admin || false,
    fullName: (state) => state.user ? `${state.user.first_name} ${state.user.last_name}` : '',
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      try {
        const response = await authAPI.login(credentials)
        const { user, access_token, refresh_token } = response.data

        this.user = user
        this.token = access_token
        this.refreshToken = refresh_token

        // Salvar no localStorage
        localStorage.setItem('token', access_token)
        if (refresh_token) {
          localStorage.setItem('refreshToken', refresh_token)
        }

        toast.success(`Bem-vindo, ${user.first_name}!`)
        return response.data
      } catch (error) {
        this.logout()
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      try {
        const response = await authAPI.register(userData)
        const { user, access_token, refresh_token } = response.data

        this.user = user
        this.token = access_token
        this.refreshToken = refresh_token

        // Salvar no localStorage
        localStorage.setItem('token', access_token)
        if (refresh_token) {
          localStorage.setItem('refreshToken', refresh_token)
        }

        toast.success(`Conta criada com sucesso! Bem-vindo, ${user.first_name}!`)
        return response.data
      } catch (error) {
        this.logout()
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
        if (this.token) {
          await authAPI.logout()
        }
      } catch (error) {
        console.error('Erro ao fazer logout:', error)
      } finally {
        // Limpar estado
        this.user = null
        this.token = null
        this.refreshToken = null

        // Limpar localStorage
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')

        toast.info('Logout realizado com sucesso')
      }
    },

    async getCurrentUser() {
      if (!this.token) {
        throw new Error('Token não encontrado')
      }

      try {
        const response = await authAPI.getCurrentUser()
        this.user = response.data.user
        return response.data.user
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        this.logout()
        throw new Error('Refresh token não encontrado')
      }

      try {
        const response = await authAPI.refreshToken()
        const { access_token, user } = response.data

        this.token = access_token
        this.user = user

        localStorage.setItem('token', access_token)
        return access_token
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async changePassword(passwords) {
      this.isLoading = true
      try {
        await authAPI.changePassword(passwords)
        toast.success('Senha alterada com sucesso!')
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateProfile(userData) {
      this.isLoading = true
      try {
        const response = await usersAPI.updateUser(this.user.id, userData)
        this.user = response.data.user
        toast.success('Perfil atualizado com sucesso!')
        return response.data.user
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // Inicializar store (verificar se há token válido)
    async initialize() {
      if (this.token && !this.user) {
        try {
          await this.getCurrentUser()
        } catch (error) {
          this.logout()
        }
      }
    },
  },
}) 