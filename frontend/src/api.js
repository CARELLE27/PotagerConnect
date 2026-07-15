const BASE = '/api'

function getToken() {
  return localStorage.getItem('access_token')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth && getToken()) headers.Authorization = `Bearer ${getToken()}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) return null

  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    const err = new Error(data.detail || 'Une erreur est survenue')
    err.status = res.status
    throw err
  }
  return data
}

export const api = {
  register: (b) => request('/auth/register', { method: 'POST', body: b, auth: false }),
  login: (b) => request('/auth/login', { method: 'POST', body: b, auth: false }),
  me: () => request('/auth/me'),

  listeParcelles: () => request('/parcelles'),
  mesParcelles: () => request('/parcelles/mes-parcelles'),
  detailParcelle: (id) => request(`/parcelles/${id}`),
  attribuer: (id, userId) =>
    request(`/parcelles/${id}/attribuer`, { method: 'PATCH', body: { user_id: userId } }),
  liberer: (id) => request(`/parcelles/${id}/liberer`, { method: 'PATCH' }),
  listeJardiniers: () => request('/users'),

  creerCulture: (parcelleId, b) =>
    request(`/parcelles/${parcelleId}/cultures`, { method: 'POST', body: b }),
  recolter: (id) => request(`/cultures/${id}/recolter`, { method: 'PATCH' }),
  supprimerCulture: (id) => request(`/cultures/${id}`, { method: 'DELETE' }),
  suggestions: (parcelleId) =>
    request(`/suggestions${parcelleId ? `?parcelle_id=${parcelleId}` : ''}`),


  listePhotos: (cultureId) => request(`/cultures/${cultureId}/photos`),
  ajouterPhoto: (cultureId, b) =>
    request(`/cultures/${cultureId}/photos`, { method: 'POST', body: b }),
  supprimerPhoto: (id) => request(`/photos/${id}`, { method: 'DELETE' }),

  listeRecoltes: (statut) =>
    request(`/recoltes${statut ? `?statut=${statut}` : ''}`),
  proposerRecolte: (b) => request('/recoltes', { method: 'POST', body: b }),
  reserverRecolte: (id) => request(`/recoltes/${id}/reserver`, { method: 'PATCH' }),
  annulerRecolte: (id) => request(`/recoltes/${id}`, { method: 'DELETE' }),

  meteo: () => request('/meteo'),


  listePosts: (type) => request(`/forum${type ? `?type=${type}` : ''}`),
  creerPost: (b) => request('/forum', { method: 'POST', body: b }),
  detailPost: (id) => request(`/forum/${id}`),
  commenter: (id, b) => request(`/forum/${id}/commentaires`, { method: 'POST', body: b }),
  supprimerPost: (id) => request(`/forum/${id}`, { method: 'DELETE' }),

}

export { getToken }
