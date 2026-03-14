# TrustLens — Rapport Produit

## Qu'est-ce que TrustLens ?

TrustLens est une plateforme d'intelligence relationnelle alimentée par l'IA. Elle aide les personnes qui doutent de la fidélité ou de l'engagement de leur partenaire à **analyser objectivement les signaux comportementaux** de leur relation — sans espionner, sans accuser, et sans créer de compte.

L'utilisateur répond à une série de questions structurées sur les changements récents dans sa relation. TrustLens compare ces réponses à une base de données de **300+ cas documentés** et produit un rapport détaillé avec un score de suspicion calibré, une analyse narrative par IA, et des recommandations concrètes.

---

## Comment ça fonctionne

1. **L'utilisateur partage son expérience** — Durée de la relation, satisfaction passée, habitudes de communication, changements récents (distance émotionnelle, secret autour du téléphone, changements d'horaire, etc.)
2. **Le moteur hybride analyse** — 5 questions déterministes pour le scoring + jusqu'à 3 questions contextuelles générées par IA si des signaux forts sont détectés
3. **TrustLens produit un rapport complet** — Score de suspicion, analyse narrative, comparaison avec des schémas réels, résumé des signaux, vérification de cohérence, timeline relationnelle

---

## Features qui rendent TrustLens unique

### 1. Anonymat total par défaut
Aucun compte requis. L'analyse complète est accessible sans inscription. Les comptes sont optionnels et proposés uniquement après l'obtention des résultats, pour sauvegarder l'historique. **La vie privée est au coeur du produit.**

### 2. Moteur hybride (Déterministe + IA)
Le score de suspicion est calculé de manière **déterministe** (pas d'hallucination possible). L'IA (Claude Sonnet 4.5) intervient uniquement pour :
- Générer des questions de suivi contextuelles
- Rédiger l'analyse narrative personnalisée
- Alimenter le Conversation Coach

Cette architecture garantit des résultats **fiables et reproductibles**.

### 3. Mirror Mode (Analyse Duale)
Deux partenaires peuvent chacun compléter une analyse indépendamment, puis consentir à comparer leurs résultats. TrustLens génère un **rapport de gap de perception** — montrant les écarts entre la façon dont chaque partenaire perçoit la relation. Aucune autre plateforme n'offre cette fonctionnalité.

### 4. Conversation Coach avec export PDF
Après l'analyse, l'utilisateur peut préparer une conversation difficile avec son partenaire grâce à un coach IA qui fournit :
- Le cadrage de la conversation
- Des phrases d'ouverture suggérées
- Des questions à poser
- Une préparation émotionnelle
- Les choses à éviter

Le tout est téléchargeable en PDF.

### 5. Filtrage démographique multi-dimensionnel
Les résultats de comparaison sont filtrés par **durée de relation + tranche d'âge + situation de cohabitation**. Cela signifie que les patterns auxquels l'utilisateur est comparé sont ceux de personnes dans des situations similaires — pas une moyenne générique.

### 6. Global Pattern Engine (contributions anonymes)
Après chaque analyse, l'utilisateur peut anonymement contribuer son expérience à la base de données. Les données sont automatiquement anonymisées et enrichissent la base de patterns pour les futurs utilisateurs. **Le produit s'améliore avec chaque utilisation.**

### 7. Signal Strength Summary avec suivi de tendance
Le rapport montre transparemment quels signaux ont été détectés et avec quelle intensité (Fort / Modéré / Faible). Pour les utilisateurs avec compte, le système compare les signaux avec l'analyse précédente et affiche les deltas (+12%, -8%).

### 8. Reveal progressif cinématique
Les résultats ne s'affichent pas d'un coup. Ils sont révélés en **12 étapes progressives** avec animations, créant une expérience émotionnelle et immersive — comme un documentaire qui dévoile ses conclusions étape par étape.

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | React 19, Tailwind CSS, Framer Motion, shadcn/ui |
| Backend | FastAPI (Python), Motor (MongoDB async) |
| Base de données | MongoDB |
| IA | Claude Sonnet 4.5 (via emergentintegrations) |
| PDF | ReportLab |
| Auth | JWT (passlib + python-jose) |

---

## Chiffres clés

- **300+** cas documentés dans la base de données
- **5** questions déterministes + **3** questions IA adaptatives
- **12** étapes de révélation progressive des résultats
- **5** catégories de contribution (infidélité confirmée, désengagement émotionnel, malentendu, crise personnelle, conflit non résolu)
- **100%** de taux de réussite aux tests (16/16 backend, tous les tests frontend)

---

## Statut

**L'application est entièrement opérationnelle et prête pour le lancement.**

Toutes les fonctionnalités planifiées ont été implémentées et testées. Le backlog est vide.
