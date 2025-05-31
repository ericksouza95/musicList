<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" class="text-center">
        <v-icon size="120" color="grey">mdi-music-off</v-icon>
        <h1 class="text-h2 font-weight-bold mt-4 mb-2">404</h1>
        <h2 class="text-h4 mb-4">Página não encontrada</h2>
        <p class="text-subtitle-1 text-medium-emphasis mb-6">
          A página que você está procurando não existe ou foi movida.
        </p>
        <v-btn
          color="primary"
          size="large"
          @click="$router.push('/')"
        >
          <v-icon start>mdi-home</v-icon>
          Voltar ao Início
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Página 404 - sem lógica adicional necessária
</script> 