// Test de charge k6 - J8 matin
// Usage : k6 run -e BASE_URL=https://potagerconnect.example.fr loadtest/charge.js
import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 50 },   // 50 utilisateurs simultanes
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'],   // p95 sous 800 ms
    http_req_failed: ['rate<0.01'],     // moins de 1% d'erreurs
  },
}

const BASE = __ENV.BASE_URL || 'http://localhost:8000'

export function setup() {
  const res = http.post(
    `${BASE}/auth/login`,
    JSON.stringify({ email: 'aicha.kone@potager.fr', password: 'Jardin2026!' }),
    { headers: { 'Content-Type': 'application/json' } }
  )
  return { token: res.json('access_token') }
}

export default function (data) {
  const params = { headers: { Authorization: `Bearer ${data.token}` } }

  const r1 = http.get(`${BASE}/parcelles/mes-parcelles`, params)
  check(r1, { 'mes-parcelles 200': (r) => r.status === 200 })

  const r2 = http.get(`${BASE}/suggestions`, params)
  check(r2, { 'suggestions 200': (r) => r.status === 200 })

  sleep(1)
}
