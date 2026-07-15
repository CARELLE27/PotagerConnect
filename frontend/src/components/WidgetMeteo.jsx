import { useEffect, useState } from 'react'
import { api } from '../api'

export default function WidgetMeteo() {
  const [meteo, setMeteo] = useState(null)
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    api.meteo()
      .then(setMeteo)
      .catch((e) => setErreur(e.message))
      .finally(() => setChargement(false))
  }, [])

  if (chargement) return <div className="carte" style={{ marginBottom: 20 }}>Chargement de la meteo...</div>

  // Erreur non bloquante : la meteo est un plus, pas un coeur de metier
  if (erreur) return (
    <div className="carte" style={{ marginBottom: 20, fontSize: 13, color: 'var(--gris)' }}>
      Meteo indisponible pour le moment.
    </div>
  )

  const a = meteo.aujourd_hui

  return (
    <div className="carte" style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ fontSize: 13, color: 'var(--gris)' }}>Meteo — {meteo.jardin}</div>
          <div style={{ fontSize: 24, fontWeight: 500, marginTop: 2 }}>
            {Math.round(a.temp_max)}° <span style={{ fontSize: 16, color: 'var(--gris)', fontWeight: 400 }}>/ {Math.round(a.temp_min)}°</span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--gris)' }}>Pluie : {a.pluie_mm} mm</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {meteo.previsions.slice(1).map((p) => (
            <div key={p.date} style={{ textAlign: 'center', fontSize: 12, color: 'var(--gris)' }}>
              <div>{new Date(p.date).toLocaleDateString('fr-FR', { weekday: 'short' })}</div>
              <div style={{ fontWeight: 500, color: 'var(--text-primary, #2C2C2A)' }}>{Math.round(p.temp_max)}°</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--bord)' }}>
        {meteo.conseils.map((c, i) => (
          <div key={i} style={{ fontSize: 14, color: 'var(--vert)', marginBottom: 4 }}>
            🌱 {c}
          </div>
        ))}
      </div>
    </div>
  )
}
