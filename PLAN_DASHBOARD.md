# Plan: Dashboard Vue3 para ia-crawler-tracker

## Estado Actual
- Backend FastAPI funcional en puerto 5000
- Endpoints: `/track`, `/visits` (sin paginación), `/stats`, `/tracker.js`
- Base de datos SQLite con tabla `visits` vacía
- Sin frontend/dashboard todavía

## Lo que el usuario quiere ver
1. **Gráfico de barras** → cada bot/ai_provider y su cantidad de visitas
2. **Tabla histórica con paginación** → todas las visitas con paginación desde `/visits`
3. **Cards de stats** → métricas resumidas (total, crawlers, referrals, últimos 24h)

---

## Fase 1: Mejoras al Backend (Python)

### 1.1 Nuevo endpoint: `/visits` con paginación
El endpoint actual devuelve TODO sin paginación. Necesitamos soporte para:
- `?page=1&limit=20` (parámetros de query)
- Respuesta con `{ visits: [...], total: N, page: N, pages: N }`

**Archivo:** `app/main.py` - modificar endpoint `GET /visits`

### 1.2 Nuevo endpoint: `/stats/by-bot`
El endpoint `/stats` ya agrupa por `ai_provider`, pero para el gráfico de barras
necesitamos un desglose más detallado que incluya también el `user_agent_token` específico.

**Opción:** Reutilizar `/stats` existente que ya retorna `by_provider` con conteos.
→ Decisión: Usar `/stats` tal como está, el `by_provider` ya da lo necesario para el gráfico.

---

## Fase 2: Setup del Proyecto Vue3

### 2.1 Estructura de archivos
```
ia-crawler-tracker/
├── app/                    (backend existente)
├── dashboard/              ← NUEVO: frontend Vue3
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── style.css
│   │   ├── api.js              (servicio para llamar al backend)
│   │   ├── components/
│   │   │   ├── BarChart.vue     (gráfico de barras por bot)
│   │   │   ├── StatsCards.vue   (tarjetas de métricas)
│   │   │   └── VisitsTable.vue  (tabla paginada)
│   │   └── assets/
│   └── public/
```

### 2.2 Dependencias
- `vue` (core)
- `vite` + `@vitejs/plugin-vue` (build tool)
- `chart.js` + `vue-chartjs` (para el gráfico de barras)

### 2.3 Vite proxy
Configurar proxy en `vite.config.js` para que las llamadas a `/api` se redirijan
a `http://localhost:5000` — así evitamos problemas de CORS en desarrollo.

---

## Fase 3: Componentes del Dashboard

### 3.1 `api.js` - Servicio de comunicación
Funciones:
- `fetchStats()` → `GET /stats` con Authorization header
- `fetchVisits(page, limit)` → `GET /visits?page=N&limit=N` con Authorization header

### 3.2 `BarChart.vue` - Gráfico de barras
- Recibe datos de `stats.by_provider`
- Muestra barras horizontales/verticales con el nombre del bot y su conteo
- Colores diferenciados por tipo (crawler vs referral si es posible)
- Librería: Chart.js via vue-chartjs

### 3.3 `StatsCards.vue` - Tarjetas de métricas
- 4 tarjetas: Total visits, Crawlers, Referrals, Últimas 24h
- Datos de `stats.total`, `stats.by_type`, `stats.recent_24h`
- Estilo limpio con iconos/colores

### 3.4 `VisitsTable.vue` - Tabla paginada
- Columnas: Timestamp, Target URL, Traffic Type, AI Provider, User Agent, Referrer
- Paginación con botones Previous/Next + indicador de página
- Recibe datos de `fetchVisits(page, limit)`

---

## Fase 4: Integración y Pruebas

### 4.1 Datos de prueba
- Insertar visitas de prueba en la BD para verificar que el dashboard muestra datos reales
- Script curl o directamente con Python para insertar registros fake

### 4.2 Verificación
- Levantar backend: `docker-compose up` o `uvicorn app.main:app`
- Levantar dashboard: `npm run dev` en `/dashboard`
- Verificar que:
  - El gráfico muestra los bots con sus conteos
  - La tabla pagina correctamente
  - Las stats cards muestran datos correctos

---

## Orden de ejecución
1. Modificar backend: paginación en `/visits`
2. Crear proyecto Vue3 con Vite
3. Implementar `api.js`
4. Implementar `StatsCards.vue`
5. Implementar `BarChart.vue`
6. Implementar `VisitsTable.vue`
7. Armar `App.vue` con el layout
8. Insertar datos de prueba
9. Probar todo junto
