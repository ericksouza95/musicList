<template>
  <v-container class="pa-6">
    <h1 class="text-h4 font-weight-bold mb-6">
      <v-icon class="mr-2">mdi-magnify</v-icon>
      Buscar Músicas
    </h1>

    <!-- Campo de busca -->
    <v-card class="mb-6">
      <v-card-text>
        <v-text-field
          v-model="searchQuery"
          label="Digite o nome da música, artista ou álbum"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          size="large"
          @keyup.enter="searchMusics"
        />
        <v-btn
          color="primary"
          size="large"
          class="mt-4"
          :loading="musicStore.loading"
          @click="searchMusics"
        >
          Buscar
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Resultados da busca -->
    <v-card v-if="musicStore.searchResults.length > 0">
      <v-card-title>Resultados da Busca</v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item
            v-for="music in musicStore.searchResults"
            :key="music.id"
            class="pa-4"
          >
            <template #prepend>
              <v-avatar size="60">
                <v-img
                  v-if="music.artwork_url"
                  :src="music.artwork_url"
                  :alt="music.title"
                />
                <v-icon v-else size="30">mdi-music</v-icon>
              </v-avatar>
            </template>

            <div class="flex-grow-1 mr-4">
              <div class="text-h6 font-weight-medium">{{ music.title }}</div>
              <div class="text-subtitle-2 text-medium-emphasis">{{ music.artist }}</div>
              <div class="text-caption">{{ music.album }} • {{ music.year }}</div>
            </div>

            <template #append>
              <div class="d-flex align-center">
                <v-chip
                  v-if="music.genre"
                  size="small"
                  color="primary"
                  variant="outlined"
                  class="mr-2"
                >
                  {{ music.genre }}
                </v-chip>
                
                <v-btn
                  v-if="music.source === 'external'"
                  icon="mdi-plus"
                  color="primary"
                  @click="addToLibrary(music)"
                  :loading="addingMusic === music.id"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
                
                <v-btn
                  v-else
                  icon="mdi-play"
                  color="primary"
                  @click="playMusic(music)"
                >
                  <v-icon>mdi-play</v-icon>
                </v-btn>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- Estado vazio -->
    <v-card v-if="!musicStore.loading && searchQuery && musicStore.searchResults.length === 0">
      <v-card-text class="text-center pa-8">
        <v-icon size="64" color="grey">mdi-music-off</v-icon>
        <div class="text-h6 mt-4">Nenhuma música encontrada</div>
        <div class="text-subtitle-1 text-medium-emphasis">
          Tente buscar com termos diferentes
        </div>
      </v-card-text>
    </v-card>

    <!-- Estado inicial -->
    <v-card v-if="!searchQuery">
      <v-card-text class="text-center pa-8">
        <v-icon size="64" color="primary">mdi-magnify</v-icon>
        <div class="text-h6 mt-4">Busque por suas músicas favoritas</div>
        <div class="text-subtitle-1 text-medium-emphasis">
          Digite o nome da música, artista ou álbum acima
        </div>
        
        <!-- Sugestões de busca -->
        <div class="mt-6">
          <div class="text-subtitle-2 mb-2">Sugestões:</div>
          <v-chip-group>
            <v-chip
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="searchQuery = suggestion; searchMusics()"
            >
              {{ suggestion }}
            </v-chip>
          </v-chip-group>
        </div>
      </v-card-text>
    </v-card>

    <!-- Snackbar de sucesso -->
    <v-snackbar
      v-model="showSuccess"
      color="success"
      timeout="3000"
    >
      Música adicionada à sua biblioteca!
      <template #actions>
        <v-btn @click="showSuccess = false">Fechar</v-btn>
      </template>
    </v-snackbar>

    <!-- Snackbar de erro -->
    <v-snackbar
      v-model="showError"
      color="error"
      timeout="5000"
    >
      {{ errorMessage }}
      <template #actions>
        <v-btn @click="showError = false">Fechar</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMusicStore } from '@/stores/music'

const route = useRoute()
const musicStore = useMusicStore()

const searchQuery = ref('')
const addingMusic = ref(null)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')

const suggestions = [
  'Ed Sheeran',
  'The Weeknd',
  'Taylor Swift',
  'Drake',
  'Billie Eilish',
  'Pop',
  'Rock',
  'Hip Hop'
]

const searchMusics = async () => {
  if (!searchQuery.value.trim()) return
  
  try {
    await musicStore.searchMusics(searchQuery.value)
  } catch (error) {
    console.error('Erro na busca:', error)
    errorMessage.value = 'Erro ao buscar músicas. Tente novamente.'
    showError.value = true
  }
}

const addToLibrary = async (music) => {
  addingMusic.value = music.id
  try {
    await musicStore.addToLibrary(music)
    showSuccess.value = true
  } catch (error) {
    console.error('Erro ao adicionar à biblioteca:', error)
    errorMessage.value = 'Erro ao adicionar música à biblioteca'
    showError.value = true
  } finally {
    addingMusic.value = null
  }
}

const playMusic = (music) => {
  musicStore.playMusic(music)
}

onMounted(() => {
  // Verificar se há query parameter
  if (route.query.q) {
    searchQuery.value = route.query.q
    searchMusics()
  }
})
</script> 