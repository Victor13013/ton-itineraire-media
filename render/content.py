# -*- coding: utf-8 -*-
"""Pulse Care — posts de 18h, 30 jours (10/11 → 09/12/2026).

Formats :
  photo    -> 1 visuel 1080x1350
  carousel -> 2 à 10 visuels 1080x1350

Gabarits : hero, statement, product, list, stats, versus (habillés par la DA du post)
           + bignum, quiz, steps, mosaic, arch, tracker, schema (formats mixtes).
DA du post : "a" (aplats v5), "b" (dégradés & verre), "c" (carnet & tchat).

Sources d'images (une seule utilisation par visuel sur tout le calendrier) :
  "s:<fichier>"  photo produit Shopify (cdn.shopify.com)
  "u:<id>"       photo Unsplash (licence Unsplash, libre d'usage commercial)

[CTA] est remplacé à l'export (Instagram : lien en bio / Facebook : URL).
"""

SHOP = "https://cdn.shopify.com/s/files/1/0906/8147/5446/files/"
CTA_IG = "Lien en bio pour voir la gamme Pulse Care."
CTA_FB = "Toute la gamme ici → https://pulsecarefrance.com"

S = {  # photos produit Shopify
 "p046": "Pulsecare-046.webp", "p088": "Pulsecare-088.webp", "p019": "Pulsecare-019.webp",
 "p083": "Pulsecare-083.webp", "p097": "Pulsecare-097.webp", "p095": "Pulsecare-095.webp",
 "p087": "Pulsecare-087.webp", "p121": "Pulsecare-121.webp", "p091": "Pulsecare-091.webp",
 "p090": "Pulsecare-090.webp", "p056": "Pulsecare-056.webp",
 "p002": "Pulsecare-002.png", "p004": "Pulsecare-004.png", "p005": "Pulsecare-005.png",
 "p006": "Pulsecare-006.png", "p011": "Pulsecare-011.webp", "p012": "Pulsecare-012.png",
 "p014": "Pulsecare-014.png", "p016": "Pulsecare-016.png", "p017": "Pulsecare-017.png",
 "p018": "Pulsecare-018.webp", "p021": "Pulsecare-021.webp", "p029": "Pulsecare-029.webp",
 "p055": "Pulsecare-055.webp", "p084": "Pulsecare-084.png", "p085": "Pulsecare-085.png",
 "p092": "Pulsecare-092.webp",
 "usb": "pulse-care-port-charge-usb-c-brosse-electrique.webp",
 "tete_main": "tete-rechange-brosse-dents-electrique-bambou-pulsecare.webp",
 "tete_main2": "tete-rechange-brosse-dents-electrique-bambou.webp",
 "ricin_gp": "pulse-care-poils-ricin-tete-bambou-gros-plan.webp",
 "ricin_fibres": "pulse-care-fibres-ricin-detail-tete-bambou.webp",
 "ricin_solo": "pulse-care-tete-brosse-ricin-bambou.webp",
 "ricin_face": "tete-brosse-bambou-compatible-brosse-electrique-pulsecare.webp",
 "ricin_profil": "tete-brosse-rechange-bambou-brosse-electrique-ecologique.webp",
 "ricin_arriere": "tete-brosse-electrique-bambou-rechange-pulsecare.webp",
 "ricin_pack2": "pulse-care-tetes-rechange-ricin-pack2-bambou.webp",
 "ricin_pack4": "pulse-care-tetes-rechange-ricin-pack4-bambou.webp",
 "ricin_pack4_vue": "tetes-brosse-electrique-bambou-rechange-pack4-pulsecare.webp",
 "nylon_profil": "tete-rechange-brosse-electrique-bambou-nylon-pulsecare-profil.webp",
 "nylon_face": "tete-brosse-electrique-bambou-nylon-pulsecare-face.webp",
 "nylon_pack2": "tetes-rechange-brosse-electrique-bambou-pack2-pulsecare.webp",
 "nylon_pack4": "pulse-care-tetes-rechange-nylon-pack4-bambou.webp",
 "nylon_pack4_noir": "recharges-brosse-bambou-nylon-pack4-pulsecare-noir.webp",
 "decouverte_main": "pulse-care-brosse-pack-decouverte-main.png",
 "decouverte_contenu": "pulse-care-pack-decouverte-contenu-manche-tetes.webp",
 "decouverte_neutre": "pulse-care-pack-decouverte-fond-neutre.webp",
 "decouverte_tetes": "pulse-care-pack-decouverte-tetes-ricin-incluses.webp",
 "bamboo_face": "pulse-care-brosse-sonique-bamboo-plus-face.webp",
 "icones": "pulse-care-icones-4-modes-brossage.webp",
 "modes_main": "pulse-care-brosse-electrique-modes-brossage.webp",
 "duo_tete": "pulse-care-pack-duo-brosse-tete-bambou.webp",
 "duo_acc": "pulse-care-pack-duo-accessoires-bambou.webp",
 "duo_etuis": "pulse-care-pack-duo-brosses-etuis.webp",
 "duo_coffret": "pulse-care-pack-duo-coffret-vue-ensemble.webp",
 "deux_brosses": "deux-brosses-a-dents-pulse-care.webp",
 "dec_etui_tetes": "pulse-care-pack-decouverte-brosse-etui-tetes.webp",
 "etui": "pulse-care-etui-bambou-ferme-brosse-electrique.webp",
 "etui_ouvert": "pulse-care-etui-bambou-ouvert-tetes-rechange.webp",
 "etui_voyage": "etui-de-voyage.webp",
 "etui_plat": "pulse-care-brosse-etui-bambou-tete-rechange.webp",
 "boite_bambou": "boite-bambou-brosse-a-dents.webp",
 "chargeur": "chargeur-usb-c-pulse-care.webp",
 "tete_ricin2": "tete-de-brosse-ricin.webp",
 "nylon_gauche": "tete-brosse-electrique-bambou-nylon-pulsecare-profil-gauche.webp",
 "nylon_pack2_profil": "tetes-rechange-brosse-electrique-bambou-nylon-pack2-profil.webp",
 "nylon_pack4_profil": "tetes-rechange-brosse-electrique-bambou-nylon-pack4-vue-profil.webp",
 "ricin_pack4_douce": "tetes-rechange-brosse-electrique-bambou-douce-pack4-pulsecare.webp",
}
def s(k): return "s:" + S[k]

TAGS = "#brosseadentselectrique #brosseadentsbambou #hygienebuccodentaire #pulsecare"

POSTS = [
# ───────────────────────── 2 · 11/11 · unboxing
dict(date="2026-11-11", kind="carousel", da="b", slides=[
  dict(tpl="hero", img=s("p029"), kicker="Pulse Care Bamboo+", title="Ce qu'il y a *dans la boîte*", swipe=True),
  dict(tpl="mosaic", kicker="Le contenu", title="4 choses, rien de plus", imgs=[(s("bamboo_face"), "Le manche"), (s("ricin_pack2"), "2 têtes en bambou"), (s("etui_voyage"), "L'étui"), (s("boite_bambou"), "Le câble USB-C")]),
  dict(tpl="arch", kicker="Tout compris", title="Rien d'autre *à racheter* avant 6 mois", img=s("dec_etui_tetes"), price="59,90 €"),
],
caption="""Brosse à dents électrique Pulse Care Bamboo+ : voilà ce qu'il y a dans la boîte.

→ 1 manche sonique
→ 2 têtes en bambou
→ 1 étui de voyage en bambou
→ 1 câble USB-C

Tout est inclus pour 59,90 €. Avec deux têtes, tu tiens environ 6 mois avant la première recharge.

Swipe pour voir le détail.

[CTA]

#brosseadentselectrique #brosseadentsbambou #unboxing #pulsecare"""),

# ───────────────────────── 3 · 12/11 · schéma dent
dict(date="2026-11-12", kind="photo", da="a", tone="mint", slides=[
  dict(tpl="schema", kind="tooth", kicker="Anatomie", title="Ce qu'il y a *sous l'émail*",
       sub="Et pourquoi l'émail ne repousse jamais."),
],
caption="""Pourquoi on répète de ne pas appuyer fort avec une brosse à dents électrique ? Regarde la coupe d'une dent.

→ L'émail est la couche extérieure. C'est le tissu le plus dur du corps, mais il ne se régénère pas.
→ Dessous, la dentine est plus tendre et plus sensible.
→ Au centre, la pulpe contient le nerf.

Quand l'émail s'use, la dentine se découvre. C'est là que le froid commence à piquer.

[CTA]

#brosseadentselectrique #email #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 4 · 13/11 · quiz tête
dict(date="2026-11-13", kind="carousel", da="c", slides=[
  dict(tpl="quiz", kicker="Question du jour", title="Tu changes ta tête *tous les combien* ?",
       options=["Tous les 3 mois", "Quand les poils s'écartent", "Une fois par an", "Jamais, en fait"], swipe=True),
  dict(tpl="quiz", kicker="La réponse", title="Tous les *3 mois*",
       options=["Tous les 3 mois", "Quand les poils s'écartent", "Une fois par an", "Jamais, en fait"], answer=0,
       note="Et aussi après une angine ou un gros rhume."),
  dict(tpl="product", img=s("tete_main"), kicker="Têtes de recharge", title="Clip en *une seconde*", sub="Têtes en bambou, poils ricin ou nylon."),
],
caption="""Petite question sur ta brosse à dents électrique : tu changes la tête tous les combien ?

A. Tous les 3 mois
B. Quand les poils partent dans tous les sens
C. Une fois par an
D. Jamais, en fait

Réponds en commentaire avant de swiper.

La bonne réponse : tous les 3 mois. Après, les poils s'écartent et retirent moins bien la plaque. Change-la aussi après une angine.

[CTA]

#brosseadentselectrique #tetederechange #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 5 · 14/11 · pack découverte
dict(date="2026-11-14", kind="photo", da="b", tone="sand", slides=[
  dict(tpl="arch", kicker="Pack découverte", title="Ton kit *pour commencer*", sub="Le manche, les têtes en bambou, l'étui.", img=s("decouverte_neutre"), price="64,90 €"),
],
caption="""Le pack découverte Pulse Care, pour passer à la brosse à dents électrique sans se poser de questions.

Dedans : le manche sonique, des têtes en bambou à poils de ricin et l'étui de voyage.

C'est le point de départ si tu hésites encore. Ou l'idée cadeau pour quelqu'un qui galère avec sa brosse manuelle.

Pack découverte : 64,90 €.

[CTA]

#brosseadentselectrique #packdecouverte #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 6 · 15/11 · routine du soir
dict(date="2026-11-15", kind="carousel", da="a", slides=[
  dict(tpl="hero", img="u:1552650272-b8a34e21bc4b", kicker="Routine du soir", title="Le brossage du soir compte *plus que celui du matin*", swipe=True),
  dict(tpl="steps", tone="mint", kicker="L'ordre qui marche", title="4 étapes, dans cet ordre", items=[("Fil dentaire", "Ou brossettes entre les dents."), ("2 minutes de brossage", "Mode Nettoyage, le minuteur gère."), ("Tu craches", "Sans rincer à l'eau."), ("Plus rien à manger", "Jusqu'au lendemain matin.")]),
],
caption="""Avec une brosse à dents électrique comme avec une manuelle, le brossage du soir compte plus que celui du matin.

La nuit, tu produis moins de salive. Les bactéries sont tranquilles pendant 8 heures.

L'ordre qui marche :
→ fil dentaire ou brossettes
→ 2 minutes de brossage
→ tu craches, tu ne rinces pas
→ plus rien à manger après

Enregistre ce post pour ce soir.

[CTA]

#brosseadentselectrique #routinedusoir #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 7 · 16/11 · dentiste
dict(date="2026-11-16", kind="photo", da="c", slides=[
  dict(tpl="statement", img="u:1777331903190-341a3dd0441b", kicker="Rappel", title="Ta brosse ne remplace pas *ton dentiste.*",
       sub="Un contrôle par an. Le tartre installé, seul un pro peut l'enlever."),
],
caption="""Une bonne brosse à dents électrique ne remplace pas le rendez-vous chez le dentiste.

Elle retire la plaque au quotidien. Mais une fois que la plaque a durci en tartre, le brossage n'y peut plus rien : il faut un détartrage.

Le rythme conseillé : un contrôle par an, plus souvent si ton dentiste te le demande.

Ton dernier rendez-vous date de quand ?

[CTA]

#brosseadentselectrique #dentiste #detartrage #pulsecare"""),

# ───────────────────────── 8 · 17/11 · manuelle ou électrique
dict(date="2026-11-17", kind="carousel", da="b", slides=[
  dict(tpl="hero", img="u:1693692273603-3b9e13789298", kicker="Le match", title="Manuelle ou *électrique* ?", swipe=True),
  dict(tpl="versus", kicker="Ce qui change", title="Lequel est *fait pour toi* ?", left=("Brosse manuelle", ["Technique à soigner", "Pas de minuteur", "Tout part à la poubelle"]), right=("Pulse Care", ["Les vibrations nettoient", "Minuteur 2 min intégré", "Seule la tête se change"])),
  dict(tpl="arch", kicker="Pulse Care Bamboo+", title="Prête à passer *à l'électrique* ?", img=s("p017"), price="59,90 €"),
],
caption="""Brosse à dents électrique ou manuelle : laquelle choisir ?

La manuelle fait le travail si ta technique est parfaite : bon angle, bon mouvement, 2 minutes pile. Dans la vraie vie, c'est rare.

La sonique facilite les choses :
→ 41 000 vibrations par minute, tu n'as qu'à guider
→ minuteur intégré, plus de brossage bâclé
→ un mode Sensible pour les gencives fragiles

Team manuelle ou team électrique ?

[CTA]

#brosseadentselectrique #brosseadentssonique #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 9 · 18/11 · autonomie
dict(date="2026-11-18", kind="photo", da="c", slides=[
  dict(tpl="bignum", kicker="Autonomie", big="30 j", title="sans toucher *au chargeur*", sub="Environ 2,5 h de charge, en USB-C.", img=s("chargeur")),
],
caption="""Une brosse à dents électrique qui se recharge une fois par mois, en USB-C.

→ environ 2,5 heures pour une charge complète
→ jusqu'à 30 jours d'autonomie, pour 2 brossages par jour
→ batterie lithium 500 mAh
→ le même câble que ton téléphone

Pas de socle qui traîne sur le lavabo. Et en voyage, tu peux laisser le chargeur à la maison.

[CTA]

#brosseadentselectrique #usbc #brosseadentsrechargeable #pulsecare"""),

# ───────────────────────── 10 · 19/11 · les 4 zones
dict(date="2026-11-19", kind="carousel", da="a", slides=[
  dict(tpl="schema", kind="zones", tone="sand", kicker="Le minuteur", title="4 zones, *30 secondes chacune*", swipe=True),
  dict(tpl="list", img="u:1758521539597-c774ddffba24", title="Les oubliées", numbered=True, items=[("Derrière les molaires", "Le fond, tout au bout."), ("Les faces internes", "Côté langue."), ("La ligne des gencives", "Là où la plaque s'accumule."), ("La langue", "3 passages doux suffisent.")]),
],
caption="""Une brosse à dents électrique, 2 minutes, 4 zones de 30 secondes. C'est toute la méthode.

Haut gauche, haut droite, bas gauche, bas droite. La micro-pause du minuteur te dit quand changer.

Les endroits que presque tout le monde oublie :
→ derrière les dernières molaires
→ les faces internes, côté langue
→ la ligne des gencives
→ la langue elle-même

Tu en oublies combien, honnêtement ?

[CTA]

#brosseadentselectrique #techniquedebrossage #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 11 · 20/11 · les 4 modes
dict(date="2026-11-20", kind="photo", da="b", tone="fresh", slides=[
  dict(tpl="mosaic", kicker="4 modes", title="Lequel choisir ?", sub="Un mode par besoin, un bouton pour passer de l'un à l'autre.",
       imgs=[(s("modes_main"), "Sensible"), (s("icones"), "Nettoyage"), (s("p019"), "Blanchiment"), (s("p090"), "Polissage")]),
],
caption="""4 modes sur ta brosse à dents électrique Pulse Care : lequel utiliser et quand ?

→ Sensible : vibrations adoucies, pour les gencives qui saignent ou les dents réactives
→ Nettoyage : le mode de tous les jours, matin et soir
→ Blanchiment : pour aider à retirer les taches de surface (café, thé)
→ Polissage : pour finir avec une sensation de dents lisses

Astuce : si tu passes du manuel à l'électrique, reste 1 à 2 semaines en mode Sensible.

[CTA]

#brosseadentselectrique #brosseadentssonique #modesdebrossage #pulsecare"""),

# ───────────────────────── 12 · 21/11 · vrai ou faux
dict(date="2026-11-21", kind="carousel", da="c", slides=[
  dict(tpl="statement", img="u:1593183230686-69876b0cb240", kicker="Vrai ou faux", title="Appuyer fort =\n*dents plus propres ?*", swipe=True),
  dict(tpl="schema", kind="angle", kicker="Le bon geste", title="Un angle *de 45°*", sub="Les poils orientés vers la gencive, aucune pression."),
],
caption="""Vrai ou faux : avec une brosse à dents électrique, plus tu appuies fort, plus tes dents sont propres ?

FAUX. Et c'est même l'inverse.

Appuyer use l'émail et fait reculer la gencive. Avec une sonique, le nettoyage vient des vibrations, pas de la force.

Le bon geste : la tête posée à 45° vers la gencive, et tu glisses lentement d'une dent à l'autre.

[CTA]

#brosseadentselectrique #vraioufaux #conseilsdentaires #pulsecare"""),

# ───────────────────────── 13 · 22/11 · poils ricin
dict(date="2026-11-22", kind="photo", da="a", tone="honey", slides=[
  dict(tpl="product", img=s("ricin_gp"), kicker="Gros plan", title="Des poils à base *de ricin*", sub="Fibre d'origine végétale, douce pour l'émail et les gencives."),
],
caption="""Gros plan sur les poils des têtes de brosse à dents électrique Pulse Care.

Ils sont fabriqués à base d'huile de ricin, une fibre d'origine végétale, à la place des poils 100 % pétrole.

Au brossage, le toucher est doux, pour l'émail comme pour les gencives sensibles. Et la plaque part comme il faut.

Montés sur une tête en bambou, compatibles uniquement avec les manches Pulse Care.

[CTA]

#brosseadentselectrique #poilsricin #gencivessensibles #pulsecare"""),

# ───────────────────────── 14 · 23/11 · tuto
dict(date="2026-11-23", kind="carousel", da="b", slides=[
  dict(tpl="hero", img=s("decouverte_main"), kicker="Tuto", title="Bien utiliser ta brosse *dès le premier jour*", swipe=True),
  dict(tpl="steps", tone="fresh", kicker="Avant d'allumer", title="L'ordre des gestes", items=[("Dentifrice sur la tête", "Une noisette suffit."), ("Tête sur les dents", "Puis seulement, tu allumes."), ("Angle de 45°", "Poils vers la gencive."), ("Tu glisses, tu ne frottes pas", "30 secondes par zone.")]),
],
caption="""Bien utiliser une brosse à dents électrique, c'est surtout une question d'ordre des gestes.

1. Mets le dentifrice sur la tête
2. Place la tête sur les dents AVANT d'allumer, sinon éclaboussures garanties
3. Angle de 45° vers la gencive
4. Tu glisses dent par dent, sans frotter, 30 secondes par zone

C'est tout. Le reste, le minuteur s'en occupe.

Enregistre ce post pour l'avoir sous la main.

[CTA]

#brosseadentselectrique #tuto #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 15 · 24/11 · défi 7 jours
dict(date="2026-11-24", kind="photo", da="c", slides=[
  dict(tpl="tracker", kicker="Le défi", title="7 jours, *2 brossages par jour*", sub="Capture ce post et coche tes cases chaque soir.", rows=["Matin", "Soir"], done=3),
],
caption="""Un défi simple avec ta brosse à dents électrique : 7 jours, 2 brossages de 2 minutes par jour.

Pas de nouveau matériel, pas de méthode compliquée. Juste la régularité, qui est le vrai facteur d'un sourire en bonne santé.

Capture ce post, coche une case matin et soir. Au bout de 7 jours, l'habitude commence à tenir toute seule.

Tu relèves ?

[CTA]

#brosseadentselectrique #defi7jours #routinedentaire #pulsecare"""),

# ───────────────────────── 16 · 25/11 · pack duo
dict(date="2026-11-25", kind="carousel", da="a", slides=[
  dict(tpl="hero", img=s("p121"), kicker="Pack duo", title="Une brosse pour toi.\n*Une pour l'autre.*", swipe=True),
  dict(tpl="mosaic", tone="sand", kicker="Dans le coffret", title="Deux routines, un seul lavabo", imgs=[(s("duo_etuis"), "2 manches"), (s("duo_acc"), "Les accessoires"), (s("duo_coffret"), "2 étuis")]),
  dict(tpl="arch", kicker="Pack duo", title="Pour deux, *d'un coup*", img=s("p091"), price="94,90 €"),
],
caption="""Le pack duo : deux brosses à dents électriques Pulse Care Bamboo+ pour la maison.

Pour le couple, les colocs, ou toi et ton ado.

Chacun son manche. Chacun ses têtes en bambou. Une seule routine pour toute la salle de bain.

Pack duo : 94,90 € les deux.

Identifie la personne avec qui tu partages ton lavabo.

[CTA]

#brosseadentselectrique #packduo #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 17 · 26/11 · régularité
dict(date="2026-11-26", kind="photo", da="b", tone="forest", slides=[
  dict(tpl="statement", img="u:1706951413911-a4477e18ccd5", kicker="Le vrai secret", title="*La régularité.*", sub="Matin et soir. 2 minutes. Tous les jours. Rien de plus."),
],
caption="""Un sourire en bonne santé ne se joue pas sur un brossage parfait, avec ou sans brosse à dents électrique. Il se joue sur la régularité.

Matin et soir. 2 minutes. Tous les jours.

C'est moins une question de matériel que d'habitude. La brosse aide juste à tenir le rythme : le minuteur s'arrête seul, et tu n'as plus à compter.

Tu brosses déjà 2 fois par jour ? Oui ou non en commentaire.

[CTA]

#brosseadentselectrique #routinedentaire #sourire #pulsecare"""),

# ───────────────────────── 18 · 27/11 · abonnement
dict(date="2026-11-27", kind="carousel", da="c", slides=[
  dict(tpl="hero", img="u:1481708426686-bad08e28e1c2", kicker="Abonnement Pulse Care", title="Oublier de changer ta tête ?\n*Plus possible.*", swipe=True),
  dict(tpl="schema", kind="calendar", kicker="Sur un an", title="4 changements *par an*"),
  dict(tpl="steps", kicker="Comment ça marche", title="En 3 points", items=[("Tu choisis tes têtes", "Poils ricin ou nylon."), ("Elles arrivent chez toi", "Au rythme choisi, sans commande à repasser."), ("Sans engagement", "Tu arrêtes quand tu veux depuis ton compte.")]),
],
caption="""L'abonnement têtes de brosse à dents électrique Pulse Care, en 3 points.

Une tête tous les 3 mois, c'est 4 têtes par an. Le genre de chose qu'on oublie toujours.

→ tu choisis tes têtes, poils ricin ou nylon
→ elles arrivent chez toi au rythme choisi
→ sans engagement, tu arrêtes quand tu veux depuis ton compte

Plus besoin d'y penser.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

# ───────────────────────── 19 · 28/11 · 3 mois
dict(date="2026-11-28", kind="photo", da="a", tone="forest", slides=[
  dict(tpl="bignum", kicker="Le rappel", big="3 mois", title="la durée de vie *d'une tête*", sub="Après, les poils s'écartent et nettoient moins bien.", img=s("ricin_pack4_vue")),
],
caption="""3 mois : c'est la durée de vie d'une tête de brosse à dents électrique.

Passé ce délai, les poils s'écartent vers l'extérieur. Ils ne suivent plus la forme de la dent et retirent moins bien la plaque, même si la tête a l'air propre.

Les 3 signes qu'il est temps :
→ les poils partent sur les côtés
→ la couleur a changé
→ ça fait plus de 3 mois

[CTA]

#brosseadentselectrique #tetederechange #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 20 · 29/11 · FAQ
dict(date="2026-11-29", kind="carousel", da="b", slides=[
  dict(tpl="arch", img=s("p055"), kicker="FAQ Pulse Care", title="Tes questions, *nos réponses*", swipe=True),
  dict(tpl="product", img=s("nylon_pack2"), kicker="Compatibilité", title="Compatible avec *d'autres manches* ?", sub="Non. Les têtes sont conçues uniquement pour les manches Pulse Care."),
  dict(tpl="hero", img="u:1610178169668-530baa052915", kicker="Étanchéité", title="Sous la douche ?", sub="Oui, la brosse est étanche IPX7. Sèche le port USB-C avant de recharger."),
  dict(tpl="product", img=s("p056"), kicker="Autonomie", title="La batterie tient *combien de temps* ?", sub="Jusqu'à 30 jours, pour 2 brossages par jour."),
],
caption="""FAQ brosse à dents électrique Pulse Care : les 3 questions qui reviennent le plus.

Les têtes sont-elles compatibles avec d'autres manches ?
Non. Elles sont conçues uniquement pour les manches Pulse Care.

Je peux l'utiliser sous la douche ?
Oui, elle est étanche IPX7. Pense juste à sécher le port USB-C avant de la recharger.

Combien de temps tient la batterie ?
Jusqu'à 30 jours, pour 2 brossages par jour.

Une autre question ? Pose-la en commentaire.

[CTA]

#brosseadentselectrique #faq #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 21 · 30/11 · bambou
dict(date="2026-11-30", kind="photo", da="c", slides=[
  dict(tpl="hero", img="u:1768593049340-6e50351b4b2f", kicker="Pourquoi le bambou ?", title="Il pousse vite.\n*Il résiste à l'eau.*",
       sub="Sur la Bamboo+, il est sur les têtes et sur l'étui. Le manche, lui, est en plastique ASA."),
],
caption="""Le bambou sur une brosse à dents électrique, pourquoi ce matériau ?

→ il pousse vite, sans replantation
→ il est léger et supporte bien l'humidité de la salle de bain
→ il remplace le plastique sur la tête, la partie qu'on jette le plus souvent

Sur la Bamboo+, le bambou est sur les têtes et sur l'étui de voyage. Le manche est en plastique ASA, choisi pour résister à l'eau et aux chocs pendant des années.

[CTA]

#brosseadentsbambou #brosseadentselectrique #bambou #pulsecare"""),

# ───────────────────────── 22 · 01/12 · plaque et tartre
dict(date="2026-12-01", kind="carousel", da="a", slides=[
  dict(tpl="schema", kind="plaque", tone="forest", kicker="Hygiène dentaire", title="De la plaque *au tartre*", swipe=True),
  dict(tpl="list", img="u:1606811841689-23dfddce3e95", title="Ce qu'il faut retenir", items=[("La plaque, tu l'enlèves", "Avec un brossage de 2 minutes, 2 fois par jour."), ("Le tartre, non", "Il durcit en 24 à 72 h et reste collé."), ("Le détartrage", "Seul un pro peut le retirer.")]),
],
caption="""Plaque et tartre sur une brosse à dents électrique : ce n'est pas la même chose.

La plaque, c'est un film de bactéries qui se dépose en permanence. Souple, elle part au brossage.

Si elle reste, elle se minéralise en 24 à 72 heures et devient du tartre. Dur, accroché à la dent, impossible à retirer avec une brosse.

D'où les 2 minutes, 2 fois par jour. Et le détartrage quand ton dentiste le juge utile.

[CTA]

#brosseadentselectrique #tartre #plaquedentaire #pulsecare"""),

# ───────────────────────── 23 · 02/12 · la brosse
dict(date="2026-12-02", kind="photo", da="c", slides=[
  dict(tpl="arch", kicker="Pulse Care Bamboo+", title="Le manche reste.\n*La tête se change.*", sub="41 000 vibrations/min · 4 modes · 30 jours d'autonomie", img=s("p084"), price="59,90 €"),
],
caption="""La brosse à dents électrique Pulse Care Bamboo+, en une phrase : un manche qu'on garde, des têtes en bambou qu'on change.

→ 41 000 vibrations par minute
→ 4 modes de brossage
→ minuteur 2 minutes, pause toutes les 30 s
→ 30 jours d'autonomie, recharge USB-C
→ étanche IPX7

59,90 € avec 2 têtes, l'étui de voyage et le câble.

[CTA]

""" + TAGS),

# ───────────────────────── 24 · 03/12 · idée cadeau
dict(date="2026-12-03", kind="carousel", da="b", slides=[
  dict(tpl="hero", img="u:1545608444-f045a6db6133", kicker="Idée cadeau", title="Un cadeau *qui sert tous les jours*", swipe=True),
  dict(tpl="mosaic", tone="sand", kicker="Trois budgets", title="Pour qui, à quel prix", imgs=[(s("nylon_pack4_noir"), "Pack de 4 têtes · 14,90 €"), (s("decouverte_contenu"), "Pack découverte · 64,90 €"), (s("deux_brosses"), "Pack duo · 94,90 €")]),
  dict(tpl="statement", img="u:1512909006721-3d6018887383", kicker="Le bon argument", title="Il ne finira pas *au fond d'un tiroir.*", sub="Deux fois par jour, tous les jours, pendant des années."),
],
caption="""Une brosse à dents électrique en cadeau de Noël : l'idée bête qui fait mouche.

Parce que c'est un objet utilisé deux fois par jour, tous les jours, pendant des années. Peu de cadeaux peuvent en dire autant.

Trois budgets :
→ pack de 4 têtes en bambou : 14,90 €
→ pack découverte : 64,90 €
→ pack duo : 94,90 €

Tu offres à qui cette année ?

[CTA]

#brosseadentselectrique #ideecadeau #cadeaunoel #pulsecare"""),

# ───────────────────────── 25 · 04/12 · quiz durée
dict(date="2026-12-04", kind="photo", da="a", tone="mint", slides=[
  dict(tpl="quiz", kicker="Sois honnête", title="Tu brosses *combien de temps* ?",
       options=["Moins d'une minute", "Environ 1 minute", "2 minutes pile", "Plus de 3 minutes"], answer=2,
       note="Le minuteur s'arrête seul à 2 minutes. Plus besoin de compter."),
],
caption="""Avec ou sans brosse à dents électrique : tu brosses combien de temps, honnêtement ?

À l'œil, la plupart des gens s'arrêtent avant une minute, en pensant en avoir fait deux. C'est le biais classique.

La recommandation reste 2 minutes, 2 fois par jour. Sur la Bamboo+, le minuteur s'arrête seul à 2 minutes, avec une pause toutes les 30 secondes pour changer de zone.

Tu es dans quelle case ? Dis-le en commentaire.

[CTA]

#brosseadentselectrique #minuteur #routinedentaire #pulsecare"""),

# ───────────────────────── 26 · 05/12 · ricin ou nylon
dict(date="2026-12-05", kind="carousel", da="c", slides=[
  dict(tpl="product", img=s("ricin_fibres"), kicker="Têtes de recharge", title="Poils *ricin* ou poils *nylon* ?", swipe=True),
  dict(tpl="versus", kicker="Têtes Pulse Care", title="Lequel est *fait pour toi* ?", both_good=True, left=("Poils nylon", ["Brossage plus ferme", "Tu sens bien le nettoyage", "Tête en bambou"]), right=("Poils ricin", ["Fibre d'origine végétale", "Toucher très doux", "Idéal gencives sensibles"])),
  dict(tpl="arch", kicker="Pack de 4", title="Un an *de brossage*", img=s("nylon_pack4"), price="14,90 €"),
],
caption="""Têtes de brosse à dents électrique : poils ricin ou poils nylon ?

Les deux sont montées sur une tête en bambou et se clipsent en une seconde. La différence, c'est la fibre.

→ Ricin : fibre d'origine végétale, toucher très doux, idéal si tes gencives sont sensibles
→ Nylon : brossage plus ferme, pour ceux qui aiment sentir le nettoyage

Pas sûr ? Prends une tête de chaque et compare sur deux semaines.

[CTA]

#brosseadentselectrique #tetederechange #poilsricin #pulsecare"""),

# ───────────────────────── 27 · 06/12 · récap chiffres
dict(date="2026-12-06", kind="photo", da="b", tone="forest", slides=[
  dict(tpl="bignum", big="41 000", title="vibrations par minute, *et tout le reste*", sub="4 modes · minuteur 2 min · 30 jours d'autonomie · étanche IPX7", img=s("p085")),
],
caption="""La brosse à dents électrique Pulse Care Bamboo+ en 4 chiffres.

→ 41 000 vibrations par minute, technologie sonique
→ 4 modes : Sensible, Nettoyage, Blanchiment, Polissage
→ jusqu'à 30 jours d'autonomie, recharge USB-C
→ étanche IPX7, tu peux te brosser sous la douche

Et toujours le même principe : le manche reste, la tête en bambou se change.

[CTA]

""" + TAGS),

# ───────────────────────── 28 · 07/12 · 5 erreurs
dict(date="2026-12-07", kind="carousel", da="a", slides=[
  dict(tpl="arch", img="u:1676897288522-e8a081e71430", kicker="Brosse à dents électrique", title="5 erreurs *à corriger ce soir*", swipe=True),
  dict(tpl="steps", tone="honey", kicker="Les gestes", title="Les 3 premières", items=[("Frotter comme avec une manuelle", "Pose la tête, laisse les vibrations faire."), ("Appuyer fort", "Ça use l'émail et irrite la gencive."), ("Oublier les faces internes", "Le côté langue compte autant.")]),
  dict(tpl="steps", tone="mint", start=4, kicker="La routine", title="Et les 2 dernières", items=[("Rincer juste après", "Crache, ne rince pas : le fluor reste."), ("Garder la même tête 6 mois", "On la change tous les 3 mois.")]),
],
caption="""5 erreurs fréquentes avec une brosse à dents électrique.

1. Frotter comme avec une manuelle : pose la tête et laisse les vibrations travailler
2. Appuyer trop fort : ça use l'émail et fait reculer les gencives
3. Oublier les faces internes, côté langue
4. Rincer juste après : crache le dentifrice, ne rince pas, le fluor agit plus longtemps
5. Garder la même tête 6 mois

Tu te reconnais dans laquelle ? Sois honnête en commentaire.

[CTA]

#brosseadentselectrique #erreursbrossage #conseilsdentaires #pulsecare"""),

# ───────────────────────── 29 · 08/12 · pack de 4
dict(date="2026-12-08", kind="photo", da="c", slides=[
  dict(tpl="product", img=s("ricin_pack4_douce"), kicker="Pack de 4 têtes", title="Prends un pack, *oublie le sujet*", sub="Une tête tous les 3 mois : 4 têtes, c'est un an.", price="14,90 €"),
],
caption="""Têtes de recharge pour brosse à dents électrique : prends un pack de 4 et oublie le sujet pour un an.

Une tête tous les 3 mois. Quatre têtes, douze mois de brossage.

→ têtes en bambou
→ poils ricin ou poils nylon
→ clip en une seconde sur le manche Pulse Care

Pack de 4 : 14,90 €.

[CTA]

#brosseadentselectrique #tetederechange #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 30 · 09/12 · récap
dict(date="2026-12-09", kind="carousel", da="b", slides=[
  dict(tpl="hero", img=s("p004"), kicker="Le récap", title="Pourquoi la *Bamboo+* ?", swipe=True, tw=0.68),
  dict(tpl="bignum", tone="sand", kicker="Le principe", big="1", title="manche, *des têtes à changer*", sub="Le manche dure des années. Seule la tête en bambou se remplace.", img=s("p092")),
  dict(tpl="stats", tone="forest", img=s("etui_plat"), title="En résumé", items=[("41 000", "vibrations par minute"), ("4", "modes de brossage"), ("2 min", "de minuteur intégré"), ("30 j", "d'autonomie")]),
  dict(tpl="arch", tone="fresh", kicker="Pulse Care Bamboo+", title="Avec 2 têtes, *l'étui et le câble*", img=s("p014"), price="59,90 €"),
],
caption="""Pourquoi choisir la brosse à dents électrique Pulse Care Bamboo+ ? Le récap complet.

→ 41 000 vibrations par minute
→ 4 modes de brossage
→ minuteur 2 min avec pause toutes les 30 s
→ 30 jours d'autonomie, recharge USB-C
→ étanche IPX7
→ têtes en bambou, poils ricin ou nylon

Le manche reste des années. Seule la tête se change, tous les 3 mois.

Swipe pour tout voir.

[CTA]

""" + TAGS),
]
