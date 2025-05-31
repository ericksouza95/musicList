<template>
  <v-container fluid class="fill-height login-container">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="login-card" elevation="8">
          <v-card-title class="text-center pa-6">
            <div class="login-header">
              <v-icon size="48" color="primary" class="mb-4">mdi-music</v-icon>
              <h1 class="text-h4 font-weight-light">Music List</h1>
              <p class="text-subtitle-1 text-medium-emphasis mt-2">
                Faça login para acessar suas músicas
              </p>
            </div>
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid" @submit.prevent="handleLogin">
              <v-text-field
                v-model="credentials.login"
                label="Email ou Nome de usuário"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="loginRules"
                :error-messages="errors.login"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="credentials.password"
                label="Senha"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                variant="outlined"
                :rules="passwordRules"
                :error-messages="errors.password"
                class="mb-4"
                required
                @click:append-inner="showPassword = !showPassword"
              />

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="authStore.isLoading"
                :disabled="!valid"
                class="mb-4"
              >
                Entrar
              </v-btn>
            </v-form>

            <div class="text-center">
              <v-btn
                variant="text"
                color="primary"
                @click="$router.push('/register')"
              >
                Não tem uma conta? Cadastre-se
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const form = ref(null)
const valid = ref(false)
const showPassword = ref(false)

const credentials = reactive({
  login: '',
  password: ''
})

const errors = reactive({
  login: [],
  password: []
})

const loginRules = [
  v => !!v || 'Email ou nome de usuário é obrigatório',
  v => v.length >= 3 || 'Deve ter pelo menos 3 caracteres'
]

const passwordRules = [
  v => !!v || 'Senha é obrigatória',
  v => v.length >= 6 || 'Senha deve ter pelo menos 6 caracteres'
]

const handleLogin = async () => {
  // Limpar erros anteriores
  errors.login = []
  errors.password = []

  if (!form.value.validate()) {
    return
  }

  try {
    await authStore.login(credentials)
    
    // Redirecionar para a página solicitada ou home
    const redirectTo = route.query.redirect || '/'
    router.push(redirectTo)
  } catch (error) {
    console.error('Erro no login:', error)
    
    // Tratar erros específicos
    if (error.response?.status === 401) {
      errors.login = ['Credenciais inválidas']
      errors.password = ['Credenciais inválidas']
    } else if (error.response?.status === 403) {
      errors.login = ['Conta desativada']
    }
  }
}
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.login-card {
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
}

.v-card-title {
  padding-bottom: 0 !important;
}

.v-text-field {
  margin-bottom: 8px;
}

@media (max-width: 600px) {
  .login-card {
    margin: 16px;
  }
}
</style> 