<template>
  <v-container class="pa-6">
    <!-- Cabeçalho -->
    <div class="mb-6">
      <h1 class="text-h4 font-weight-bold mb-2">
        Bem-vindo, {{ authStore.user?.first_name }}! 🎵
      </h1>
      <p class="text-subtitle-1 text-medium-emphasis">
        Sua biblioteca musical pessoal
      </p>
    </div>

    <!-- Cards de estatísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="40" class="mr-3">mdi-music</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.totalMusics }}</div>
                <div class="text-caption">Músicas</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="secondary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="40" class="mr-3">mdi-playlist-music</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.totalPlaylists }}</div>
                <div class="text-caption">Playlists</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="success" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="40" class="mr-3">mdi-heart</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.favoriteMusics }}</div>
                <div class="text-caption">Favoritas</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="info" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="40" class="mr-3">mdi-clock</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ formatDuration(stats.totalDuration) }}</div>
                <div class="text-caption">Duração Total</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- Músicas recentes -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-clock-outline</v-icon>
            Adicionadas Recentemente
            <v-spacer />
            <v-btn
              variant="text"
              size="small"
              @click="$router.push('/music')"
            >
              Ver todas
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-list lines="two">
              <v-list-item
                v-for="music in recentMusics"
                :key="music.id"
                class="pa-2"
              >
                <template #prepend>
                  <v-avatar>
                    <v-img
                      v-if="music.artwork_url"
                      :src="music.artwork_url"
                      :alt="music.title"
                    />
                    <v-icon v-else>mdi-music</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ music.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ music.artist }}</v-list-item-subtitle>

                <template #append>
                  <v-btn
                    icon="mdi-play"
                    variant="text"
                    size="small"
                    @click="playMusic(music)"
                  />
                </template>
              </v-list-item>

              <v-list-item v-if="recentMusics.length === 0">
                <v-list-item-title class="text-center text-medium-emphasis">
                  Nenhuma música adicionada ainda
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Playlists recentes -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-playlist-music</v-icon>
            Suas Playlists
            <v-spacer />
            <v-btn
              variant="text"
              size="small"
              @click="$router.push('/playlists')"
            >
              Ver todas
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="playlist in recentPlaylists"
                :key="playlist.id"
                class="pa-2"
                @click="$router.push(`/playlists/${playlist.id}`)"
              >
                <template #prepend>
                  <v-avatar color="primary">
                    <v-icon>mdi-playlist-music</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ playlist.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ playlist.musics_count || 0 }} música(s)
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item v-if="recentPlaylists.length === 0">
                <v-list-item-title class="text-center text-medium-emphasis">
                  Nenhuma playlist criada ainda
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Ações rápidas -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  color="primary"
                  size="large"
                  @click="$router.push('/music/upload')"
                >
                  <v-icon start>mdi-upload</v-icon>
                  Upload de Música
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  color="secondary"
                  size="large"
                  @click="$router.push('/music/search')"
                >
                  <v-icon start>mdi-magnify</v-icon>
                  Buscar Música
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  color="success"
                  size="large"
                  @click="createPlaylist"
                >
                  <v-icon start>mdi-plus</v-icon>
                  Nova Playlist
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  color="info"
                  size="large"
                  @click="$router.push('/music')"
                >
                  <v-icon start>mdi-library-music</v-icon>
                  Ver Biblioteca
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMusicStore } from '@/stores/music'
import { usePlaylistStore } from '@/stores/playlists'

const authStore = useAuthStore()
const musicStore = useMusicStore()
const playlistStore = usePlaylistStore()

const stats = ref({
  totalMusics: 0,
  totalPlaylists: 0,
  favoriteMusics: 0,
  totalDuration: 0
})

const recentMusics = ref([])
const recentPlaylists = ref([])

const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const playMusic = (music) => {
  musicStore.playMusic(music)
}

const createPlaylist = () => {
  // Implementar criação de playlist
  console.log('Criar nova playlist')
}

const loadDashboardData = async () => {
  try {
    // Carregar estatísticas
    const response = await fetch('/api/dashboard/stats', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      stats.value = await response.json()
    }

    // Carregar músicas recentes
    const musicsResponse = await fetch('/api/musics?limit=5&sort=created_at', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (musicsResponse.ok) {
      const musicsData = await musicsResponse.json()
      recentMusics.value = musicsData.musics || []
    }

    // Carregar playlists recentes
    const playlistsResponse = await fetch('/api/playlists?limit=5', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (playlistsResponse.ok) {
      const playlistsData = await playlistsResponse.json()
      recentPlaylists.value = playlistsData.playlists || []
    }
  } catch (error) {
    console.error('Erro ao carregar dados do dashboard:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script> 