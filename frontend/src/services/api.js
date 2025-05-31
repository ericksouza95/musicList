import axios from 'axios'

// Configuração base do Axios
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptador de requisição para adicionar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptador de resposta para tratar erros
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// Serviços de API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  refreshToken: () => api.post('/auth/refresh'),
  changePassword: (passwords) => api.post('/auth/change-password', passwords),
}

export const usersAPI = {
  getUsers: (params) => api.get('/users', { params }),
  getUser: (id) => api.get(`/users/${id}`),
  updateUser: (id, userData) => api.put(`/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/users/${id}`),
  getUserPlaylists: (id, params) => api.get(`/users/${id}/playlists`, { params }),
  getUserUploads: (id, params) => api.get(`/users/${id}/uploads`, { params }),
}

export const musicAPI = {
  getMusic: (params) => api.get('/music', { params }),
  getMusicById: (id) => api.get(`/music/${id}`),
  updateMusic: (id, musicData) => api.put(`/music/${id}`, musicData),
  deleteMusic: (id) => api.delete(`/music/${id}`),
  searchMusic: (params) => api.get('/music/search', { params }),
  importFromSpotify: (spotifyData) => api.post('/music/import', spotifyData),
  uploadMusic: (formData) => api.post('/music/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  streamMusic: (id) => api.get(`/music/${id}/stream`, {
    responseType: 'blob',
  }),
  incrementPlayCount: (id) => api.post(`/music/${id}/play`),
}

export const playlistsAPI = {
  getPlaylists: (params) => api.get('/playlists', { params }),
  getPlaylist: (id, params) => api.get(`/playlists/${id}`, { params }),
  createPlaylist: (playlistData) => api.post('/playlists', playlistData),
  updatePlaylist: (id, playlistData) => api.put(`/playlists/${id}`, playlistData),
  deletePlaylist: (id) => api.delete(`/playlists/${id}`),
  getPlaylistTracks: (id, params) => api.get(`/playlists/${id}/tracks`, { params }),
  addTrackToPlaylist: (id, trackData) => api.post(`/playlists/${id}/tracks`, trackData),
  removeTrackFromPlaylist: (playlistId, musicId) => api.delete(`/playlists/${playlistId}/tracks/${musicId}`),
  reorderPlaylistTracks: (id, orderData) => api.post(`/playlists/${id}/tracks/reorder`, orderData),
  incrementPlayCount: (id) => api.post(`/playlists/${id}/play`),
  duplicatePlaylist: (id, duplicateData) => api.post(`/playlists/${id}/duplicate`, duplicateData),
  refreshDuration: (id) => api.post(`/playlists/${id}/refresh-duration`),
}

export default api 