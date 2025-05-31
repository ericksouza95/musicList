<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-6" elevation="8">
          <v-card-title class="text-center mb-4">
            <v-icon class="mr-2" color="primary">mdi-account-plus</v-icon>
            <span class="text-h4">Criar Conta</span>
          </v-card-title>

          <v-form @submit.prevent="handleSubmit" ref="form">
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="form.first_name"
                  label="Nome"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="form.last_name"
                  label="Sobrenome"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>
            </v-row>

            <v-text-field
              v-model="form.username"
              label="Nome de usuário"
              prepend-inner-icon="mdi-account-circle"
              variant="outlined"
              :rules="[rules.required, rules.username]"
              required
            />

            <v-text-field
              v-model="form.email"
              label="E-mail"
              type="email"
              prepend-inner-icon="mdi-email"
              variant="outlined"
              :rules="[rules.required, rules.email]"
              required
            />

            <v-text-field
              v-model="form.password"
              label="Senha"
              :type="showPassword ? 'text' : 'password'"
              prepend-inner-icon="mdi-lock"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPassword = !showPassword"
              variant="outlined"
              :rules="[rules.required, rules.password]"
              required
            />

            <v-text-field
              v-model="form.confirmPassword"
              label="Confirmar senha"
              :type="showConfirmPassword ? 'text' : 'password'"
              prepend-inner-icon="mdi-lock-check"
              :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showConfirmPassword = !showConfirmPassword"
              variant="outlined"
              :rules="[rules.required, rules.confirmPassword]"
              required
            />

            <div class="mt-6">
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="authStore.isLoading"
                :disabled="!isFormValid"
              >
                Criar Conta
              </v-btn>
            </div>

            <div class="mt-4 text-center">
              <span class="text-body-2">Já tem uma conta?</span>
              <router-link to="/login" class="text-primary ml-1">
                Faça login
              </router-link>
            </div>
          </v-form>
        </v-card>
      </v-col>
    </v-row>

    <!-- Debug panel -->
    <v-card v-if="showDebug" class="mt-4 pa-4" color="grey-lighten-4">
      <v-card-title class="text-caption">Debug Info</v-card-title>
      <pre class="text-caption">{{ debugInfo }}</pre>
    </v-card>

    <!-- Snackbar de erro -->
    <v-snackbar
      v-model="showError"
      color="error"
      timeout="5000"
      location="top"
    >
      {{ errorMessage }}
      <template #actions>
        <v-btn variant="text" @click="showError = false">Fechar</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  first_name: '',
  last_name: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const showDebug = ref(false)

const rules = {
  required: (value) => !!value || 'Campo obrigatório',
  email: (value) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || 'E-mail inválido'
  },
  username: (value) => {
    if (!value) return 'Nome de usuário é obrigatório'
    if (value.length < 3) return 'Nome de usuário deve ter pelo menos 3 caracteres'
    if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Use apenas letras, números e underscore'
    return true
  },
  password: (value) => {
    if (!value) return 'Senha é obrigatória'
    if (value.length < 6) return 'Senha deve ter pelo menos 6 caracteres'
    return true
  },
  confirmPassword: (value) => {
    if (!value) return 'Confirmação de senha é obrigatória'
    if (value !== form.value.password) return 'Senhas não conferem'
    return true
  }
}

const isFormValid = computed(() => {
  return (
    form.value.username &&
    form.value.email &&
    form.value.password &&
    form.value.confirmPassword &&
    form.value.first_name &&
    form.value.last_name &&
    form.value.password === form.value.confirmPassword &&
    rules.email(form.value.email) === true &&
    rules.username(form.value.username) === true &&
    rules.password(form.value.password) === true
  )
})

const debugInfo = computed(() => ({
  form: form.value,
  isFormValid: isFormValid.value,
  loading: authStore.isLoading,
  errors: errorMessage.value
}))

const handleSubmit = async () => {
  if (!isFormValid.value) {
    errorMessage.value = 'Por favor, preencha todos os campos corretamente'
    showError.value = true
    return
  }

  try {
    showDebug.value = true
    
    const userData = {
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      first_name: form.value.first_name,
      last_name: form.value.last_name
    }

    console.log('Enviando dados de registro:', userData)

    await authStore.register(userData)
    
    // Sucesso - redirecionar
    router.push('/')
  } catch (error) {
    console.error('Erro no registro:', error)
    
    // Extrair mensagem de erro
    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error
    } else if (error.response?.data?.message) {
      errorMessage.value = error.response.data.message
    } else if (error.message) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Erro ao criar conta. Tente novamente.'
    }
    
    showError.value = true
  }
}

// Ativar debug em desenvolvimento
if (import.meta.env.DEV) {
  showDebug.value = true
}
</script> 