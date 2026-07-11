import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setChargement(false)
      return
    }
    api
      .me()
      .then(setUser)
      .catch(() => localStorage.removeItem('access_token'))
      .finally(() => setChargement(false))
  }, [])

  async function connexion(email, password) {
    const tokens = await api.login({ email, password })
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    setUser(await api.me())
  }

  function deconnexion() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, chargement, connexion, deconnexion }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth doit etre utilise dans un AuthProvider')
  return ctx
}
