import { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Forum() {
  const { user } = useAuth()
  const [posts, setPosts] = useState([])
  const [filtre, setFiltre] = useState('')
  const [ouvert, setOuvert] = useState(false)
  const [form, setForm] = useState({ titre: '', contenu: '', type: 'entraide' })
  const [detail, setDetail] = useState(null)
  const [nouveauComm, setNouveauComm] = useState('')
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)

  async function recharger() {
    try {
      setPosts(await api.listePosts(filtre))
    } catch (e) {
      setErreur(e.message)
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { recharger() }, [filtre])

  async function publier() {
    setErreur('')
    try {
      await api.creerPost(form)
      setOuvert(false)
      setForm({ titre: '', contenu: '', type: 'entraide' })
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  async function ouvrirDetail(id) {
    try {
      setDetail(await api.detailPost(id))
    } catch (e) {
      setErreur(e.message)
    }
  }

  async function envoyerCommentaire() {
    if (!nouveauComm.trim()) return
    try {
      await api.commenter(detail.id, { contenu: nouveauComm })
      setNouveauComm('')
      setDetail(await api.detailPost(detail.id))
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  async function supprimer(id) {
    try {
      await api.supprimerPost(id)
      setDetail(null)
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  if (chargement) return <p className="vide">Chargement du forum...</p>

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 20, marginBottom: 4 }}>Forum d'entraide et troc</h1>
          <p style={{ color: 'var(--gris)', fontSize: 14, marginTop: 0 }}>
            Posez vos questions, echangez graines et plants entre jardiniers.
          </p>
        </div>
        <button className="primaire" onClick={() => setOuvert(true)}>+ Publier</button>
      </div>

      {erreur && <div className="erreur" role="alert">{erreur}</div>}

      <div style={{ display: 'flex', gap: 8, margin: '12px 0' }}>
        {['', 'entraide', 'troc'].map((t) => (
          <button key={t} onClick={() => setFiltre(t)}
            style={{ fontSize: 13, background: filtre === t ? 'var(--vert)' : '#fff',
              color: filtre === t ? '#fff' : 'var(--gris)',
              borderColor: filtre === t ? 'var(--vert)' : 'var(--bord)' }}>
            {t === '' ? 'Tout' : t === 'entraide' ? 'Entraide' : 'Troc'}
          </button>
        ))}
      </div>

      {posts.length === 0 ? (
        <p className="vide">Aucun post pour l'instant. Lancez la discussion !</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {posts.map((p) => (
            <div className="carte" key={p.id} style={{ padding: 16, cursor: 'pointer' }}
              onClick={() => ouvrirDetail(p.id)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ fontWeight: 500 }}>{p.titre}</div>
                <span className="badge" style={{
                  background: p.type === 'troc' ? 'var(--ambre-clair)' : 'var(--vert-clair)',
                  color: p.type === 'troc' ? 'var(--ambre)' : 'var(--vert)' }}>
                  {p.type === 'troc' ? 'Troc' : 'Entraide'}
                </span>
              </div>
              <div style={{ fontSize: 13, color: 'var(--gris)', marginTop: 6 }}>
                Par {p.auteur_nom} · {p.nb_commentaires} commentaire{p.nb_commentaires > 1 ? 's' : ''}
              </div>
            </div>
          ))}
        </div>
      )}

      {ouvert && (
        <div className="modale-fond" onClick={() => setOuvert(false)}>
          <div className="modale" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: 17, marginTop: 0 }}>Nouveau post</h2>
            <label htmlFor="type">Type</label>
            <select id="type" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
              <option value="entraide">Entraide</option>
              <option value="troc">Troc de graines/plants</option>
            </select>
            <div style={{ height: 12 }} />
            <label htmlFor="titre">Titre</label>
            <input id="titre" value={form.titre} onChange={(e) => setForm({ ...form, titre: e.target.value })} />
            <div style={{ height: 12 }} />
            <label htmlFor="contenu">Message</label>
            <textarea id="contenu" rows={4} value={form.contenu}
              onChange={(e) => setForm({ ...form, contenu: e.target.value })}
              style={{ width: '100%', padding: '9px 12px', border: '1px solid var(--bord)',
                borderRadius: 'var(--rayon)', fontFamily: 'inherit', resize: 'vertical' }} />
            <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
              <button style={{ flex: 1 }} onClick={() => setOuvert(false)}>Annuler</button>
              <button className="primaire" style={{ flex: 1 }} onClick={publier}
                disabled={!form.titre || !form.contenu}>Publier</button>
            </div>
          </div>
        </div>
      )}

      {detail && (
        <div className="modale-fond" onClick={() => setDetail(null)}>
          <div className="modale" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 520 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <h2 style={{ fontSize: 18, marginTop: 0 }}>{detail.titre}</h2>
              {detail.user_id === user.id && (
                <button onClick={() => supprimer(detail.id)} style={{ fontSize: 12 }}>Supprimer</button>
              )}
            </div>
            <p style={{ fontSize: 14 }}>{detail.contenu}</p>
            <div style={{ fontSize: 12, color: 'var(--gris)' }}>Par {detail.auteur_nom}</div>

            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--bord)' }}>
              <strong style={{ fontSize: 14 }}>Commentaires ({detail.commentaires.length})</strong>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, margin: '10px 0' }}>
                {detail.commentaires.map((c) => (
                  <div key={c.id} style={{ background: 'var(--gris-clair)', padding: 10, borderRadius: 'var(--rayon)' }}>
                    <div style={{ fontSize: 14 }}>{c.contenu}</div>
                    <div style={{ fontSize: 12, color: 'var(--gris)', marginTop: 2 }}>{c.auteur_nom}</div>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <input placeholder="Ajouter un commentaire..." value={nouveauComm}
                  onChange={(e) => setNouveauComm(e.target.value)} />
                <button className="primaire" onClick={envoyerCommentaire} disabled={!nouveauComm.trim()}>
                  Envoyer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
