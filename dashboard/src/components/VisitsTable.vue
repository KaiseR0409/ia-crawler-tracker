<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: null } })
const emit = defineEmits(['page'])

const rows = computed(() => props.data?.visits ?? [])
const page = computed(() => props.data?.page ?? 1)
const pages = computed(() => props.data?.pages ?? 1)
const total = computed(() => props.data?.total ?? 0)

const typeProps = {
    crawler: { color: 'secondary', icon: 'mdi-robot-outline' },
    referral: { color: 'success', icon: 'mdi-web' },
    unknown: { color: 'grey', icon: 'mdi-help-circle-outline' },
}

function fmtDate(ts) {
    const d = new Date(ts)
    return d.toLocaleString('es', { dateStyle: 'medium', timeStyle: 'short' })
}

function typeInfo(type) {
    return typeProps[type] ?? typeProps.unknown
}

function truncate(text, len = 60) {
    if (!text) return '—'
    return text.length > len ? text.slice(0, len - 1) + '…' : text
}
</script>

<template>
    <v-card rounded="xl" variant="elevated">
        <v-card-title class="d-flex align-center px-5 pt-5 pb-0 text-subtitle-1 font-weight-bold">
            <v-icon color="primary" class="mr-2">mdi-table-large</v-icon>
            Registro de visitas
            <v-spacer />
            <v-chip size="small" variant="tonal" class="d-none d-sm-inline-flex">
                {{ total }} registros
            </v-chip>
        </v-card-title>

        <v-card-text class="pa-4">
            <div class="table-scroll">
                <table class="mtable">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Tráfico</th>
                            <th>Proveedor</th>
                            <th>URL de destino</th>
                            <th class="d-none d-md-table-cell">User Agent</th>
                            <th class="d-none d-md-table-cell">Referrer</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(v, i) in rows" :key="i" class="mtable-row">
                            <td class="text-body-2" nowrap>{{ fmtDate(v.timestamp) }}</td>
                            <td>
                                <v-chip
                                    :color="typeInfo(v.traffic_type).color"
                                    size="small"
                                    variant="tonal"
                                    density="comfortable"
                                >
                                    <v-icon size="14" class="mr-1">{{ typeInfo(v.traffic_type).icon }}</v-icon>
                                    {{ v.traffic_type }}
                                </v-chip>
                            </td>
                            <td class="text-body-2 font-weight-medium" nowrap>{{ v.ai_provider }}</td>
                            <td class="text-body-2 url-cell" :title="v.target_url">{{ truncate(v.target_url) }}</td>
                            <td class="text-body-2 text-medium-emphasis d-none d-md-table-cell" :title="v.user_agent">
                                {{ truncate(v.user_agent) }}
                            </td>
                            <td class="text-body-2 text-medium-emphasis d-none d-md-table-cell" :title="v.referrer">
                                {{ truncate(v.referrer) }}
                            </td>
                        </tr>
                        <tr v-if="!rows.length">
                            <td colspan="6" class="text-center text-medium-emphasis py-10">
                                <v-icon class="mb-2" size="40">mdi-inbox-outline</v-icon>
                                <div class="text-body-2">Aún no hay visitas registradas</div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="d-flex align-center justify-end mt-4 ga-2">
                <span class="text-body-2 text-medium-emphasis mr-2">
                    Página {{ page }} de {{ pages }}
                </span>
                <v-btn
                    variant="outlined"
                    size="small"
                    rounded="lg"
                    :disabled="page <= 1"
                    :title="'Anterior'"
                    @click="emit('page', page - 1)"
                >
                    <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <v-btn
                    variant="outlined"
                    size="small"
                    rounded="lg"
                    :disabled="page >= pages || !pages"
                    title="Siguiente"
                    @click="emit('page', page + 1)"
                >
                    <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.table-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.mtable {
    width: 100%;
    border-collapse: collapse;
    white-space: nowrap;
}
.mtable th {
    text-align: left;
    padding: 8px 12px;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: rgb(var(--v-theme-on-surface-variant));
    background: rgb(var(--v-theme-surface-variant));
    border-radius: 8px;
}
.mtable th:first-child,
.mtable td:first-child {
    padding-left: 16px;
}
.mtable th:last-child,
.mtable td:last-child {
    padding-right: 16px;
}
.mtable-row td {
    padding: 12px;
    border-bottom: 1px solid rgb(var(--v-theme-outline));
}
.mtable-row:last-child td {
    border-bottom: none;
}
.mtable-row:hover td {
    background: rgb(var(--v-theme-surface-variant))cc;
}
.url-cell {
    max-width: 260px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>