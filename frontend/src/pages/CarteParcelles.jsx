import { useEffect, useState } from 'react'
import { api } from '../api'

export default function CarteParcelles() {
  const [parcelles, setParcelles] = useState([])
  const [jardiniers, setJardiniers] = useState([])
  const [selection, setSelection] = useState(null)
  const [choix, setChoix] = useState('')
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)

  async function recharger() {
    try {
      const [p, j] = await Promise.all([api.listeParcelles(), api.listeJardiniers()])
      setParcelles(p)
      setJardiniers(j)
    } catch (e) {
      setErreur(e.message)
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { recharger() }, [])

  async function attribuer() {
    setErreur('')
    try {
      await api.attribuer(selection.id, Number(choix))
      setSelection(null)
      setChoix('')
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  if (chargement) return <p className="vide">Chargement des parcelles...</p>

  const libres = parcelles.filter((p) => p.statut === 'libre').length

  return (
    <>
      <h1 style={{ fontSize: 20 }}>Carte des parcelles</h1>
      <p style={{ color: 'var(--gris)', fontSize: 14 }}>
        {parcelles.length} parcelles — {libres} libre{libres > 1 ? 's' : ''}
      </p>

      {erreur && <div className="erreur" role="alert">{erreur}</div>}

      <div style={{ display: 'flex', gap: 16, margin: '14px 0', fontSize: 13 }}>
        <span>🟩 Libre</span>
        <span>⬜ Attribuee</span>
      </div>

      <div className="grille-parcelles">
        {parcelles.map((p) => {
          const libre = p.statut === 'libre'
          return (
            <button
              key={p.id}
              className={`parcelle ${libre ? 'libre' : 'attribuee'}`}
              onClick={() => libre && setSelection(p)}
              disabled={!libre}
              aria-label={`Parcelle ${p.numero}, ${libre ? 'libre' : `attribuee a ${p.jardinier_nom}`}`}
            >
              <div style={{ fontWeight: 500 }}>{p.numero}</div>
              <div style={{ fontSize: 12, marginTop: 4 }}>
                {libre ? 'Libre' : p.jardinier_nom}
              </div>
              <div style={{ fontSize: 11, color: 'var(--gris)', marginTop: 2 }}>{p.surface_m2} m²</div>
            </button>
          )
        })}
      </div>

      {selection && (
        <div className="modale-fond" onClick={() => setSelection(null)}>
          <div className="modale" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: 17, marginTop: 0 }}>Attribuer la parcelle {selection.numero}</h2>
            <label htmlFor="jardinier">Jardinier</label>
            <select id="jardinier" value={choix} onChange={(e) => setChoix(e.target.value)}>
              <option value="">Choisir un jardinier</option>
              {jardiniers.map((j) => (
                <option key={j.id} value={j.id}>{j.prenom} {j.nom}</option>
              ))}
            </select>
            <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
              <button style={{ flex: 1 }} onClick={() => setSelection(null)}>Annuler</button>
              <button className="primaire" style={{ flex: 1 }} onClick={attribuer} disabled={!choix}>
                Attribuer
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
