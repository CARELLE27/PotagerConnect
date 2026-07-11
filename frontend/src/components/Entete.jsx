import { useAuth } from '../context/AuthContext'

export default function Entete() {
  const { user, deconnexion } = useAuth()
  return (
    <header className="entete">
      <strong>PotagerConnect</strong>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 14, color: 'var(--gris)' }}>
          {user.prenom} {user.nom} — {user.role === 'admin' ? 'Responsable' : 'Jardinier'}
        </span>
        <button onClick={deconnexion}>Deconnexion</button>
      </div>
    </header>
  )
}
