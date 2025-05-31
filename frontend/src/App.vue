<template>
  <v-app>
    <!-- Barra de navegação -->
    <v-app-bar
      v-if="authStore.isAuthenticated"
      app
      color="primary"
      dark
      elevation="1"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <v-toolbar-title>
        <v-icon class="mr-2">mdi-music</v-icon>
        Music List
      </v-toolbar-title>

      <v-spacer />

      <!-- Busca rápida -->
      <v-text-field
        v-model="searchQuery"
        hide-details
        placeholder="Buscar músicas..."
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="compact"
        class="mr-4"
        style="max-width: 300px"
        @keyup.enter="performSearch"
      />

      <!-- Menu do usuário -->
      <v-menu>
        <template #activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar size="32">
              <v-img
                v-if="authStore.user?.avatar_url"
                :src="authStore.user.avatar_url"
                :alt="authStore.fullName"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
            <v-list-item-title>{{ authStore.fullName }}</v-list-item-title>
            <v-list-item-subtitle>{{ authStore.user?.email }}</v-list-item-subtitle>
          </v-list-item>

          <v-divider />

          <v-list-item @click="$router.push('/profile')">
            <template #prepend>
              <v-icon>mdi-account-circle</v-icon>
            </template>
            <v-list-item-title>Perfil</v-list-item-title>
          </v-list-item>

          <v-list-item @click="toggleTheme">
            <template #prepend>
              <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
            </template>
            <v-list-item-title>{{ isDark ? 'Tema Claro' : 'Tema Escuro' }}</v-list-item-title>
          </v-list-item>

          <v-divider />

          <v-list-item @click="logout">
            <template #prepend>
              <v-icon>mdi-logout</v-icon>
            </template>
            <v-list-item-title>Sair</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Menu lateral -->
    <v-navigation-drawer
      v-if="authStore.isAuthenticated"
      v-model="drawer"
      app
      temporary
    >
      <v-list>
        <v-list-item
          prepend-icon="mdi-home"
          title="Início"
          @click="$router.push('/')"
        />
        
        <v-list-item
          prepend-icon="mdi-music"
          title="Músicas"
          @click="$router.push('/music')"
        />
        
        <v-list-item
          prepend-icon="mdi-playlist-music"
          title="Playlists"
          @click="$router.push('/playlists')"
        />

        <v-divider class="my-2" />

        <v-list-item
          prepend-icon="mdi-magnify"
          title="Buscar Músicas"
          @click="$router.push('/music/search')"
        />
        
        <v-list-item
          prepend-icon="mdi-upload"
          title="Upload de Música"
          @click="$router.push('/music/upload')"
        />

        <v-divider v-if="authStore.isAdmin" class="my-2" />

        <v-list-item
          v-if="authStore.isAdmin"
          prepend-icon="mdi-account-group"
          title="Usuários"
          @click="$router.push('/users')"
        />
      </v-list>
    </v-navigation-drawer>

    <!-- Conteúdo principal -->
    <v-main>
      <router-view />
    </v-main>

    <!-- Player de música (se houver música tocando) -->
    <MusicPlayer v-if="authStore.isAuthenticated" />

    <!-- Loading global -->
    <v-overlay
      v-model="isLoading"
      class="align-center justify-center"
      persistent
    >
      <v-progress-circular
        color="primary"
        indeterminate
        size="64"
      />
    </v-overlay>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAuthStore } from '@/stores/auth'
import MusicPlayer from '@/components/MusicPlayer.vue'

const router = useRouter()
const theme = useTheme()
const authStore = useAuthStore()

const drawer = ref(false)
const searchQuery = ref('')
const isLoading = ref(false)

const isDark = computed(() => theme.global.current.value.dark)

const toggleTheme = () => {
  theme.global.name.value = isDark.value ? 'musicTheme' : 'musicDarkTheme'
}

const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'MusicSearch',
      query: { q: searchQuery.value.trim() }
    })
  }
}

const logout = async () => {
  isLoading.value = true
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Erro ao fazer logout:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  // Inicializar store de autenticação
  await authStore.initialize()
})
</script>

<style scoped>
.v-app-bar .v-text-field {
  margin-top: 0;
}
</style> 