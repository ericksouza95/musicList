<template>
  <v-container class="pa-6">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4 font-weight-bold">
        <v-icon class="mr-2">mdi-playlist-music</v-icon>
        Suas Playlists
      </h1>
      <v-spacer />
      <v-btn color="primary" @click="createPlaylist">
        <v-icon start>mdi-plus</v-icon>
        Nova Playlist
      </v-btn>
    </div>

    <v-row>
      <v-col
        v-for="playlist in playlists"
        :key="playlist.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card
          :to="`/playlists/${playlist.id}`"
          hover
          class="mx-auto"
        >
          <v-img
            :src="playlist.artwork_url || '/default-playlist.jpg'"
            height="200"
            cover
          >
            <div class="d-flex align-end pa-4" style="height: 100%;">
              <div class="text-white">
                <div class="text-h6 font-weight-bold">{{ playlist.name }}</div>
                <div class="text-caption">{{ playlist.musics_count || 0 }} música(s)</div>
              </div>
            </div>
          </v-img>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const playlists = ref([])

const createPlaylist = () => {
  console.log('Criar nova playlist')
}

onMounted(() => {
  // Carregar playlists
  playlists.value = []
})
</script> 