<template>
  <v-container class="pa-6">
    <v-btn
      variant="text"
      @click="$router.go(-1)"
      class="mb-4"
    >
      <v-icon start>mdi-arrow-left</v-icon>
      Voltar
    </v-btn>

    <div v-if="playlist">
      <div class="d-flex align-center mb-6">
        <v-avatar size="120" class="mr-6">
          <v-img
            v-if="playlist.artwork_url"
            :src="playlist.artwork_url"
            :alt="playlist.name"
          />
          <v-icon v-else size="60">mdi-playlist-music</v-icon>
        </v-avatar>
        
        <div>
          <h1 class="text-h4 font-weight-bold">{{ playlist.name }}</h1>
          <p class="text-subtitle-1 text-medium-emphasis">
            {{ playlist.musics?.length || 0 }} música(s)
          </p>
          <v-btn color="primary" class="mt-2">
            <v-icon start>mdi-play</v-icon>
            Reproduzir Tudo
          </v-btn>
        </div>
      </div>

      <v-card>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="(music, index) in playlist.musics"
              :key="music.id"
              class="pa-2"
            >
              <template #prepend>
                <span class="text-caption mr-4">{{ index + 1 }}</span>
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
                />
              </template>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const playlist = ref(null)

onMounted(() => {
  // Carregar playlist
  playlist.value = {
    id: route.params.id,
    name: 'Minha Playlist',
    musics: []
  }
})
</script> 