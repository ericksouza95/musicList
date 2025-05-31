<template>
  <v-container class="pa-6">
    <h1 class="text-h4 font-weight-bold mb-6">
      <v-icon class="mr-2">mdi-upload</v-icon>
      Adicionar Música
    </h1>

    <v-row>
      <!-- Upload de arquivo -->
      <v-col cols="12" md="6">
        <v-card class="mb-6">
          <v-card-title>Upload de Arquivo</v-card-title>
          <v-card-text>
            <v-file-input
              v-model="selectedFile"
              label="Selecione um arquivo de música"
              accept="audio/*"
              prepend-icon="mdi-music"
              variant="outlined"
              show-size
              @change="handleFileSelect"
            />

            <v-form v-if="selectedFile" @submit.prevent="uploadMusic" ref="uploadForm">
              <v-text-field
                v-model="musicData.title"
                label="Título da música"
                variant="outlined"
                :rules="[rules.required]"
                required
                class="mt-4"
              />

              <v-text-field
                v-model="musicData.artist"
                label="Artista"
                variant="outlined"
                :rules="[rules.required]"
                required
              />

              <v-text-field
                v-model="musicData.album"
                label="Álbum"
                variant="outlined"
              />

              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="musicData.genre"
                    label="Gênero"
                    variant="outlined"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="musicData.year"
                    label="Ano"
                    type="number"
                    variant="outlined"
                  />
                </v-col>
              </v-row>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="uploadLoading"
                class="mt-4"
              >
                <v-icon class="mr-2">mdi-upload</v-icon>
                Fazer Upload
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Preview do arquivo -->
      <v-col cols="12" md="6">
        <v-card v-if="selectedFile">
          <v-card-title>Preview</v-card-title>
          <v-card-text>
            <div class="text-center pa-4">
              <v-icon size="64" color="primary">mdi-music</v-icon>
              <div class="text-h6 mt-2">{{ selectedFile.name }}</div>
              <div class="text-caption">{{ formatFileSize(selectedFile.size) }}</div>
              
              <!-- Player de áudio se suportado -->
              <audio 
                v-if="audioPreview" 
                :src="audioPreview" 
                controls 
                class="mt-4"
                style="width: 100%"
              ></audio>
            </div>
          </v-card-text>
        </v-card>

        <!-- Informações de ajuda -->
        <v-card v-else>
          <v-card-title>Como funciona?</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <template #prepend>
                  <v-icon color="primary">mdi-file-music</v-icon>
                </template>
                <v-list-item-title>Formatos suportados</v-list-item-title>
                <v-list-item-subtitle>MP3, WAV, FLAC, M4A</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="primary">mdi-information</v-icon>
                </template>
                <v-list-item-title>Metadados automáticos</v-list-item-title>
                <v-list-item-subtitle>Tentaremos extrair informações do arquivo</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="primary">mdi-cloud-upload</v-icon>
                </template>
                <v-list-item-title>Upload seguro</v-list-item-title>
                <v-list-item-subtitle>Seus arquivos são protegidos</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upload em massa -->
    <v-card class="mt-6">
      <v-card-title>Upload em Massa</v-card-title>
      <v-card-text>
        <v-file-input
          v-model="bulkFiles"
          label="Selecione múltiplos arquivos"
          accept="audio/*"
          multiple
          prepend-icon="mdi-file-multiple"
          variant="outlined"
          show-size
        />

        <v-btn
          v-if="bulkFiles.length > 0"
          color="secondary"
          :loading="bulkUploadLoading"
          @click="uploadBulkFiles"
          class="mt-4"
        >
          <v-icon class="mr-2">mdi-upload-multiple</v-icon>
          Upload {{ bulkFiles.length }} arquivo(s)
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Progress das uploads -->
    <v-card v-if="uploadProgress.length > 0" class="mt-6">
      <v-card-title>Progresso das Uploads</v-card-title>
      <v-card-text>
        <div v-for="(progress, index) in uploadProgress" :key="index" class="mb-4">
          <div class="d-flex justify-space-between mb-1">
            <span class="text-body-2">{{ progress.filename }}</span>
            <span class="text-caption">{{ progress.status }}</span>
          </div>
          <v-progress-linear
            :model-value="progress.percentage"
            :color="progress.status === 'Erro' ? 'error' : 'primary'"
            height="6"
          />
        </div>
      </v-card-text>
    </v-card>

    <!-- Snackbars -->
    <v-snackbar
      v-model="showSuccess"
      color="success"
      timeout="3000"
    >
      {{ successMessage }}
      <template #actions>
        <v-btn @click="showSuccess = false">Fechar</v-btn>
      </template>
    </v-snackbar>

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
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMusicStore } from '@/stores/music'

const router = useRouter()
const musicStore = useMusicStore()

const selectedFile = ref(null)
const bulkFiles = ref([])
const audioPreview = ref(null)
const uploadLoading = ref(false)
const bulkUploadLoading = ref(false)
const uploadProgress = ref([])

const musicData = ref({
  title: '',
  artist: '',
  album: '',
  genre: '',
  year: new Date().getFullYear()
})

const showSuccess = ref(false)
const showError = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const rules = {
  required: (value) => !!value || 'Campo obrigatório'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileSelect = (event) => {
  if (selectedFile.value) {
    // Tentar extrair metadados do nome do arquivo
    const filename = selectedFile.value.name
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, '')
    
    // Tentar separar artista - título
    if (nameWithoutExt.includes(' - ')) {
      const parts = nameWithoutExt.split(' - ')
      musicData.value.artist = parts[0].trim()
      musicData.value.title = parts[1].trim()
    } else {
      musicData.value.title = nameWithoutExt
    }

    // Criar preview de áudio
    if (selectedFile.value.type.startsWith('audio/')) {
      audioPreview.value = URL.createObjectURL(selectedFile.value)
    }
  }
}

const uploadMusic = async () => {
  if (!selectedFile.value) return

  uploadLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('title', musicData.value.title)
    formData.append('artist', musicData.value.artist)
    formData.append('album', musicData.value.album || '')
    formData.append('genre', musicData.value.genre || '')
    formData.append('year', musicData.value.year || '')

    await musicStore.uploadMusic(formData)
    
    successMessage.value = 'Música enviada com sucesso!'
    showSuccess.value = true
    
    // Reset form
    selectedFile.value = null
    audioPreview.value = null
    musicData.value = {
      title: '',
      artist: '',
      album: '',
      genre: '',
      year: new Date().getFullYear()
    }

    // Redirecionar para lista de músicas após 2 segundos
    setTimeout(() => {
      router.push('/music')
    }, 2000)

  } catch (error) {
    console.error('Erro no upload:', error)
    errorMessage.value = error.message || 'Erro ao fazer upload da música'
    showError.value = true
  } finally {
    uploadLoading.value = false
  }
}

const uploadBulkFiles = async () => {
  if (bulkFiles.value.length === 0) return

  bulkUploadLoading.value = true
  uploadProgress.value = []

  for (let i = 0; i < bulkFiles.value.length; i++) {
    const file = bulkFiles.value[i]
    const progressItem = {
      filename: file.name,
      percentage: 0,
      status: 'Enviando...'
    }
    uploadProgress.value.push(progressItem)

    try {
      progressItem.percentage = 50
      
      const formData = new FormData()
      formData.append('file', file)
      
      // Tentar extrair título do nome do arquivo
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
      if (nameWithoutExt.includes(' - ')) {
        const parts = nameWithoutExt.split(' - ')
        formData.append('artist', parts[0].trim())
        formData.append('title', parts[1].trim())
      } else {
        formData.append('title', nameWithoutExt)
      }

      await musicStore.uploadMusic(formData)
      
      progressItem.percentage = 100
      progressItem.status = 'Concluído'
    } catch (error) {
      progressItem.percentage = 100
      progressItem.status = 'Erro'
      console.error(`Erro no upload de ${file.name}:`, error)
    }
  }

  bulkUploadLoading.value = false
  
  const successCount = uploadProgress.value.filter(p => p.status === 'Concluído').length
  if (successCount > 0) {
    successMessage.value = `${successCount} música(s) enviada(s) com sucesso!`
    showSuccess.value = true
  }

  // Reset after 5 seconds
  setTimeout(() => {
    uploadProgress.value = []
    bulkFiles.value = []
  }, 5000)
}

// Cleanup audio preview on unmount
watch(selectedFile, (newFile, oldFile) => {
  if (oldFile && audioPreview.value) {
    URL.revokeObjectURL(audioPreview.value)
  }
})
</script> 