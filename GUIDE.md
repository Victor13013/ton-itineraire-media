# Ton Itinéraire — Instagram automatique : procédure quotidienne

Ce dépôt sert d'hébergement public aux visuels. Make lit `planning/AAAA-MM-JJ.json` chaque jour à 18h (Europe/Paris) et publie le post + la story sur Instagram.
Ta mission à chaque exécution : **garantir que les fichiers de planning des 3 prochains jours existent**, sont beaux, justes et variés.

## 1. Préparer (espace cloud)
```
cd /home/claude && rm -rf ti && git clone -q --depth 1 https://github.com/Victor13013/ton-itineraire-media.git ti && cd ti
pip install playwright pillow --break-system-packages -q   # Chromium est déjà installé
```
Le cloud peut LIRE le dépôt mais pas y écrire : l'envoi se fait depuis le Mac (étape 4).
Lis `history.json` (30 derniers jours), liste `queue/` et `planning/`.
Dates à préparer : **J+1, J+2 et J+3** (fuseau Europe/Paris) si leur `planning/<date>.json` n'existe pas encore. Ce tampon de 3 jours couvre les jours où le Mac est éteint.

## 2. Pour chaque date manquante (J+1 à J+3)
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
   - Pas la même destination 2 fois en 5 jours ; pas le même format 2 jours de suite ; **une photo n'est JAMAIS réutilisée** : ni deux fois dans la même publication (post + story), ni d'une publication à l'autre, quelle que soit l'ancienneté (voir `history.json`). Aucun visuel en double. Le script bloque toute réutilisation.
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

## 4. Publier (via le Mac)
1. Copie les fichiers produits (dossiers `media/<date>/`, `planning/<date>.json`, `history.json`, et note les fichiers `queue/` consommés) dans `/mnt/user-data/outputs/sync/` en gardant l'arborescence.
2. `device_commit_files` → vers `/Users/victormazuy/Claude/Projects/ton itinéraire/instagram-auto/_sync/` (même arborescence).
3. `device_bash` :
```
set -e; P="$HOME/mnt/ton itinéraire/instagram-auto"; cd $HOME; rm -rf repo
git clone -q https://x-access-token:$TOKEN@github.com/Victor13013/ton-itineraire-media.git repo && cd repo
git config user.name "Ton Itineraire Bot"; git config user.email "bot@ton-itineraire.com"
cp -r "$P/_sync/." ./ ; git rm -q --ignore-unmatch queue/<fichiers consommés>
git add -A && git commit -qm "Planning <dates>" && git push -q
mkdir -p "$P/_sync_archive" && mv -n "$P/_sync" "$P/_sync_archive/$(date +%F-%H%M)"
```
4. Vérifie qu'une URL `https://raw.githubusercontent.com/Victor13013/ton-itineraire-media/main/media/<date>/<fichier>.jpg` répond 200.

## 5. Banque de photos (recharge)
Chaque photo ne sert qu'une fois (≈ 25 à 30 photos consommées par semaine). Si moins de 45 photos de `photos/` n'ont jamais été utilisées (d'après `history.json`), recharge ~40 photos (10 destinations ou thèmes × 4, en privilégiant les destinations absentes ou presque épuisées ; vérifie aussi que l'identifiant Unsplash n'est pas déjà dans `credits.json` pour éviter tout doublon) :
- Navigateur intégré de l'app Claude (outils `Claude_Browser`), onglet sur https://unsplash.com.
- En JS dans la page : `fetch('/napi/search/photos?query=...&per_page=20&orientation=portrait')`, garde uniquement `!premium && !plus`, télécharge chaque photo via `fetch('/photos/'+id+'/download?force=true&w=1600')`, concatène tout en un seul Blob `[images..., JSON index {file,dest,id,alt,author,link,offset,size}, longueur JSON sur 8 octets big-endian]`, puis déclenche UN seul téléchargement `ti_bank.bin` (le navigateur bloque les téléchargements multiples).
- Le fichier arrive dans `~/Downloads` sous un nom caché `.…claudefordesktop.…` : repère le plus récent, découpe-le en Python (device_bash) dans `instagram-auto/photos/` (noms `<destination>-NN.jpg`), compresse (1600 px, qualité 82), ajoute les entrées à `photos/credits.json`, copie dans le dépôt cloné et pousse.

## 6. Résumé final
Termine par un résumé court : dates préparées, sujet, format, nombre de visuels, sources vérifiées, alertes éventuelles.
