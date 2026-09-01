// session-based api client; the dashboard is served same-origin by FastAPI,
// so the api key never reaches the browser — only the httpOnly session cookie.

export async function login(apiKey) {
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
    })
    if (!response.ok) throw new Error('Invalid API key')
}

export async function logout() {
    await fetch('/api/logout', { method: 'POST' })
}

export async function authStatus() {
    const response = await fetch('/api/auth/status')
    const data = await response.json()
    return data.authenticated
}

async function get(url) {
    const response = await fetch(url)
    if (response.status === 401) {
        window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        throw new Error('Sesión expirada')
    }
    if (!response.ok) throw new Error(`Error ${response.status}`)
    return response.json()
}

export const fetchStats = () => get('/api/stats')
export const fetchVisits = (page = 1, limit = 10) => get(`/api/visits?page=${page}&limit=${limit}`)