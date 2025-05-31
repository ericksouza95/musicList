<template>
  <v-container class="pa-6">
    <h1 class="text-h4 font-weight-bold mb-6">
      <v-icon class="mr-2">mdi-account-group</v-icon>
      Gerenciar Usuários
    </h1>

    <v-card>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="users"
          :loading="loading"
          item-value="id"
        >
          <template #item.is_admin="{ item }">
            <v-chip
              :color="item.is_admin ? 'success' : 'default'"
              size="small"
            >
              {{ item.is_admin ? 'Admin' : 'Usuário' }}
            </v-chip>
          </template>

          <template #item.actions="{ item }">
            <v-btn
              icon="mdi-pencil"
              variant="text"
              size="small"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const users = ref([])
const loading = ref(false)

const headers = [
  { title: 'Nome', key: 'full_name' },
  { title: 'Email', key: 'email' },
  { title: 'Tipo', key: 'is_admin' },
  { title: 'Criado em', key: 'created_at' },
  { title: 'Ações', key: 'actions', sortable: false }
]

onMounted(() => {
  // Carregar usuários
  users.value = []
})
</script> 