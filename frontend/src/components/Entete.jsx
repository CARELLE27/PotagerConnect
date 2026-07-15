import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Entete() {
  const { user, deconnexion } = useAuth()
  const { pathname } = useLocation()

  const lienStyle = (actif) => ({
    fontSize: 14,
    textDecoration: 'none',
    color: actif ? 'var(--vert)' : 'var(--gris)',
    fontWeight: actif ? 500 : 400,
    padding: '4px 0',
    borderBottom: actif ? '2px solid var(--vert)' : '2px solid transparent',
  })

  return (
    <header className="entete">
      <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        <strong>PotagerConnect</strong>
        <nav style={{ display: 'flex', gap: 16 }}>
          {user.role === 'admin' ? (
            <Link to="/parcelles" style={lienStyle(pathname === '/parcelles')}>Parcelles</Link>
          ) : (
            <Link to="/ma-parcelle" style={lienStyle(pathname === '/ma-parcelle')}>Ma parcelle</Link>
          )}
          <Link to="/recoltes" style={lienStyle(pathname === '/recoltes')}>Recoltes partagees</Link>
          <Link to="/forum" style={lienStyle(pathname === '/forum')}>Forum</Link>

        </nav>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 14, color: 'var(--gris)' }}>
          {user.prenom} {user.nom} — {user.role === 'admin' ? 'Responsable' : 'Jardinier'}
        </span>
        <button onClick={deconnexion}>Deconnexion</button>
      </div>
    </header>
  )
}
