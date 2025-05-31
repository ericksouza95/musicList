import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

const musicTheme = {
  dark: false,
  colors: {
    primary: '#1976D2',
    secondary: '#424242',
    accent: '#82B1FF',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFC107',
    background: '#FAFAFA',
    surface: '#FFFFFF',
    'primary-darken-1': '#1565C0',
    'secondary-darken-1': '#1976D2',
  }
}

const musicDarkTheme = {
  dark: true,
  colors: {
    primary: '#2196F3',
    secondary: '#424242',
    accent: '#FF4081',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFC107',
    background: '#121212',
    surface: '#1E1E1E',
    'primary-darken-1': '#1976D2',
    'secondary-darken-1': '#1565C0',
  }
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'musicTheme',
    themes: {
      musicTheme,
      musicDarkTheme,
    },
  },
  defaults: {
    VCard: {
      elevation: 2,
    },
    VBtn: {
      elevation: 2,
    },
    VAppBar: {
      elevation: 1,
    },
  },
}) 