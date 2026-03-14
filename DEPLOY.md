# TrustLens — Guide de Déploiement sur Render.com

## Prérequis

1. Un compte [Render.com](https://render.com) (gratuit)
2. Un compte [MongoDB Atlas](https://www.mongodb.com/atlas) (gratuit, tier M0)
3. Votre code poussé sur un repo GitHub (utilisez "Save to Github" depuis Emergent)
4. Votre clé Emergent LLM (pour Claude Sonnet)

---

## Étape 1 : Créer la base MongoDB Atlas

1. Allez sur [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Créez un cluster gratuit (M0 Sandbox)
3. Créez un utilisateur de base de données (Database Access → Add New User)
4. Autorisez toutes les IPs (Network Access → Add IP → `0.0.0.0/0`)
5. Récupérez votre **connection string** : `mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/trustlens?retryWrites=true&w=majority`

---

## Étape 2 : Déployer le Backend (Web Service)

1. Sur Render, cliquez **New → Web Service**
2. Connectez votre repo GitHub
3. Configurez :

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `trustlens-api` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/` |
| **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

4. Ajoutez les **Variables d'environnement** :

| Clé | Valeur |
|-----|--------|
| `MONGO_URL` | `mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/trustlens?retryWrites=true&w=majority` |
| `DB_NAME` | `trustlens` |
| `CORS_ORIGINS` | `https://trustlens.onrender.com` (l'URL de votre frontend, à mettre à jour après) |
| `EMERGENT_LLM_KEY` | Votre clé Emergent LLM |
| `JWT_SECRET` | Un secret aléatoire (ex: `openssl rand -hex 32`) |

5. Cliquez **Create Web Service**

Votre backend sera accessible à : `https://trustlens-api.onrender.com`

---

## Étape 3 : Déployer le Frontend (Static Site)

1. Sur Render, cliquez **New → Static Site**
2. Connectez le même repo GitHub
3. Configurez :

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `trustlens` |
| **Root Directory** | `frontend` |
| **Build Command** | `yarn install && yarn build` |
| **Publish Directory** | `build` |

4. Ajoutez la **Variable d'environnement** :

| Clé | Valeur |
|-----|--------|
| `REACT_APP_BACKEND_URL` | `https://trustlens-api.onrender.com` |

5. Ajoutez une **Rewrite Rule** (Settings → Redirects/Rewrites) :

| Source | Destination | Action |
|--------|-------------|--------|
| `/api/*` | `https://trustlens-api.onrender.com/api/*` | Proxy |
| `/*` | `/index.html` | Rewrite |

La première règle redirige les appels API vers le backend.
La seconde permet au routing React de fonctionner.

6. Cliquez **Create Static Site**

---

## Étape 4 : Mettre à jour CORS

Retournez dans les variables d'environnement du backend et mettez à jour `CORS_ORIGINS` avec l'URL exacte de votre frontend :

```
CORS_ORIGINS=https://trustlens.onrender.com
```

---

## Étape 5 : Vérifier

1. Ouvrez `https://trustlens.onrender.com`
2. La landing page doit s'afficher
3. Cliquez "Start Relationship Analysis" — l'analyse doit démarrer
4. Vérifiez l'API directement : `https://trustlens-api.onrender.com/api/cases/stats`

---

## Notes importantes

- **Premier démarrage** : Le tier gratuit Render met le service en veille après 15min d'inactivité. Le premier chargement peut prendre 30-50 secondes.
- **MongoDB Atlas** : Le tier gratuit M0 offre 512MB — largement suffisant pour démarrer.
- **Emergent LLM Key** : Si la clé arrive à expiration, allez dans Profile → Universal Key → Add Balance sur la plateforme Emergent.
- **Domaine personnalisé** : Render permet d'ajouter un domaine custom gratuitement (Settings → Custom Domains).
