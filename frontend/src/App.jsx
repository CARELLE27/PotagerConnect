import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Entete from './components/Entete'
import Login from './pages/Login'
import CarteParcelles from './pages/CarteParcelles'
import MaParcelle from './pages/MaParcelle'
import PartageRecoltes from './pages/PartageRecoltes'

import Forum from './pages/Forum'


function RouteProtegee({ children, adminSeulement = false }) {
  const { user, chargement } = useAuth()
  if (chargement) return <p className="vide">Chargement...</p>
  if (!user) return <Navigate to="/login" replace />
  if (adminSeulement && user.role !== 'admin') return <Navigate to="/ma-parcelle" replace />
  return children
}

export default function App() {
  const { user, chargement } = useAuth()
  if (chargement) return <p className="vide">Chargement...</p>

  return (
    <>
      {user && <Entete />}
      <main className="contenu">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
          <Route
            path="/parcelles"
            element={
              <RouteProtegee adminSeulement>
                <CarteParcelles />
              </RouteProtegee>
            }
          />
          <Route
            path="/ma-parcelle"
            element={
              <RouteProtegee>
                <MaParcelle />
              </RouteProtegee>
            }
          />
          <Route
            path="/recoltes"
            element={
              <RouteProtegee>
                <PartageRecoltes />
              </RouteProtegee>
            }
          />
          <Route

            path="/forum"
            element={
              <RouteProtegee>
                <Forum />
              </RouteProtegee>
            }
          />
          <Route

            path="/"
            element={
              <Navigate to={user?.role === 'admin' ? '/parcelles' : '/ma-parcelle'} replace />
            }
          />
        </Routes>
      </main>
    </>
  )
}
