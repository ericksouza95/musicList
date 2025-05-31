import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'

export const useTasksStore = defineStore('tasks', () => {
  // Estado
  const tasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const dashboardStats = ref(null)
  const priorities = ref([])

  // Getters
  const getTaskById = computed(() => {
    return (id) => tasks.value.find(task => task.id === id)
  })

  const completedTasks = computed(() => {
    return tasks.value.filter(task => task.completed)
  })

  const pendingTasks = computed(() => {
    return tasks.value.filter(task => !task.completed)
  })

  const overdueTasks = computed(() => {
    return tasks.value.filter(task => task.is_overdue)
  })

  const tasksByPriority = computed(() => {
    const grouped = {}
    priorities.value.forEach(priority => {
      grouped[priority.value] = tasks.value.filter(task => task.priority === priority.value)
    })
    return grouped
  })

  const totalTasks = computed(() => tasks.value.length)

  // Actions
  async function fetchTasks(filters = {}) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get('/api/tasks', { params: filters })
      
      tasks.value = response.data.tasks || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao carregar tarefas'
      console.error('Erro ao buscar tarefas:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTaskById(id) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get(`/api/tasks/${id}`)
      
      currentTask.value = response.data.task
      
      // Atualizar na lista também
      const index = tasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        tasks.value[index] = response.data.task
      }
      
      return response.data.task
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao carregar tarefa'
      console.error('Erro ao buscar tarefa:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTask(taskData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.post('/api/tasks', taskData)
      
      const newTask = response.data.task
      tasks.value.unshift(newTask)
      
      return newTask
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao criar tarefa'
      console.error('Erro ao criar tarefa:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTask(id, updates) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.put(`/api/tasks/${id}`, updates)
      
      const updatedTask = response.data.task
      
      // Atualizar na lista
      const index = tasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      
      // Atualizar currentTask se for a mesma
      if (currentTask.value?.id === id) {
        currentTask.value = updatedTask
      }
      
      return updatedTask
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao atualizar tarefa'
      console.error('Erro ao atualizar tarefa:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTask(id) {
    loading.value = true
    error.value = null
    
    try {
      await apiService.delete(`/api/tasks/${id}`)
      
      // Remover da lista
      tasks.value = tasks.value.filter(task => task.id !== id)
      
      // Limpar currentTask se for a mesma
      if (currentTask.value?.id === id) {
        currentTask.value = null
      }
      
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao deletar tarefa'
      console.error('Erro ao deletar tarefa:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleTaskCompletion(id) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.patch(`/api/tasks/${id}/toggle`)
      
      const updatedTask = response.data.task
      
      // Atualizar na lista
      const index = tasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      
      // Atualizar currentTask se for a mesma
      if (currentTask.value?.id === id) {
        currentTask.value = updatedTask
      }
      
      return updatedTask
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao alterar status da tarefa'
      console.error('Erro ao toggle tarefa:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPriorities() {
    try {
      const response = await apiService.get('/api/tasks/priorities')
      priorities.value = response.data.priorities || []
      return response.data.priorities
    } catch (err) {
      console.error('Erro ao buscar prioridades:', err)
      // Prioridades padrão como fallback
      priorities.value = [
        { value: 'low', label: 'Baixa', color: '#4caf50' },
        { value: 'medium', label: 'Média', color: '#ff9800' },
        { value: 'high', label: 'Alta', color: '#f44336' },
        { value: 'urgent', label: 'Urgente', color: '#9c27b0' }
      ]
      return priorities.value
    }
  }

  async function fetchDashboardStats() {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get('/api/tasks/dashboard')
      
      dashboardStats.value = response.data.stats
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro ao carregar estatísticas'
      console.error('Erro ao buscar dashboard:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function bulkOperation(taskIds, operation, options = {}) {
    loading.value = true
    error.value = null
    
    try {
      const payload = {
        task_ids: taskIds,
        operation,
        ...options
      }
      
      const response = await apiService.post('/api/tasks/bulk', payload)
      
      // Recarregar tarefas após operação em lote
      await fetchTasks()
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Erro na operação em lote'
      console.error('Erro em operação bulk:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearCurrentTask() {
    currentTask.value = null
  }

  function clearError() {
    error.value = null
  }

  function reset() {
    tasks.value = []
    currentTask.value = null
    loading.value = false
    error.value = null
    dashboardStats.value = null
  }

  // Filtros úteis
  function filterTasks(filters) {
    let filtered = [...tasks.value]
    
    if (filters.completed !== undefined) {
      filtered = filtered.filter(task => task.completed === filters.completed)
    }
    
    if (filters.priority) {
      filtered = filtered.filter(task => task.priority === filters.priority)
    }
    
    if (filters.task_list_id) {
      filtered = filtered.filter(task => task.task_list_id === filters.task_list_id)
    }
    
    if (filters.search) {
      const search = filters.search.toLowerCase()
      filtered = filtered.filter(task => 
        task.title.toLowerCase().includes(search) ||
        task.description?.toLowerCase().includes(search)
      )
    }
    
    if (filters.overdue_only) {
      filtered = filtered.filter(task => task.is_overdue)
    }
    
    return filtered
  }

  return {
    // Estado
    tasks,
    currentTask,
    loading,
    error,
    dashboardStats,
    priorities,
    
    // Getters
    getTaskById,
    completedTasks,
    pendingTasks,
    overdueTasks,
    tasksByPriority,
    totalTasks,
    
    // Actions
    fetchTasks,
    fetchTaskById,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
    fetchPriorities,
    fetchDashboardStats,
    bulkOperation,
    clearCurrentTask,
    clearError,
    reset,
    filterTasks
  }
}) 