import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresGuest: true }
  },
  
  // === ROTAS TO-DO (PRINCIPAIS) ===
  {
    path: '/task-lists',
    name: 'TaskLists',
    component: () => import('@/views/todo/TaskListsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/task-lists/:id',
    name: 'TaskList',
    component: () => import('@/views/todo/TaskListDetailView.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/todo/TasksView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/todo/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  
  // === ROTAS DE MÚSICA (COMPATIBILIDADE) ===
  {
    path: '/music',
    name: 'Music',
    component: () => import('@/views/music/MusicListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/music/search',
    name: 'MusicSearch',
    component: () => import('@/views/music/MusicSearchView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/music/upload',
    name: 'MusicUpload',
    component: () => import('@/views/music/MusicUploadView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/playlists',
    name: 'Playlists',
    component: () => import('@/views/playlists/PlaylistsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/playlists/:id',
    name: 'PlaylistDetail',
    component: () => import('@/views/playlists/PlaylistDetailView.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  
  // === ROTAS DE USUÁRIO ===
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/admin/UsersView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  
  // === ROTA 404 ===
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Guards de navegação
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Verificar se o usuário está autenticado
  if (!authStore.isAuthenticated && authStore.token) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      authStore.logout()
    }
  }
  
  // Verificar se a rota requer autenticação
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // Verificar se a rota requer que o usuário não esteja autenticado
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }
  
  // Verificar se a rota requer privilégios de admin
  if (to.meta.requiresAdmin && (!authStore.user || !authStore.user.is_admin)) {
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router 