<template>
  <v-container class="pa-6">
    <h1 class="text-h4 font-weight-bold mb-6">
      <v-icon class="mr-2">mdi-account</v-icon>
      Meu Perfil
    </h1>

    <v-card>
      <v-card-text>
        <v-form>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.firstName"
                label="Nome"
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.lastName"
                label="Sobrenome"
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-text-field
            v-model="form.email"
            label="Email"
            variant="outlined"
            type="email"
          />

          <v-btn color="primary" class="mt-4">
            Salvar Alterações
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  firstName: '',
  lastName: '',
  email: ''
})
</script> 