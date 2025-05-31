import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlaylistStore = defineStore('playlists', () => {
  const playlists = ref([])
  const currentPlaylist = ref(null)
  const loading = ref(false)

  const fetchPlaylists = async () => {
    loading.value = true
    try {
      // Implementar busca de playlists
      return { playlists: [] }
    } finally {
      loading.value = false
    }
  }

  const createPlaylist = async (playlistData) => {
    // Implementar criação de playlist
    console.log('Criar playlist:', playlistData)
  }

  const deletePlaylist = async (playlistId) => {
    // Implementar exclusão de playlist
    console.log('Excluir playlist:', playlistId)
  }

  return {
    playlists,
    currentPlaylist,
    loading,
    fetchPlaylists,
    createPlaylist,
    deletePlaylist
  }
}) 