<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { authStatus, logout } from './api/api'
import { useThemeMode } from './composables/useTheme'
import LoginView from './views/LoginView.vue'
import Dashboard from './views/Dashboard.vue'

const authenticated = ref(null)
const { isDark, toggle } = useThemeMode()

onMounted(async () => {
    try { authenticated.value = await authStatus() } catch { authenticated.value = false }
    window.addEventListener('auth:unauthorized', onUnauthorized)
})
onUnmounted(() => window.removeEventListener('auth:unauthorized', onUnauthorized))

function onUnauthorized() {
    authenticated.value = false
}

async function onLogout() {
    try { await logout() } finally { authenticated.value = false }
}
</script>

<template>
    <v-app>
        <v-app-bar flat color="background" height="64" class="app-bar">
            <v-app-bar-title class="d-flex align-center">
                <v-icon color="primary" class="mr-2">mdi-radar</v-icon>
                <span class="font-weight-bold">Creawler</span>
                <span class="text-medium-emphasis ml-3 text-body-2 d-none d-sm-inline">AI traffic tracker</span>
            </v-app-bar-title>
            <template v-slot:append>
                <v-btn variant="text" density="comfortable" icon :title="isDark ? 'Cambiar a claro' : 'Cambiar a oscuro'" @click="toggle">
                    <v-icon>{{ isDark ? 'mdi-white-balance-sunny' : 'mdi-weather-night' }}</v-icon>
                </v-btn>
                <v-btn
                    v-if="authenticated"
                    variant="text"
                    density="comfortable"
                    icon
                    title="Cerrar sesión"
                    class="pl-1"
                    @click="onLogout"
                >
                    <v-icon>mdi-logout-variant</v-icon>
                </v-btn>
            </template>
        </v-app-bar>

        <v-main>
            <v-container
                v-if="authenticated === null"
                class="d-flex justify-center align-center"
                style="min-height: 60vh"
            >
                <v-progress-circular indeterminate color="primary" />
            </v-container>
            <LoginView v-else-if="!authenticated" @authed="authenticated = true" />
            <Dashboard v-else />
        </v-main>
    </v-app>
</template>

<style scoped>
.app-bar {
    border-bottom: 1px solid rgb(var(--v-theme-outline));
}
</style>