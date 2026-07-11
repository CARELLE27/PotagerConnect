import { useState } from 'react'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { connexion } = useAuth()
  const [onglet, setOnglet] = useState('connexion')
  const [form, setForm] = useState({ email: '', password: '', nom: '', prenom: '' })
  const [erreur, setErreur] = useState('')
  const [enCours, setEnCours] = useState(false)

  const maj = (champ) => (e) => setForm({ ...form, [champ]: e.target.value })

  async function soumettre() {
    setErreur('')
    setEnCours(true)
    try {
      if (onglet === 'inscription') {
        await api.register(form)
      }
      await connexion(form.email, form.password)
    } catch (e) {
      setErreur(e.message)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div style={{ maxWidth: 380, margin: '48px auto' }}>
      <div className="carte">
        <h1 style={{ textAlign: 'center', fontSize: 22, marginTop: 0 }}>PotagerConnect</h1>

        <div style={{ display: 'flex', borderBottom: '1px solid var(--bord)', marginBottom: 20 }}>
          {['connexion', 'inscription'].map((t) => (
            <button
              key={t}
              onClick={() => { setOnglet(t); setErreur('') }}
              style={{
                flex: 1, border: 'none', background: 'none', padding: 10,
                borderBottom: onglet === t ? '2px solid var(--vert)' : '2px solid transparent',
                fontWeight: onglet === t ? 500 : 400,
              }}
            >
              {t === 'connexion' ? 'Connexion' : 'Inscription'}
            </button>
          ))}
        </div>

        {erreur && <div className="erreur" role="alert">{erreur}</div>}

        {onglet === 'inscription' && (
          <>
            <label htmlFor="prenom">Prenom</label>
            <input id="prenom" value={form.prenom} onChange={maj('prenom')} />
            <div style={{ height: 12 }} />
            <label htmlFor="nom">Nom</label>
            <input id="nom" value={form.nom} onChange={maj('nom')} />
            <div style={{ height: 12 }} />
          </>
        )}

        <label htmlFor="email">Email</label>
        <input id="email" type="email" placeholder="nom@email.com" value={form.email} onChange={maj('email')} />
        <div style={{ height: 12 }} />
        <label htmlFor="mdp">Mot de passe</label>
        <input id="mdp" type="password" placeholder="8 caracteres minimum" value={form.password} onChange={maj('password')} />

        <div style={{ height: 20 }} />
        <button className="primaire" style={{ width: '100%' }} onClick={soumettre} disabled={enCours}>
          {enCours ? 'Patientez...' : onglet === 'connexion' ? 'Se connecter' : "S'inscrire"}
        </button>
      </div>
    </div>
  )
}
