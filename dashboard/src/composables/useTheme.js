import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useTheme } from 'vuetify'

const STORAGE_KEY = 'creawler-theme'
const mq = window.matchMedia('(prefers-color-scheme: dark)')

// defaults to the OS preference; once toggled by the user, that choice persists
export function useThemeMode() {
    const theme = useTheme()
    const stored = localStorage.getItem(STORAGE_KEY)
    const isDark = ref(stored ? stored === 'dark' : mq.matches)

    function toggle() {
        isDark.value = !isDark.value
        localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
    }

    watch(isDark, (dark) => {
        theme.global.name.value = dark ? 'dark' : 'light'
    }, { immediate: true })

    onMounted(() => {
        if (!stored) {
            const onChange = (e) => {
                if (!localStorage.getItem(STORAGE_KEY)) isDark.value = e.matches
            }
            mq.addEventListener('change', onChange)
            onUnmounted(() => mq.removeEventListener('change', onChange))
        }
    })

    return { isDark, toggle }
}