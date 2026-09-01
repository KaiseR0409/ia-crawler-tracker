<script setup>
import { ref } from 'vue'
import { login } from '../api/api'

const emit = defineEmits(['authed'])
const apiKey = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
    if (!apiKey.value.trim()) return
    error.value = ''
    loading.value = true
    try {
        await login(apiKey.value.trim())
        emit('authed')
    } catch {
        error.value = 'Clave API incorrecta'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <v-container class="d-flex justify-center align-center" style="min-height: 70vh">
        <v-card
            class="mx-auto"
            width="100%"
            max-width="400"
            rounded="xl"
            variant="elevated"
        >
            <v-card-item class="text-center pt-8">
                <v-avatar color="primary" size="64" class="mb-4 mx-auto">
                    <v-icon size="34" color="white">mdi-radar</v-icon>
                </v-avatar>
                <div class="text-h5 font-weight-bold">Creawler</div>
                <div class="text-body-2 text-medium-emphasis mt-1">Acceso al dashboard</div>
            </v-card-item>

            <v-card-text class="px-8 pb-8 pt-4">
                <v-form @submit.prevent="submit">
                    <v-text-field
                        v-model="apiKey"
                        label="Clave API"
                        type="password"
                        variant="outlined"
                        density="comfortable"
                        :append-inner-icon="'mdi-key-variant'"
                        :error-messages="error"
                        autocomplete="current-password"
                        @keyup.enter="submit"
                    />
                    <v-btn
                        block
                        color="primary"
                        size="large"
                        rounded="lg"
                        :loading="loading"
                        @click="submit"
                    >
                        Entrar
                    </v-btn>
                </v-form>
            </v-card-text>
        </v-card>
    </v-container>
</template>