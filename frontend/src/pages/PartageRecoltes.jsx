import { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'

export default function PartageRecoltes() {
  const { user } = useAuth()
  const [recoltes, setRecoltes] = useState([])
  const [ouvert, setOuvert] = useState(false)
  const [form, setForm] = useState({ nom_produit: '', quantite: '' })
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)

  async function recharger() {
    try {
      setRecoltes(await api.listeRecoltes())
    } catch (e) {
      setErreur(e.message)
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { recharger() }, [])

  async function proposer() {
    setErreur('')
    try {
      await api.proposerRecolte(form)
      setOuvert(false)
      setForm({ nom_produit: '', quantite: '' })
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  async function reserver(id) {
    setErreur('')
    try {
      await api.reserverRecolte(id)
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  async function annuler(id) {
    setErreur('')
    try {
      await api.annulerRecolte(id)
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  if (chargement) return <p className="vide">Chargement des recoltes...</p>

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 20, marginBottom: 4 }}>Partage des recoltes</h1>
          <p style={{ color: 'var(--gris)', fontSize: 14, marginTop: 0 }}>
            Proposez vos surplus, reservez ceux des autres. Zero gaspillage.
          </p>
        </div>
        <button className="primaire" onClick={() => setOuvert(true)}>+ Proposer</button>
      </div>

      {erreur && <div className="erreur" role="alert">{erreur}</div>}

      {recoltes.length === 0 ? (
        <p className="vide">Aucune recolte partagee pour l'instant. Soyez le premier !</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 8 }}>
          {recoltes.map((r) => {
            const estAMoi = r.user_id === user.id
            const reservee = r.statut === 'reservee'
            return (
              <div className="carte" key={r.id}
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 16 }}>
                <div>
                  <div style={{ fontWeight: 500, fontSize: 15 }}>{r.nom_produit}</div>
                  <div style={{ fontSize: 13, color: 'var(--gris)', marginTop: 2 }}>
                    Quantite : {r.quantite}{estAMoi && ' — votre offre'}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  {reservee ? (
                    <span className="badge recoltee">Reservee</span>
                  ) : estAMoi ? (
                    <button onClick={() => annuler(r.id)} style={{ fontSize: 13 }}>Retirer</button>
                  ) : (
                    <button className="primaire" onClick={() => reserver(r.id)} style={{ fontSize: 13 }}>
                      Reserver
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {ouvert && (
        <div className="modale-fond" onClick={() => setOuvert(false)}>
          <div className="modale" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: 17, marginTop: 0 }}>Proposer une recolte</h2>
            <label htmlFor="produit">Produit</label>
            <input id="produit" placeholder="Tomates, courgettes..." value={form.nom_produit}
              onChange={(e) => setForm({ ...form, nom_produit: e.target.value })} />
            <div style={{ height: 12 }} />
            <label htmlFor="quantite">Quantite</label>
            <input id="quantite" placeholder="2 kg, 1 botte, 5 pieces..." value={form.quantite}
              onChange={(e) => setForm({ ...form, quantite: e.target.value })} />
            <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
              <button style={{ flex: 1 }} onClick={() => setOuvert(false)}>Annuler</button>
              <button className="primaire" style={{ flex: 1 }} onClick={proposer}
                disabled={!form.nom_produit || !form.quantite}>
                Proposer
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
