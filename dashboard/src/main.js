import { createApp } from 'vue'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import './style.css'
import App from './App.vue'

const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'light',
        themes: {
            light: {
                dark: false,
                colors: {
                    primary: '#4F46E5',
                    secondary: '#0EA5E9',
                    success: '#16A34A',
                    warning: '#D97706',
                    error: '#DC2626',
                    background: '#F5F6FA',
                    surface: '#FFFFFF',
                    'on-surface': '#111827',
                    'on-background': '#111827',
                    'surface-variant': '#EEF0F6',
                    'on-surface-variant': '#475569',
                    outline: '#CBD5E1',
                },
            },
            dark: {
                dark: true,
                colors: {
                    primary: '#818CF8',
                    secondary: '#38BDF8',
                    success: '#22C55E',
                    warning: '#FBBF24',
                    error: '#F87171',
                    background: '#0B0F19',
                    surface: '#131B2E',
                    'on-surface': '#E2E8F0',
                    'on-background': '#E2E8F0',
                    'surface-variant': '#1E293B',
                    'on-surface-variant': '#94A3B8',
                    outline: '#334155',
                },
            },
        },
    },
})

createApp(App).use(vuetify).mount('#app')