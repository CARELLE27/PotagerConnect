import { useEffect, useRef, useState } from 'react'
import { api } from '../api'

export default function PhotosCulture({ culture, onFermer }) {
  const [photos, setPhotos] = useState([])
  const [legende, setLegende] = useState('')
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)
  const fileRef = useRef(null)

  async function recharger() {
    try {
      setPhotos(await api.listePhotos(culture.id))
    } catch (e) {
      setErreur(e.message)
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { recharger() }, [])

  function choisirFichier(e) {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) {
      setErreur('Image trop lourde (max 2 Mo).')
      return
    }
    const reader = new FileReader()
    reader.onload = async () => {
      setErreur('')
      try {
        await api.ajouterPhoto(culture.id, { image_base64: reader.result, legende })
        setLegende('')
        if (fileRef.current) fileRef.current.value = ''
        await recharger()
      } catch (err) {
        setErreur(err.message)
      }
    }
    reader.readAsDataURL(file)
  }

  async function supprimer(id) {
    try {
      await api.supprimerPhoto(id)
      await recharger()
    } catch (e) {
      setErreur(e.message)
    }
  }

  return (
    <div className="modale-fond" onClick={onFermer}>
      <div className="modale" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 520 }}>
        <h2 style={{ fontSize: 17, marginTop: 0, textTransform: 'capitalize' }}>
          Photos — {culture.nom_plante}
        </h2>

        {erreur && <div className="erreur" role="alert">{erreur}</div>}

        <div style={{ marginBottom: 16 }}>
          <label htmlFor="legende">Legende (optionnel)</label>
          <input id="legende" placeholder="Semaine 3, floraison..." value={legende}
            onChange={(e) => setLegende(e.target.value)} />
          <div style={{ height: 8 }} />
          <input ref={fileRef} type="file" accept="image/*" onChange={choisirFichier} />
        </div>

        {chargement ? (
          <p className="vide">Chargement...</p>
        ) : photos.length === 0 ? (
          <p className="vide">Aucune photo. Ajoutez la premiere !</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: 10 }}>
            {photos.map((p) => (
              <div key={p.id} style={{ position: 'relative' }}>
                <img src={p.image_base64} alt={p.legende || 'photo culture'}
                  style={{ width: '100%', height: 100, objectFit: 'cover', borderRadius: 'var(--rayon)', border: '1px solid var(--bord)' }} />
                {p.legende && <div style={{ fontSize: 11, color: 'var(--gris)', marginTop: 2 }}>{p.legende}</div>}
                <button onClick={() => supprimer(p.id)}
                  style={{ position: 'absolute', top: 4, right: 4, fontSize: 11, padding: '2px 6px', background: 'rgba(255,255,255,0.9)' }}>
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: 20 }}>
          <button style={{ width: '100%' }} onClick={onFermer}>Fermer</button>
        </div>
      </div>
    </div>
  )
}
