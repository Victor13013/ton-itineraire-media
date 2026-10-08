# pulse-care-media

Visuels, Reels et planning de publication Instagram + Facebook de Pulse Care.

- `render/content.py` : les 30 posts (textes, légendes, photos utilisées)
- `render/render.py` : génère les visuels (1080x1350), les Reels motion design (1080x1920) et `planning/AAAA-MM-JJ.json`
- `planning/` : lu chaque jour à 18h par le scénario Make « Pulse Care – publication quotidienne »
- `index.html` : aperçu de tout le calendrier → https://victor13013.github.io/pulse-care-media/

Modifier un post : édite `render/content.py`, commit. GitHub Actions refait le rendu tout seul.

Photos : produits Pulse Care (Shopify) et Unsplash (licence Unsplash). Polices Poppins et Inter (SIL Open Font License).
