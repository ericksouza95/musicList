<template>
  <v-card
    v-if="currentMusic"
    class="music-player"
    elevation="8"
    color="surface"
  >
    <v-card-text class="pa-4">
      <div class="d-flex align-center">
        <!-- Artwork da música -->
        <v-avatar size="56" class="mr-4">
          <v-img
            v-if="currentMusic.artwork_url"
            :src="currentMusic.artwork_url"
            :alt="currentMusic.title"
          />
          <v-icon v-else size="32">mdi-music</v-icon>
        </v-avatar>

        <!-- Informações da música -->
        <div class="flex-grow-1 mr-4">
          <div class="text-subtitle-1 font-weight-medium">
            {{ currentMusic.title }}
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ currentMusic.artist }}
          </div>
        </div>

        <!-- Controles de reprodução -->
        <div class="d-flex align-center">
          <v-btn
            icon="mdi-skip-previous"
            variant="text"
            @click="previousTrack"
          />
          
          <v-btn
            :icon="isPlaying ? 'mdi-pause' : 'mdi-play'"
            color="primary"
            @click="togglePlay"
          />
          
          <v-btn
            icon="mdi-skip-next"
            variant="text"
            @click="nextTrack"
          />
          
          <v-btn
            :icon="isMuted ? 'mdi-volume-off' : 'mdi-volume-high'"
            variant="text"
            @click="toggleMute"
          />
        </div>
      </div>

      <!-- Barra de progresso -->
      <div class="mt-3">
        <v-slider
          v-model="currentTime"
          :max="duration"
          hide-details
          density="compact"
          @update:model-value="seekTo"
        >
          <template #prepend>
            <span class="text-caption">{{ formatTime(currentTime) }}</span>
          </template>
          <template #append>
            <span class="text-caption">{{ formatTime(duration) }}</span>
          </template>
        </v-slider>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useMusicStore } from '@/stores/music'

const musicStore = useMusicStore()

const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const isMuted = ref(false)
const audio = ref(null)

const currentMusic = computed(() => musicStore.currentMusic)

const togglePlay = () => {
  if (!audio.value) return
  
  if (isPlaying.value) {
    audio.value.pause()
  } else {
    audio.value.play()
  }
}

const previousTrack = () => {
  musicStore.playPrevious()
}

const nextTrack = () => {
  musicStore.playNext()
}

const toggleMute = () => {
  if (!audio.value) return
  
  isMuted.value = !isMuted.value
  audio.value.muted = isMuted.value
}

const seekTo = (time) => {
  if (!audio.value) return
  
  audio.value.currentTime = time
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const setupAudioEvents = () => {
  if (!audio.value) return
  
  audio.value.addEventListener('loadedmetadata', () => {
    duration.value = audio.value.duration
  })
  
  audio.value.addEventListener('timeupdate', () => {
    currentTime.value = audio.value.currentTime
  })
  
  audio.value.addEventListener('play', () => {
    isPlaying.value = true
  })
  
  audio.value.addEventListener('pause', () => {
    isPlaying.value = false
  })
  
  audio.value.addEventListener('ended', () => {
    nextTrack()
  })
}

watch(currentMusic, (newMusic) => {
  if (newMusic && newMusic.file_url) {
    if (audio.value) {
      audio.value.pause()
    }
    
    audio.value = new Audio(newMusic.file_url)
    setupAudioEvents()
    audio.value.play()
  }
})

onMounted(() => {
  if (currentMusic.value && currentMusic.value.file_url) {
    audio.value = new Audio(currentMusic.value.file_url)
    setupAudioEvents()
  }
})

onUnmounted(() => {
  if (audio.value) {
    audio.value.pause()
    audio.value = null
  }
})
</script>

<style scoped>
.music-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}
</style> 