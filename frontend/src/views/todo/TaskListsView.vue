<template>
  <div class="task-lists-view">
    <v-container fluid>
      <!-- Header -->
      <v-row class="mb-4">
        <v-col cols="12">
          <div class="d-flex justify-space-between align-center">
            <div>
              <h1 class="text-h4 font-weight-bold">Minhas Listas</h1>
              <p class="text-body-1 text-medium-emphasis">
                Organize suas tarefas em listas personalizadas
              </p>
            </div>
            <v-btn
              color="primary"
              size="large"
              @click="showCreateDialog = true"
              prepend-icon="mdi-plus"
            >
              Nova Lista
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <!-- Filtros -->
      <v-row class="mb-4">
        <v-col cols="12" md="6">
          <v-text-field
            v-model="searchQuery"
            label="Buscar listas..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            clearable
          />
        </v-col>
        <v-col cols="12" md="6">
          <div class="d-flex gap-2">
            <v-btn-toggle
              v-model="viewMode"
              mandatory
              variant="outlined"
              density="compact"
            >
              <v-btn value="active" size="small">
                <v-icon start>mdi-format-list-bulleted</v-icon>
                Ativas
              </v-btn>
              <v-btn value="archived" size="small">
                <v-icon start>mdi-archive</v-icon>
                Arquivadas
              </v-btn>
            </v-btn-toggle>
          </div>
        </v-col>
      </v-row>

      <!-- Loading -->
      <v-row v-if="taskListsStore.loading">
        <v-col cols="12">
          <div class="text-center py-8">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
            />
            <p class="mt-4 text-body-1">Carregando listas...</p>
          </div>
        </v-col>
      </v-row>

      <!-- Lista vazia -->
      <v-row v-else-if="filteredLists.length === 0">
        <v-col cols="12">
          <v-card class="text-center py-8">
            <v-card-text>
              <v-icon
                size="64"
                color="grey-lighten-1"
                class="mb-4"
              >
                mdi-format-list-bulleted-square
              </v-icon>
              <h3 class="text-h6 mb-2">
                {{ viewMode === 'active' ? 'Nenhuma lista ativa' : 'Nenhuma lista arquivada' }}
              </h3>
              <p class="text-body-2 text-medium-emphasis mb-4">
                {{ viewMode === 'active' 
                  ? 'Crie sua primeira lista para começar a organizar suas tarefas'
                  : 'Você não possui listas arquivadas'
                }}
              </p>
              <v-btn
                v-if="viewMode === 'active'"
                color="primary"
                @click="showCreateDialog = true"
              >
                Criar Primeira Lista
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Grid de Listas -->
      <v-row v-else>
        <v-col
          v-for="list in filteredLists"
          :key="list.id"
          cols="12"
          sm="6"
          md="4"
          lg="3"
        >
          <v-card
            :style="{ borderTop: `4px solid ${list.color}` }"
            @click="goToList(list.id)"
            class="h-100 task-list-card"
            hover
          >
            <v-card-text class="pb-2">
              <div class="d-flex justify-space-between align-start mb-2">
                <h3 class="text-h6 font-weight-medium text-truncate">
                  {{ list.title }}
                </h3>
                <v-menu>
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-dots-vertical"
                      size="small"
                      variant="text"
                      @click.stop
                    />
                  </template>
                  <v-list density="compact">
                    <v-list-item
                      @click="editList(list)"
                      prepend-icon="mdi-pencil"
                    >
                      Editar
                    </v-list-item>
                    <v-list-item
                      @click="toggleArchive(list)"
                      :prepend-icon="list.is_archived ? 'mdi-unarchive' : 'mdi-archive'"
                    >
                      {{ list.is_archived ? 'Desarquivar' : 'Arquivar' }}
                    </v-list-item>
                    <v-list-item
                      @click="deleteList(list)"
                      prepend-icon="mdi-delete"
                      class="text-error"
                    >
                      Excluir
                    </v-list-item>
                  </v-list>
                </v-menu>
              </div>

              <p class="text-body-2 text-medium-emphasis mb-3">
                {{ list.description || 'Sem descrição' }}
              </p>

              <!-- Estatísticas -->
              <div class="d-flex justify-space-between align-center">
                <div class="d-flex gap-3">
                  <div class="text-center">
                    <div class="text-h6 font-weight-bold">{{ list.task_count }}</div>
                    <div class="text-caption text-medium-emphasis">Total</div>
                  </div>
                  <div class="text-center">
                    <div class="text-h6 font-weight-bold text-success">
                      {{ list.completed_count }}
                    </div>
                    <div class="text-caption text-medium-emphasis">Concluídas</div>
                  </div>
                  <div class="text-center">
                    <div class="text-h6 font-weight-bold text-warning">
                      {{ list.pending_count }}
                    </div>
                    <div class="text-caption text-medium-emphasis">Pendentes</div>
                  </div>
                </div>

                <!-- Progress -->
                <div class="flex-shrink-0">
                  <v-progress-circular
                    :model-value="getCompletionRate(list)"
                    :color="list.color"
                    size="40"
                    width="4"
                  >
                    <span class="text-caption">
                      {{ Math.round(getCompletionRate(list)) }}%
                    </span>
                  </v-progress-circular>
                </div>
              </div>
            </v-card-text>

            <v-card-actions class="pt-0">
              <v-chip
                size="small"
                :color="list.is_archived ? 'grey' : 'primary'"
                variant="tonal"
              >
                {{ list.is_archived ? 'Arquivada' : 'Ativa' }}
              </v-chip>
              <v-spacer />
              <v-btn
                size="small"
                variant="text"
                @click.stop="goToList(list.id)"
              >
                Abrir
                <v-icon end>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Dialog: Criar/Editar Lista -->
    <v-dialog
      v-model="showCreateDialog"
      max-width="500"
      persistent
    >
      <v-card>
        <v-card-title>
          {{ editingList ? 'Editar Lista' : 'Nova Lista' }}
        </v-card-title>

        <v-card-text>
          <v-form ref="form" v-model="formValid">
            <v-text-field
              v-model="formData.title"
              label="Título da Lista"
              :rules="[rules.required, rules.maxLength(100)]"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />

            <v-textarea
              v-model="formData.description"
              label="Descrição (opcional)"
              variant="outlined"
              density="comfortable"
              rows="3"
              class="mb-3"
            />

            <div class="mb-3">
              <label class="text-body-2 font-weight-medium mb-2 d-block">
                Cor da Lista
              </label>
              <div class="d-flex gap-2 flex-wrap">
                <v-btn
                  v-for="color in availableColors"
                  :key="color"
                  :color="color"
                  :variant="formData.color === color ? 'elevated' : 'tonal'"
                  size="small"
                  icon
                  @click="formData.color = color"
                >
                  <v-icon v-if="formData.color === color">mdi-check</v-icon>
                </v-btn>
              </div>
            </div>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            @click="cancelEdit"
            variant="text"
          >
            Cancelar
          </v-btn>
          <v-btn
            @click="saveList"
            color="primary"
            :loading="taskListsStore.loading"
            :disabled="!formValid"
          >
            {{ editingList ? 'Salvar' : 'Criar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskListsStore } from '@/stores/taskLists'
import { useNotification } from '@/composables/useNotification'

// Composables
const router = useRouter()
const taskListsStore = useTaskListsStore()
const { showSuccess, showError } = useNotification()

// Estado reativo
const searchQuery = ref('')
const viewMode = ref('active')
const showCreateDialog = ref(false)
const formValid = ref(false)
const editingList = ref(null)

// Form data
const formData = ref({
  title: '',
  description: '',
  color: '#1976d2'
})

// Cores disponíveis
const availableColors = [
  '#1976d2', '#9c27b0', '#673ab7', '#3f51b5',
  '#2196f3', '#00bcd4', '#009688', '#4caf50',
  '#8bc34a', '#cddc39', '#ffc107', '#ff9800',
  '#ff5722', '#795548', '#607d8b', '#e91e63'
]

// Regras de validação
const rules = {
  required: value => !!value || 'Campo obrigatório',
  maxLength: max => value => !value || value.length <= max || `Máximo ${max} caracteres`
}

// Computed
const filteredLists = computed(() => {
  let lists = viewMode.value === 'active' 
    ? taskListsStore.activeLists 
    : taskListsStore.archivedLists

  if (searchQuery.value) {
    const search = searchQuery.value.toLowerCase()
    lists = lists.filter(list => 
      list.title.toLowerCase().includes(search) ||
      list.description?.toLowerCase().includes(search)
    )
  }

  return lists
})

// Métodos
function getCompletionRate(list) {
  return list.task_count > 0 ? (list.completed_count / list.task_count) * 100 : 0
}

function goToList(listId) {
  router.push({ name: 'TaskList', params: { id: listId } })
}

function editList(list) {
  editingList.value = list
  formData.value = {
    title: list.title,
    description: list.description || '',
    color: list.color
  }
  showCreateDialog.value = true
}

async function saveList() {
  try {
    if (editingList.value) {
      await taskListsStore.updateTaskList(editingList.value.id, formData.value)
      showSuccess('Lista atualizada com sucesso!')
    } else {
      await taskListsStore.createTaskList(formData.value)
      showSuccess('Lista criada com sucesso!')
    }
    cancelEdit()
  } catch (error) {
    showError(error.message || 'Erro ao salvar lista')
  }
}

function cancelEdit() {
  showCreateDialog.value = false
  editingList.value = null
  formData.value = {
    title: '',
    description: '',
    color: '#1976d2'
  }
}

async function toggleArchive(list) {
  try {
    await taskListsStore.toggleArchiveTaskList(list.id)
    const action = list.is_archived ? 'desarquivada' : 'arquivada'
    showSuccess(`Lista ${action} com sucesso!`)
  } catch (error) {
    showError(error.message || 'Erro ao arquivar lista')
  }
}

async function deleteList(list) {
  if (!confirm(`Tem certeza que deseja excluir a lista "${list.title}"? Esta ação não pode ser desfeita.`)) {
    return
  }

  try {
    await taskListsStore.deleteTaskList(list.id)
    showSuccess('Lista excluída com sucesso!')
  } catch (error) {
    showError(error.message || 'Erro ao excluir lista')
  }
}

// Lifecycle
onMounted(() => {
  loadLists()
})

async function loadLists() {
  try {
    await taskListsStore.fetchTaskLists(true) // Incluir arquivadas
  } catch (error) {
    showError('Erro ao carregar listas')
  }
}

// Watchers
watch(viewMode, () => {
  searchQuery.value = ''
})
</script>

<style scoped>
.task-list-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.task-list-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 26px rgba(0,0,0,0.15) !important;
}
</style> 