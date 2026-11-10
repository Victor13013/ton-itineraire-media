# -*- coding: utf-8 -*-
"""Pulse Care — vidéos (Reels Instagram + Facebook), une tous les 3 jours à 18h.

Les fichiers sont dans media/reels/AAAA-MM-JJ.mp4 (1080x1920, H.264 + AAC, moov en tête).
Le jour d'une vidéo, le post image de 18h est décalé au jour suivant (voir render.py).
`cover` = image de couverture, en millisecondes depuis le début.
"""

REELS = [
dict(date="2026-11-10", cover=1200, caption="""5 000 ans d'histoire de la brosse à dents, résumés en 40 secondes.

Des brindilles mâchées de l'Antiquité aux premières brosses à poils de l'empire chinois, puis au nylon des années 1930 et aux soies synthétiques d'aujourd'hui.

Le manche a changé de matériau une dizaine de fois. Le geste, lui, n'a jamais bougé : frotter pour retirer ce qui s'accroche aux dents.

Chez Pulse Care, on garde le bois sur la partie qu'on jette : des têtes en bambou, un manche qui reste.

[CTA]

#brosseadentselectrique #histoire #brosseadentsbambou #pulsecare"""),

dict(date="2026-11-13", cover=1500, caption="""Ce qu'il y a à l'intérieur d'une dent, et pourquoi ta brosse à dents électrique ne doit jamais appuyer.

→ L'émail : la couche extérieure, le tissu le plus dur du corps. Il ne se régénère pas.
→ La dentine : plus tendre, parcourue de micro-canaux qui transmettent le froid.
→ La pulpe : le nerf et les vaisseaux, au centre.

Quand l'émail s'use, la dentine se découvre. C'est là que le froid commence à faire mal.

Ton brossage protège la couche la plus exposée. Zéro pression, poils souples.

[CTA]

#brosseadentselectrique #email #anatomiedentaire #pulsecare"""),

dict(date="2026-11-16", cover=800, caption="""Vos questions sur la brosse à dents électrique Pulse Care, et nos réponses, en direct.

→ La batterie tient jusqu'à 30 jours, pour 2 brossages par jour
→ Recharge en USB-C, le même câble que ton téléphone
→ Étanche IPX7 : la douche, aucun problème
→ Tête à changer tous les 3 mois
→ Dans la boîte : 2 têtes en bambou, l'étui de voyage et le câble
→ 4 modes : Sensible, Nettoyage, Blanchiment, Polissage

Une autre question ? Écris-la en commentaire, on répond à toutes.

[CTA]

#brosseadentselectrique #faq #brosseadentsbambou #pulsecare"""),

dict(date="2026-11-19", cover=1500, caption="""Blanchir ses dents à la maison : ce que ta brosse à dents électrique peut faire, et ce que les astuces virales font vraiment.

→ Le bicarbonate tous les jours : trop abrasif, il use l'émail à force
→ Fraise + sel : double agression, l'acide ramollit et le sel râpe
→ Le charbon : même problème, l'émail ne repousse pas

Ce qui fonctionne sans risque : retirer les taches de surface au fur et à mesure. C'est le rôle du mode Blanchiment, qui agit sur le café, le thé et le vin, pas sur la teinte naturelle de la dent.

Pour un vrai éclaircissement, il n'y a qu'une adresse : ton dentiste.

[CTA]

#brosseadentselectrique #blanchiment #ideerecue #pulsecare"""),

dict(date="2026-11-22", cover=1500, caption="""Les dents de ton enfant : le guide des parents, en 30 secondes.

→ La quantité de dentifrice : un grain de riz avant 3 ans, un petit pois ensuite
→ Jusqu'à 6 ans, c'est toi qui brosses, ou qui repasses derrière
→ À partir de 4 ans, il apprend le geste, tu vérifies
→ Le dosage de fluor adapté à son âge se demande au dentiste

Brosser, c'est un geste qui se transmet. Les enfants copient surtout ce qu'ils voient faire.

Identifie un parent qui galère au moment du brossage.

[CTA]

#brosseadentselectrique #parents #hygienebuccodentaire #pulsecare"""),

dict(date="2026-11-25", cover=1200, caption="""Ton assiette compte autant que ta brosse à dents électrique. La preuve en un ticket de caisse.

Ce que tes dents aiment : laitages, viandes et poissons, œufs, pain et céréales complètes, eau.
Ce qu'il faut limiter : sodas, boissons énergisantes, jus de fruits acides, grignotage sucré.

Et le point que presque personne ne connaît : ce n'est pas la quantité de sucre qui compte le plus, c'est le nombre de fois.

Chaque prise déclenche une attaque acide d'environ 20 minutes. Mieux vaut un dessert d'un coup que du grignotage toute l'après-midi.

[CTA]

#brosseadentselectrique #alimentation #carie #pulsecare"""),

dict(date="2026-11-28", cover=600, caption="""Mythe ou réalité ? Trois croyances sur le brossage et la brosse à dents électrique.

→ « 30 secondes de brossage, ça suffit » : non, la recommandation reste 2 minutes, 2 fois par jour
→ « Une brosse, ça se garde toute l'année » : non, une tête se change tous les 3 mois
→ « Le fil dentaire, c'est optionnel » : non, environ 40 % des surfaces sont entre les dents

Tu en pensais quoi, honnêtement ? Dis-le en commentaire.

[CTA]

#brosseadentselectrique #mythe #hygienebuccodentaire #pulsecare"""),

dict(date="2026-12-01", cover=1200, caption="""Diabète et gencives : un lien à double sens que ta brosse à dents électrique ne suffit pas à régler.

Un diabète mal équilibré fragilise les gencives. Et une gencive enflammée rend le diabète plus difficile à équilibrer. Les deux s'entretiennent.

Les signes qui doivent alerter :
→ gencives rouges ou gonflées
→ plaque ou tartre qui s'installe vite
→ mauvais goût persistant
→ dent douloureuse ou mobile

Ta bouche fait partie de ton suivi médical. Si tu es concerné, préviens ton dentiste et ton médecin.

[CTA]

#brosseadentselectrique #gencives #santebuccodentaire #pulsecare"""),

dict(date="2026-12-04", cover=1500, caption="""Les dents de sagesse, en 4 points, pour arrêter les idées reçues.

→ Elles arrivent tard, souvent entre 17 et 25 ans
→ Elles manquent fréquemment de place sur la mâchoire
→ Une mauvaise position peut provoquer douleur, infection ou gêne
→ Les enlever n'est pas systématique : c'est ton dentiste qui décide, souvent après une radio

Et quand elles sont là, elles se brossent comme les autres : tout au fond, derrière la dernière molaire. L'endroit que presque tout le monde oublie avec sa brosse à dents électrique.

[CTA]

#brosseadentselectrique #dentsdesagesse #hygienebuccodentaire #pulsecare"""),

dict(date="2026-12-07", cover=1200, caption="""Partir avec sa brosse à dents électrique : 5 règles pour que tout se passe bien.

→ Charge-la avant de partir : 30 jours d'autonomie, le chargeur peut rester à la maison
→ Range-la bien sèche, l'humidité enfermée dans l'étui est le pire ennemi
→ Emporte une tête d'avance si le séjour est long
→ Prends juste le câble USB-C, celui du téléphone fait l'affaire
→ En cabine, aucun souci : pas de restriction particulière

L'étui de voyage en bambou est inclus avec la Bamboo+.

[CTA]

#brosseadentselectrique #voyage #troussedetoilette #pulsecare"""),

dict(date="2026-12-10", cover=1200, caption="""Ta brosse à dents finit où ? La question qu'on s'est posée avant de créer Pulse Care.

Une brosse manuelle se remplace tous les 3 mois. À chaque fois, c'est l'objet entier qui part : manche compris.

Notre réponse, avec la brosse à dents électrique Bamboo+ :
→ le manche reste, pendant des années
→ seule la tête se change, et elle est en bambou
→ les poils sont à base d'huile de ricin, une fibre d'origine végétale

Un petit geste, à l'échelle d'une salle de bain. Mais répété deux fois par jour, toute l'année.

[CTA]

#brosseadentselectrique #brosseadentsbambou #poilsricin #pulsecare"""),

dict(date="2026-12-13", cover=2000, caption="""Pour une tortue marine, un sac plastique qui flotte ressemble à une méduse. La confusion peut être fatale.

C'est l'une des images qui nous a marqués quand on a conçu la brosse à dents électrique Pulse Care, et qui explique notre parti pris : réduire la partie qu'on jette.

→ la tête, celle qu'on remplace tous les 3 mois, est en bambou
→ les poils sont à base d'huile de ricin
→ le manche, lui, est fait pour durer des années

Prends soin de la mer, et de ton sourire.

[CTA]

#brosseadentselectrique #brosseadentsbambou #oceans #pulsecare"""),
]
