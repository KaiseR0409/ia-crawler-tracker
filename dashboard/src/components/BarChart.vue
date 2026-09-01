<script setup>
import { computed } from 'vue'
import { useTheme } from 'vuetify'
import {
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
} from 'chart.js'
import { Bar } from 'vue-chartjs'

const props = defineProps({ stats: { type: Object, default: null } })

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip)

const theme = useTheme()
const isDark = computed(() => theme.global.name.value === 'dark')

const labels = computed(() => props.stats?.by_provider?.map(p => p.ai_provider) ?? [])
const counts = computed(() => props.stats?.by_provider?.map(p => p.count) ?? [])

const accent = computed(() => isDark.value ? 'rgba(129, 140, 248, 0.9)' : 'rgba(79, 70, 229, 0.9)')
const accentSoft = computed(() => isDark.value ? 'rgba(129, 140, 248, 0.25)' : 'rgba(79, 70, 229, 0.18)')
const grid = computed(() => isDark.value ? 'rgba(148, 163, 184, 0.14)' : 'rgba(100, 116, 139, 0.14)')
const tick = computed(() => isDark.value ? '#CBD5E1' : '#64748B')
const tooltipBg = computed(() => isDark.value ? '#1E293B' : '#0F172A')

const chartData = computed(() => ({
    labels: labels.value,
    datasets: [
        {
            label: 'Visitas',
            data: counts.value,
            backgroundColor: accent.value,
            hoverBackgroundColor: accent.value,
            borderRadius: 8,
            borderSkipped: false,
            maxBarThickness: 48,
            hoverBorderColor: accentSoft.value,
        },
    ],
}))

const chartOptions = computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800, easing: 'easeOutQuart' },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: tooltipBg.value,
            padding: 10,
            cornerRadius: 8,
            titleColor: '#F8FAFC',
            bodyColor: '#E2E8F0',
            displayColors: false,
        },
    },
    scales: {
        x: {
            grid: { display: false },
            ticks: { color: tick.value, font: { size: 12 } },
        },
        y: {
            beginAtZero: true,
            grid: { color: grid.value },
            border: { display: false },
            ticks: { color: tick.value, precision: 0 },
        },
    },
}))
</script>

<template>
    <v-card rounded="xl" variant="elevated" class="fill-height">
        <v-card-title class="d-flex align-center px-5 pt-5 pb-0 text-subtitle-1 font-weight-bold">
            <v-icon color="primary" class="mr-2">mdi-chart-bar</v-icon>
            Visitas por proveedor AI
        </v-card-title>
        <v-card-text class="px-4 pb-4 pt-2">
            <div class="chart-box">
                <Bar :data="chartData" :options="chartOptions" />
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.chart-box {
    height: 360px;
    width: 100%;
}
</style>