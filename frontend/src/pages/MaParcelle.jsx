import { useEffect, useState } from 'react'
import { api } from '../api'
import WidgetMeteo from '../components/WidgetMeteo'

export default function MaParcelle() {
  const [parcelle, setParcelle] = useState(null)
  const [cultures, setCultures] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [ouvert, setOuvert] = useState(false)
  const [form, setForm] = useState({ nom_plante: '', date_plantation: '' })
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)

  async function recharger() {
    try {
      const mes = await api.mesParcelles()
      if (mes.length === 0) return setChargement(false)
      const detail = await api.detailParcelle(mes[0].id)
      setParcelle(detail)
      setCultures(detail.cultures)
      const s = await api.suggestions(detail.id)
      setSuggestions(s.suggestions.slice(0, 5))
    } catch (e) {
      setErreur(e.message)
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { recharger() }, [])

  async function ajouter() {
    setErreur('')
    try {
      await api.creerCulture(parcelle.id, form)
      setOuvert(false)
      setForm({ nom_plante: '', date_plantation: '' })
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  async function recolter(id) {
    try {
      await api.recolter(id)
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  if (chargement) return <p className="vide">Chargement...</p>
  if (!parcelle)
    return <p className="vide">Aucune parcelle ne vous est encore attribuee. Contactez le responsable du jardin.</p>

  const enCours = cultures.filter((c) => c.statut === 'en_cours').length

  return (
    <>
      <h1 style={{ fontSize: 20 }}>Ma parcelle</h1>
      {erreur && <div className="erreur" role="alert">{erreur}</div>}

      <WidgetMeteo />

      <div className="metriques">
        <div className="metrique">
          <div style={{ fontSize: 12, color: 'var(--gris)' }}>Parcelle</div>
          <div className="valeur">{parcelle.numero}</div>
        </div>
        <div className="metrique">
          <div style={{ fontSize: 12, color: 'var(--gris)' }}>Surface</div>
          <div className="valeur">{parcelle.surface_m2} m²</div>
        </div>
        <div className="metrique">
          <div style={{ fontSize: 12, color: 'var(--gris)' }}>Cultures en cours</div>
          <div className="valeur">{enCours}</div>
        </div>
      </div>

      {suggestions.length > 0 && (
        <div className="carte" style={{ marginBottom: 20, background: 'var(--vert-clair)', borderColor: 'var(--vert-bord)' }}>
          <strong style={{ fontSize: 14, color: 'var(--vert)' }}>A planter ce mois-ci</strong>
          <p style={{ margin: '6px 0 0', fontSize: 14, color: 'var(--vert)' }}>
            {suggestions.map((s) => s.nom_plante).join(', ')}
          </p>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <strong>Mes cultures</strong>
        <button onClick={() => setOuvert(true)}>+ Ajouter</button>
      </div>

      {cultures.length === 0 ? (
        <p className="vide">Aucune culture pour l'instant — ajoutez-en une.</p>
      ) : (
        cultures.map((c) => (
          <div className="ligne-culture" key={c.id}>
            <div>
              <div style={{ fontWeight: 500, textTransform: 'capitalize' }}>{c.nom_plante}</div>
              <div style={{ fontSize: 12, color: 'var(--gris)', marginTop: 2 }}>
                Plante le {c.date_plantation}
                {c.date_recolte_prevue && ` — recolte prevue le ${c.date_recolte_prevue}`}
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className={`badge ${c.statut}`}>
                {c.statut === 'en_cours' ? 'En cours' : 'Recoltee'}
              </span>
              {c.statut === 'en_cours' && (
                <button onClick={() => recolter(c.id)} style={{ fontSize: 13, padding: '5px 10px' }}>
                  Recolter
                </button>
              )}
            </div>
          </div>
        ))
      )}

      {ouvert && (
        <div className="modale-fond" onClick={() => setOuvert(false)}>
          <div className="modale" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: 17, marginTop: 0 }}>Ajouter une culture</h2>
            <label htmlFor="plante">Plante</label>
            <input id="plante" placeholder="tomate, radis, courgette..." value={form.nom_plante}
              onChange={(e) => setForm({ ...form, nom_plante: e.target.value })} />
            <div style={{ height: 12 }} />
            <label htmlFor="date">Date de plantation</label>
            <input id="date" type="date" value={form.date_plantation}
              onChange={(e) => setForm({ ...form, date_plantation: e.target.value })} />
            <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
              <button style={{ flex: 1 }} onClick={() => setOuvert(false)}>Annuler</button>
              <button className="primaire" style={{ flex: 1 }} onClick={ajouter}
                disabled={!form.nom_plante || !form.date_plantation}>
                Ajouter
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
