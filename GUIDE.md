# Ton Itinéraire — Instagram automatique : procédure quotidienne

Ce dépôt sert d'hébergement public aux visuels. Make lit `planning/AAAA-MM-JJ.json` chaque jour à 18h (Europe/Paris) et publie le post + la story sur Instagram.
Ta mission à chaque exécution : **garantir que les fichiers de planning de DEMAIN et d'APRÈS-DEMAIN existent**, sont beaux, justes et variés.

## 1. Préparer
```
git clone https://<TOKEN>@github.com/<USER>/ton-itineraire-media.git && cd ton-itineraire-media
pip install playwright pillow --break-system-packages -q   # Chromium est déjà installé
git config user.name "Ton Itineraire Bot"; git config user.email "bot@ton-itineraire.com"
```
Lis `history.json` (30 derniers jours) et liste `queue/`.

## 2. Pour chaque date manquante (J+1, J+2)
1. **File d'attente d'abord** : si un fichier de `queue/` respecte sa contrainte `not_before`, utilise-le (ordre alphabétique), puis supprime-le de `queue/`.
2. **Sinon, crée un contenu neuf** :
   - **Veille tendances (obligatoire)** : 2 à 4 recherches web du jour (actu voyage France, destinations tendance du mois, vacances scolaires à venir, nouvelles règles d'entrée/visa/taxes, événements). Choisis un angle utile pour quelqu'un qui prépare un voyage.
   - **Format selon le jour** (varie si le même sujet revient) :
     | Jour | Format | Type |
     |---|---|---|
     | Lundi | Mythe vs Réalité OU Dans les coulisses (signé « — Victor, fondateur de Ton Itinéraire ») | carrousel 5-7 |
     | Mardi | Destination du jour | post simple (1 slide `cover`) |
     | Mercredi | Exemple d'itinéraire (jour par jour, rappel final « ceci est un exemple ») | carrousel 5-7 |
     | Jeudi | Le saviez-vous ? (faits vérifiés, 1 par slide `fact`) | carrousel 4-6 |
     | Vendredi | Tendance / actu voyage de la semaine | carrousel ou simple |
     | Samedi | Où partir en <mois> ? / saison | carrousel 5-7 |
     | Dimanche | Inspiration : 1 photo forte + 1 conseil concret | post simple (`cover` ou `fact`) |
   - Pas la même destination 2 fois en 5 jours ; pas le même format 2 jours de suite ; pas une photo déjà utilisée dans les 21 derniers jours (voir `history.json`).
3. **Photos** : uniquement celles de `photos/` (voir `photos/credits.json` : destination, description, auteur). Fais une planche contact (PIL) des candidates et **regarde-la** avant de choisir. La photo doit montrer le lieu cité sur la slide (jamais une photo d'un autre lieu). Le champ `credit` = auteur.
4. **Écris l'item** `tmp/item.json` = `{"post": spec, "caption": "...", "story": spec_story, "topic": "slug"}`
   - Types de slides post : `cover` (photo, badge, title, sub), `photo` (photo, kicker, title, text), `fact` (photo, big, title, text), `myth` (photo, myth, title, text), `cta` (badge, title_html avec `<em>` sur 1-3 mots, points[3], button). Carrousel = cover + contenu + cta final.
   - Story : `{"slug":"story-<topic>","format":"story","slides":[{"type":"story","photo":..., "credit":..., "badge":"Nouveau post", "title":..., "text":..., "cta":"Voir le post →"}]}`. Une fois sur 3, fais plutôt une story conseil autonome (badge « Conseil du jour »).
   - Titres courts (≤ 6 mots sur cover), textes ≤ 30 mots par slide.
5. **Rends et contrôle** : `python3 pipeline/publish_day.py tmp/item.json AAAA-MM-JJ <USER>`. Le script bloque si : > 5 hashtags, mot interdit, texte qui déborde. Corrige et relance.
6. **Regarde chaque visuel** (Read sur les .jpg ou une planche) : cadrage, lisibilité du texte sur la photo, cohérence photo/texte, aucune slide vide. Refais si un défaut.

## 3. Règles de marque (non négociables)
- **Vouvoiement** partout. Ton direct, phrases courtes, voix active. Pas de superlatifs creux.
- **Mots interdits** : paradisiaque, magique, incroyable, inoubliable, époustouflant, pépite, « n'hésitez pas », voyage de rêve, havre de paix, à couper le souffle, incontournable.
- **Aucun emoji** sauf drapeaux et flèches typographiques (→).
- **Légende** : mot-clé principal (ex. « itinéraire Portugal 7 jours ») dans la 1re phrase ; puces avec « → » ; une question pour les commentaires ; CTA « lien en bio » ; **5 hashtags max** intégrés ou en fin (mix : 1 destination, 1 niche FR, #itinerairesurmesure, #tonitineraire). ≤ 1 500 caractères.
- **Tarifs** (ne jamais inventer) : Essentiel 49-69 € (0-7 j : 49 €, 8-14 j : 59 €, 15 j+ : 69 €), Complet 99-139 €, Premium 179-229 €. Toujours préciser que c'est le prix du service, pas du voyage.
- **Ton Itinéraire ne réserve jamais rien** à la place du client. 0 % de commission. Fait main. Accessible hors connexion.
- **Aucun avis client inventé**. Avis réels utilisables uniquement : Manon R. (Islande, 9 j), Thomas B. (Maroc, 12 j), Léa D. (Vietnam, 15 j), Camille V. (Kenya, 10 j) — sans inventer de citation.
- **Tout chiffre, prix, date, règle** (visa, taxe, météo, horaires) : vérifié sur 2 sources dont 1 officielle si possible, le jour même. Mets les URL dans `"sources"` de l'item. Si incertain : ne publie pas le chiffre.
- Victor n'apparaît jamais en photo.

## 4. Publier
```
git add -A && git commit -m "Planning AAAA-MM-JJ" && git push
```
Vérifie ensuite qu'une URL `raw.githubusercontent.com/.../media/<date>/...` répond 200 (curl -I).

## 5. Banque de photos
Si moins de 30 photos n'ont jamais été utilisées (d'après `history.json`), ajoute une ligne `"photos_basses": true` au planning du jour et signale-le dans le résumé final : la tâche hebdomadaire de recharge (Mac) complètera.

## 6. Résumé final
Termine par un résumé court : dates préparées, sujet, format, nombre de visuels, sources vérifiées, alertes éventuelles.
