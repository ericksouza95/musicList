<template>
  <v-container class="pa-6">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4 font-weight-bold">
        <v-icon class="mr-2">mdi-music</v-icon>
        Suas Músicas
      </h1>
      <v-spacer />
      <v-btn
        color="primary"
        @click="$router.push('/music/upload')"
      >
        <v-icon start>mdi-upload</v-icon>
        Upload de Música
      </v-btn>
    </div>

    <!-- Filtros e busca -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Buscar músicas"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              clearable
              @input="searchMusics"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.genre"
              :items="genres"
              label="Gênero"
              variant="outlined"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.sortBy"
              :items="sortOptions"
              label="Ordenar por"
              variant="outlined"
              @update:model-value="applyFilters"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              block
              color="secondary"
              @click="clearFilters"
            >
              Limpar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Lista de músicas -->
    <v-card>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="musics"
          :loading="loading"
          :search="search"
          item-value="id"
        >
          <template #item.artwork_url="{ item }">
            <v-avatar size="40" class="my-2">
              <v-img
                v-if="item.artwork_url"
                :src="item.artwork_url"
                :alt="item.title"
              />
              <v-icon v-else>mdi-music</v-icon>
            </v-avatar>
          </template>

          <template #item.title="{ item }">
            <div>
              <div class="font-weight-medium">{{ item.title }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.artist }}</div>
            </div>
          </template>

          <template #item.duration="{ item }">
            {{ formatDuration(item.duration) }}
          </template>

          <template #item.created_at="{ item }">
            {{ formatDate(item.created_at) }}
          </template>

          <template #item.actions="{ item }">
            <v-btn
              icon="mdi-play"
              variant="text"
              size="small"
              @click="playMusic(item)"
            />
            <v-btn
              icon="mdi-heart"
              variant="text"
              size="small"
              :color="item.is_favorite ? 'red' : 'default'"
              @click="toggleFavorite(item)"
            />
            <v-btn
              icon="mdi-playlist-plus"
              variant="text"
              size="small"
              @click="showAddToPlaylist(item)"
            />
            <v-btn
              icon="mdi-download"
              variant="text"
              size="small"
              @click="downloadMusic(item)"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
              @click="confirmDelete(item)"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Dialog de confirmação de exclusão -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>Confirmar Exclusão</v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir a música "{{ selectedMusic?.title }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" @click="deleteMusic">Excluir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMusicStore } from '@/stores/music'

const musicStore = useMusicStore()

const search = ref('')
const loading = ref(false)
const deleteDialog = ref(false)
const selectedMusic = ref(null)

const filters = ref({
  genre: null,
  sortBy: 'created_at'
})

const musics = ref([])
const genres = ref([])

const headers = [
  { title: '', key: 'artwork_url', sortable: false, width: '60px' },
  { title: 'Música', key: 'title' },
  { title: 'Álbum', key: 'album' },
  { title: 'Gênero', key: 'genre' },
  { title: 'Duração', key: 'duration' },
  { title: 'Adicionada', key: 'created_at' },
  { title: 'Ações', key: 'actions', sortable: false }
]

const sortOptions = [
  { title: 'Mais recentes', value: 'created_at' },
  { title: 'Título A-Z', value: 'title' },
  { title: 'Artista A-Z', value: 'artist' },
  { title: 'Duração', value: 'duration' }
]

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const loadMusics = async () => {
  loading.value = true
  try {
    const data = await musicStore.fetchMusics()
    musics.value = data.musics || []
    
    // Extrair gêneros únicos
    const uniqueGenres = [...new Set(musics.value.map(m => m.genre).filter(Boolean))]
    genres.value = uniqueGenres.map(g => ({ title: g, value: g }))
  } catch (error) {
    console.error('Erro ao carregar músicas:', error)
  } finally {
    loading.value = false
  }
}

const searchMusics = () => {
  // A busca é feita pelo v-data-table automaticamente
}

const applyFilters = () => {
  // Implementar filtros
  loadMusics()
}

const clearFilters = () => {
  search.value = ''
  filters.value = {
    genre: null,
    sortBy: 'created_at'
  }
  loadMusics()
}

const playMusic = (music) => {
  musicStore.playMusic(music)
}

const toggleFavorite = async (music) => {
  try {
    await musicStore.toggleFavorite(music.id)
    music.is_favorite = !music.is_favorite
  } catch (error) {
    console.error('Erro ao alterar favorito:', error)
  }
}

const showAddToPlaylist = (music) => {
  // Implementar adicionar à playlist
  console.log('Adicionar à playlist:', music)
}

const downloadMusic = (music) => {
  if (music.file_url) {
    const link = document.createElement('a')
    link.href = music.file_url
    link.download = `${music.artist} - ${music.title}.mp3`
    link.click()
  }
}

const confirmDelete = (music) => {
  selectedMusic.value = music
  deleteDialog.value = true
}

const deleteMusic = async () => {
  try {
    await musicStore.deleteMusic(selectedMusic.value.id)
    musics.value = musics.value.filter(m => m.id !== selectedMusic.value.id)
    deleteDialog.value = false
    selectedMusic.value = null
  } catch (error) {
    console.error('Erro ao excluir música:', error)
  }
}

onMounted(() => {
  loadMusics()
})
</script> 