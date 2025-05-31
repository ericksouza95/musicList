import { defineStore } from 'pinia'
import { ref } from 'vue'
import { musicAPI } from '@/services/api'

export const useMusicStore = defineStore('music', () => {
  const currentMusic = ref(null)
  const musics = ref([])
  const loading = ref(false)
  const searchResults = ref([])

  const playMusic = (music) => {
    currentMusic.value = music
  }

  const playPrevious = () => {
    if (!currentMusic.value || musics.value.length === 0) return
    
    const currentIndex = musics.value.findIndex(m => m.id === currentMusic.value.id)
    const previousIndex = currentIndex > 0 ? currentIndex - 1 : musics.value.length - 1
    currentMusic.value = musics.value[previousIndex]
  }

  const playNext = () => {
    if (!currentMusic.value || musics.value.length === 0) return
    
    const currentIndex = musics.value.findIndex(m => m.id === currentMusic.value.id)
    const nextIndex = currentIndex < musics.value.length - 1 ? currentIndex + 1 : 0
    currentMusic.value = musics.value[nextIndex]
  }

  const fetchMusics = async () => {
    loading.value = true
    try {
      const response = await musicAPI.getMusic()
      const data = response.data
      musics.value = data.music || data.items || []
      return data
    } catch (error) {
      console.error('Erro ao carregar músicas:', error)
      // Dados mockados em caso de erro
      const mockMusics = [
        {
          id: 1,
          title: 'Shape of You',
          artist: 'Ed Sheeran',
          album: '÷ (Divide)',
          genre: 'Pop',
          year: 2017,
          duration: 233,
          artwork_url: 'https://via.placeholder.com/300x300/1976d2/white?text=🎵',
          file_url: '#',
          is_favorite: false,
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          title: 'Blinding Lights',
          artist: 'The Weeknd',
          album: 'After Hours',
          genre: 'Synthpop',
          year: 2020,
          duration: 200,
          artwork_url: 'https://via.placeholder.com/300x300/9c27b0/white?text=🎶',
          file_url: '#',
          is_favorite: true,
          created_at: new Date().toISOString()
        },
        {
          id: 3,
          title: 'Watermelon Sugar',
          artist: 'Harry Styles',
          album: 'Fine Line',
          genre: 'Pop Rock',
          year: 2020,
          duration: 174,
          artwork_url: 'https://via.placeholder.com/300x300/4caf50/white?text=🍉',
          file_url: '#',
          is_favorite: false,
          created_at: new Date().toISOString()
        }
      ]
      musics.value = mockMusics
      return { music: mockMusics }
    } finally {
      loading.value = false
    }
  }

  const searchMusics = async (query) => {
    if (!query?.trim()) {
      searchResults.value = []
      return
    }

    loading.value = true
    try {
      const response = await musicAPI.searchMusic({ q: query })
      const data = response.data
      searchResults.value = data.results || data.music || []
    } catch (error) {
      console.error('Erro na busca:', error)
      // Resultados mockados para demonstração
      const mockResults = [
        {
          id: 'search-1',
          title: `Resultado para: ${query}`,
          artist: 'Artista Encontrado',
          album: 'Album Encontrado',
          genre: 'Pop',
          year: 2024,
          artwork_url: `https://via.placeholder.com/300x300/2196f3/white?text=${query.charAt(0).toUpperCase()}`,
          source: 'external'
        },
        {
          id: 'search-2',
          title: `${query} - Extended Version`,
          artist: 'Outro Artista',
          album: 'Single',
          genre: 'Rock',
          year: 2023,
          artwork_url: `https://via.placeholder.com/300x300/ff9800/white?text=${query.charAt(0).toUpperCase()}`,
          source: 'external'
        }
      ]
      searchResults.value = mockResults
    } finally {
      loading.value = false
    }
  }

  const toggleFavorite = async (musicId) => {
    try {
      // Simular sucesso para demonstração
      const music = musics.value.find(m => m.id === musicId)
      if (music) {
        music.is_favorite = !music.is_favorite
      }
      return true
    } catch (error) {
      console.error('Erro ao alterar favorito:', error)
      return false
    }
  }

  const deleteMusic = async (musicId) => {
    try {
      await musicAPI.deleteMusic(musicId)
      // Remover da lista local
      musics.value = musics.value.filter(m => m.id !== musicId)
      return true
    } catch (error) {
      console.error('Erro ao excluir música:', error)
      throw error
    }
  }

  const uploadMusic = async (formData) => {
    try {
      const response = await musicAPI.uploadMusic(formData)
      const data = response.data
      // Adicionar à lista local
      if (data.music) {
        musics.value.unshift(data.music)
      }
      return data
    } catch (error) {
      console.error('Erro no upload:', error)
      throw error
    }
  }

  const addToLibrary = async (externalMusic) => {
    try {
      const response = await musicAPI.importFromSpotify(externalMusic)
      const data = response.data
      if (data.music) {
        musics.value.unshift(data.music)
      }
      return data
    } catch (error) {
      console.error('Erro ao adicionar à biblioteca:', error)
      throw error
    }
  }

  return {
    currentMusic,
    musics,
    loading,
    searchResults,
    playMusic,
    playPrevious,
    playNext,
    fetchMusics,
    searchMusics,
    toggleFavorite,
    deleteMusic,
    uploadMusic,
    addToLibrary
  }
}) 