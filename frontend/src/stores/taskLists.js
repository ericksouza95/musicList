import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'

export const useTaskListsStore = defineStore('taskLists', () => {
  // Estado
  const taskLists = ref([])
  const currentTaskList = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const getTaskListById = computed(() => {
    return (id) => taskLists.value.find(list => list.id === id)
  })

  const activeLists = computed(() => {
    return taskLists.value.filter(list => !list.is_archived)
  })

  const archivedLists = computed(() => {
    return taskLists.value.filter(list => list.is_archived)
  })

  const totalLists = computed(() => taskLists.value.length)

  // Actions
  async function fetchTaskLists(includeArchived = false) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get('/api/task-lists', {
        params: { include_archived: includeArchived }
      })
      
      taskLists.value = response.data.task_lists || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao carregar listas'
      console.error('Erro ao buscar listas:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTaskListById(id, includeCompleted = true) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get(`/api/task-lists/${id}`, {
        params: { include_completed: includeCompleted }
      })
      
      currentTaskList.value = response.data.task_list
      
      // Atualizar na lista também
      const index = taskLists.value.findIndex(list => list.id === id)
      if (index !== -1) {
        taskLists.value[index] = response.data.task_list
      }
      
      return response.data.task_list
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao carregar lista'
      console.error('Erro ao buscar lista:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTaskList(taskListData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.post('/api/task-lists', taskListData)
      
      const newList = response.data.task_list
      taskLists.value.unshift(newList)
      
      return newList
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao criar lista'
      console.error('Erro ao criar lista:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTaskList(id, updates) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.put(`/api/task-lists/${id}`, updates)
      
      const updatedList = response.data.task_list
      
      // Atualizar na lista
      const index = taskLists.value.findIndex(list => list.id === id)
      if (index !== -1) {
        taskLists.value[index] = updatedList
      }
      
      // Atualizar currentTaskList se for a mesma
      if (currentTaskList.value?.id === id) {
        currentTaskList.value = updatedList
      }
      
      return updatedList
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao atualizar lista'
      console.error('Erro ao atualizar lista:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTaskList(id) {
    loading.value = true
    error.value = null
    
    try {
      await apiService.delete(`/api/task-lists/${id}`)
      
      // Remover da lista
      taskLists.value = taskLists.value.filter(list => list.id !== id)
      
      // Limpar currentTaskList se for a mesma
      if (currentTaskList.value?.id === id) {
        currentTaskList.value = null
      }
      
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao deletar lista'
      console.error('Erro ao deletar lista:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleArchiveTaskList(id) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.patch(`/api/task-lists/${id}/archive`)
      
      const updatedList = response.data.task_list
      
      // Atualizar na lista
      const index = taskLists.value.findIndex(list => list.id === id)
      if (index !== -1) {
        taskLists.value[index] = updatedList
      }
      
      return updatedList
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao arquivar/desarquivar lista'
      console.error('Erro ao arquivar lista:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getTaskListStats(id) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get(`/api/task-lists/${id}/stats`)
      return response.data.stats
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao carregar estatísticas'
      console.error('Erro ao buscar estatísticas:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearCurrentTaskList() {
    currentTaskList.value = null
  }

  function clearError() {
    error.value = null
  }

  function reset() {
    taskLists.value = []
    currentTaskList.value = null
    loading.value = false
    error.value = null
  }

  return {
    // Estado
    taskLists,
    currentTaskList,
    loading,
    error,
    
    // Getters
    getTaskListById,
    activeLists,
    archivedLists,
    totalLists,
    
    // Actions
    fetchTaskLists,
    fetchTaskListById,
    createTaskList,
    updateTaskList,
    deleteTaskList,
    toggleArchiveTaskList,
    getTaskListStats,
    clearCurrentTaskList,
    clearError,
    reset
  }
}) 