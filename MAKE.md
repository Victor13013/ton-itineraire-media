# Scénario Make : publication quotidienne (≈ 15 min, une seule fois)

Prérequis : compte Instagram **Pro** relié à une **page Facebook** (déjà OK), compte Make gratuit.

## 1. Créer le scénario
Make → **Create a new scenario** → nom : `Ton Itinéraire – publication quotidienne`.

## 2. Module 1 : lire le planning du jour
- Module **HTTP → Make a request**
- URL : `https://raw.githubusercontent.com/<USER>/ton-itineraire-media/main/planning/{{formatDate(now; "YYYY-MM-DD"; "Europe/Paris")}}.json`
- Method : `GET` · **Parse response : Yes**
- Clic droit sur le module → **Add error handler → Ignore** (s'il n'y a pas de planning ce jour-là, rien ne se passe).

## 3. Router (3 routes)
Ajoute un **Router** après le module HTTP.

**Route A — Carrousel** · filtre : `data.post.type` *Equal to* `carousel`
- Module **Instagram for Business → Create a Carousel Post**
- Connexion : ton compte Instagram (via Facebook) · Page : ta page Facebook
- Files/Media : clique sur **Map** et sélectionne `data.post.media` (chaque élément contient `media_type` = IMAGE et `url`)
- Caption : `data.post.caption`

**Route B — Post simple** · filtre : `data.post.type` *Equal to* `photo`
- Module **Instagram for Business → Create a Photo Post**
- Photo URL : `data.post.image_url` · Caption : `data.post.caption`

**Route C — Story** · sans filtre
1. **Instagram for Business → Make an API Call**
   - URL : `/<IG_USER_ID>/media` · Method : `POST`
   - Body : `{"image_url": "{{1.data.story.image_url}}", "media_type": "STORIES"}`
2. **Tools → Sleep** : 30 secondes
3. **Instagram for Business → Make an API Call**
   - URL : `/<IG_USER_ID>/media_publish` · Method : `POST`
   - Body : `{"creation_id": "{{<id renvoyé par l'étape 1>}}"}`

> `<IG_USER_ID>` : lance une fois un module *Make an API Call* avec `GET /me/accounts?fields=instagram_business_account` → copie l'`id` de `instagram_business_account`.

## 4. Planification
Horloge du scénario → **Every day** à **18:00** · fuseau **Europe/Paris** (Make → Profile → Time zone). Active le scénario (**ON**).

## 5. Tester
Bouton **Run once** le jour où un fichier `planning/<date du jour>.json` existe. Vérifie sur Instagram, puis laisse tourner.

Consommation : ≈ 6 opérations/jour ≈ 180/mois (offre gratuite Make suffisante).
