<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchStats, fetchVisits } from '../api/api'
import StatsCards from '../components/StatsCards.vue'
import BarChart from '../components/BarChart.vue'
import VisitsTable from '../components/VisitsTable.vue'

const stats = ref(null)
const visits = ref(null)
let timer

async function loadStats() {
    try { stats.value = await fetchStats() } catch { /* 401 handled globally */ }
}

async function loadVisits(page = 1) {
    try {
        const data = await fetchVisits(page, 10)
        visits.value = data
    } catch { /* 401 handled globally */ }
}

async function refresh() {
    await Promise.all([loadStats(), loadVisits(visits.value?.page ?? 1)])
}

function onChangePage(page) {
    loadVisits(page)
}

onMounted(() => {
    refresh()
    timer = setInterval(refresh, 30000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
    <v-container fluid class="py-6 px-4 px-sm-8">
        <StatsCards :stats="stats" />
        <div class="mt-6">
            <BarChart :stats="stats" />
        </div>
        <div class="mt-6">
            <VisitsTable :data="visits" @page="onChangePage" />
        </div>
    </v-container>
</template>