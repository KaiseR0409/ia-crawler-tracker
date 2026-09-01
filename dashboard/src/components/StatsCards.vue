<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({ stats: { type: Object, default: null } })

const total = computed(() => props.stats?.total ?? 0)
const crawlers = computed(() => props.stats?.by_type?.find(t => t.traffic_type === 'crawler')?.count ?? 0)
const referrals = computed(() => props.stats?.by_type?.find(t => t.traffic_type === 'referral')?.count ?? 0)
const recent24h = computed(() => props.stats?.recent_24h ?? 0)

function useCountUp(target) {
    const display = ref(0)
    watch(target, (val) => {
        const from = display.value
        const to = val ?? 0
        const diff = to - from
        if (!diff) return
        const start = performance.now()
        const duration = 500
        function frame(now) {
            const p = Math.min(1, (now - start) / duration)
            display.value = Math.round(from + diff * (1 - Math.pow(1 - p, 3)))
            if (p < 1) requestAnimationFrame(frame)
        }
        requestAnimationFrame(frame)
    }, { immediate: true })
    return display
}

const totalShown = useCountUp(total)
const crawlersShown = useCountUp(crawlers)
const referralsShown = useCountUp(referrals)
const recentShown = useCountUp(recent24h)

const cards = computed(() => [
    { label: 'Visitas totales', value: totalShown.value, icon: 'mdi-chart-box', color: 'primary' },
    { label: 'Crawlers', value: crawlersShown.value, icon: 'mdi-robot-outline', color: 'secondary' },
    { label: 'Referidos', value: referralsShown.value, icon: 'mdi-web', color: 'success' },
    { label: 'Últimas 24h', value: recentShown.value, icon: 'mdi-clock-outline', color: 'warning' },
])
</script>

<template>
    <v-row no-gutters class="mx-n2">
        <v-col
            v-for="card in cards"
            :key="card.label"
            cols="12" sm="6" lg="3"
            class="pa-2"
        >
            <v-card rounded="xl" variant="elevated" class="stat-card">
                <v-card-text class="d-flex align-center pa-4">
                    <v-avatar :color="card.color" size="46" class="mr-4" variant="tonal">
                        <v-icon :color="card.color">{{ card.icon }}</v-icon>
                    </v-avatar>
                    <div class="min-w-0">
                        <div class="text-caption text-medium-emphasis text-truncate">{{ card.label }}</div>
                        <div class="text-h4 font-weight-bold">{{ card.value.toLocaleString('es') }}</div>
                    </div>
                </v-card-text>
            </v-card>
        </v-col>
    </v-row>
</template>

<style scoped>
.stat-card {
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stat-card:hover {
    transform: translateY(-2px);
}
</style>