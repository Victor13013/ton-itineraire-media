# -*- coding: utf-8 -*-
"""Pulse Care — calendrier Instagram + Facebook, 30 jours (09/10 → 07/11/2026).

Formats :
  photo    -> 1 visuel 1080x1350
  carousel -> 2 à 10 visuels 1080x1350
  reel     -> vidéo motion design 1080x1920, 30 i/s

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
 "etui": "pulse-care-etui-bambou-ferme-brosse-electrique.webp",
}
def s(k): return "s:" + S[k]

TAGS = "#brosseadentselectrique #brosseadentsbambou #hygienebuccodentaire #pulsecare"

POSTS = [
# ───────────────────────── 1 · REEL
dict(date="2026-10-09", kind="carousel", slides=[
  dict(tpl="hero", img=s("p046"), kicker="Nouveau sur ton lavabo", title="Pulse Care *Bamboo+*", sub="La brosse à dents électrique sonique", swipe=True),
  dict(tpl="stats", img=s("modes_main"), title="Les chiffres clés", items=[("41 000","vibrations par minute"),("4","modes de brossage"),("30 j","d'autonomie"),("IPX7","étanche, même sous la douche")], page="2/4"),
  dict(tpl="hero", img=s("p083"), kicker="Recharge USB-C", title="Jusqu'à 30 jours d'autonomie", page="3/4"),
  dict(tpl="product", img=s("decouverte_tetes"), kicker="Le principe", title="Tu gardes le manche.\n*Tu changes la tête.*", sub="Têtes en bambou, poils ricin ou nylon.", page="4/4"),
],
caption="""Brosse à dents électrique Pulse Care Bamboo+ : on te la présente.

Le principe est simple. Tu gardes le manche. Tu changes seulement la tête, en bambou.

→ 41 000 vibrations par minute (technologie sonique)
→ 4 modes : Sensible, Nettoyage, Blanchiment, Polissage
→ Jusqu'à 30 jours d'autonomie, recharge USB-C
→ Étanche IPX7

[CTA]

""" + TAGS),

# ───────────────────────── 2 · PHOTO
dict(date="2026-10-10", kind="photo", slides=[
  dict(tpl="hero", img="u:1693692273603-3b9e13789298", kicker="La règle de base", title="2 minutes.\n*2 fois par jour.*", sub="Le minuteur s'arrête seul à 2 min, avec une pause toutes les 30 s pour changer de zone."),
],
caption="""2 minutes, 2 fois par jour. C'est la base avec une brosse à dents électrique comme avec une manuelle.

Le problème : à l'œil, on brosse souvent moins d'une minute.

Sur la Bamboo+, le minuteur fait le travail :
→ arrêt automatique à 2 minutes
→ une micro-pause toutes les 30 secondes pour passer à la zone suivante

4 zones x 30 secondes. Haut gauche, haut droite, bas gauche, bas droite.

Tu brosses combien de temps, honnêtement ? Dis-le en commentaire.

[CTA]

#brosseadentselectrique #routinedentaire #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 3 · CAROUSEL
dict(date="2026-10-11", kind="carousel", slides=[
  dict(tpl="hero", img="u:1586061968253-7bf5724aab7b", kicker="Brosse à dents électrique", title="Pourquoi une tête *en bambou* ?", swipe=True),
  dict(tpl="list", img=s("ricin_profil"), title="Ce qui compose ta brosse", items=[("Tête en bambou","La partie que tu changes tous les 3 mois."),("Poils à base de ricin","Une fibre d'origine végétale."),("Manche en plastique ASA","Conçu pour durer des années.")], page="2/3"),
  dict(tpl="statement", img="u:1761311554695-68cfca1f3140", kicker="Le concept", title="Moins de plastique dans la partie que tu jettes.", page="3/3"),
],
caption="""Pourquoi une tête de brosse à dents électrique en bambou ?

Parce que la tête, c'est la partie que tu jettes tous les 3 mois. Le manche, lui, reste.

Chez Pulse Care :
→ la tête est en bambou
→ les poils sont à base d'huile de ricin, d'origine végétale
→ le manche est en plastique ASA, conçu pour durer des années

Swipe pour le détail.

[CTA]

#brosseadentsbambou #brosseadentselectrique #bambou #pulsecare"""),

# ───────────────────────── 4 · REEL
dict(date="2026-10-12", kind="carousel", slides=[
  dict(tpl="hero", img=s("icones"), kicker="Brosse à dents électrique", title="Quel mode *choisir* ?", swipe=True),
  dict(tpl="list", img=s("p090"), title="Au quotidien", items=[("Sensible","Gencives fragiles, débuts à l'électrique."),("Nettoyage","Matin et soir, tous les jours.")], page="2/3"),
  dict(tpl="list", img=s("p019"), title="En complément", items=[("Blanchiment","Taches de surface : café, thé."),("Polissage","Sensation de dents lisses.")], page="3/3", alt=True),
],
caption="""4 modes sur ta brosse à dents électrique : lequel choisir ?

→ Sensible : vibrations adoucies, pour les gencives qui saignent ou les dents sensibles
→ Nettoyage : le mode de tous les jours
→ Blanchiment : pour aider à retirer les taches de surface (café, thé)
→ Polissage : pour finir avec une sensation de dents lisses

Astuce : commence 1 à 2 semaines en mode Sensible si tu passes d'une brosse manuelle à l'électrique.

[CTA]

#brosseadentselectrique #brosseadentssonique #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 5 · PHOTO
dict(date="2026-10-13", kind="photo", slides=[
  dict(tpl="product", img=s("ricin_gp"), kicker="Gros plan", title="Des poils à base *de ricin*", sub="Fibre d'origine végétale, douce pour l'émail et les gencives."),
],
caption="""Gros plan sur les poils de nos têtes de brosse à dents électrique.

Ils sont fabriqués à base d'huile de ricin. Une fibre d'origine végétale, à la place des poils 100 % pétrole.

Au brossage, ils sont doux pour l'émail et les gencives sensibles. Et ils retirent la plaque comme il faut.

Monté sur une tête en bambou. Compatible uniquement avec les manches Pulse Care.

[CTA]

#brosseadentselectrique #brosseadentsbambou #gencivessensibles #pulsecare"""),

# ───────────────────────── 6 · CAROUSEL
dict(date="2026-10-14", kind="carousel", slides=[
  dict(tpl="statement", img="u:1563635707334-5ce91b375ea6", kicker="Question du jour", title="Tu changes ta tête de brosse tous les combien ?", sub="A. Tous les 3 mois\nB. Quand les poils s'écartent\nC. Euh... jamais", swipe=True),
  dict(tpl="product", img=s("tete_main"), kicker="La réponse", title="Tous les *3 mois*", sub="Et après un rhume ou une angine.", page="2/2"),
],
caption="""Question rapide sur ta brosse à dents électrique : tu changes ta tête tous les combien ?

A. Tous les 3 mois
B. Quand les poils partent dans tous les sens
C. Euh... jamais ?

Réponds en commentaire avant de swiper. On ne juge pas.

La bonne réponse : tous les 3 mois. C'est la recommandation des dentistes. Après ça, les poils s'écartent et retirent moins bien la plaque.

[CTA]

#brosseadentselectrique #hygienebuccodentaire #routinedentaire #pulsecare"""),

# ───────────────────────── 7 · REEL
dict(date="2026-10-15", kind="carousel", slides=[
  dict(tpl="hero", img="u:1646388478486-0996b6dcc2ac", kicker="Brosse à dents électrique", title="5 erreurs de brossage à corriger", swipe=True),
  dict(tpl="list", img="u:1654373535457-383a0a4d00f9", title="Les erreurs de geste", numbered=True, items=[("Frotter","Pose la tête, les vibrations nettoient."),("Appuyer fort","Ça use l'émail et irrite les gencives."),("Oublier l'arrière","La face interne des dents.")], page="2/3"),
  dict(tpl="list", img="u:1609840113929-b130355987e1", title="Les erreurs de routine", numbered=True, start=4, items=[("Rincer juste après","Crache, ne rince pas : le fluor reste."),("Garder la même tête","On la change tous les 3 mois.")], page="3/3", alt=True),
],
caption="""5 erreurs fréquentes avec une brosse à dents électrique.

1. Frotter comme avec une manuelle. Pose la tête et laisse les vibrations bosser.
2. Appuyer trop fort. Ça abîme les gencives.
3. Oublier l'arrière des dents.
4. Rincer juste après. Crache le dentifrice, ne rince pas : le fluor agit plus longtemps.
5. Garder la même tête 6 mois.

Tu te reconnais dans laquelle ?

[CTA]

#brosseadentselectrique #conseilsdentaires #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 8 · PHOTO
dict(date="2026-10-16", kind="photo", slides=[
  dict(tpl="product", img=s("decouverte_neutre"), kicker="Pack découverte", title="Pour passer à l'électrique", sub="Le manche Bamboo+ et des têtes en bambou à poils de ricin.", price="64,90 €"),
],
caption="""Le pack découverte Pulse Care, pour passer à la brosse à dents électrique en bambou.

Dedans : le manche Bamboo+ et des têtes en bambou à poils de ricin pour tenir plusieurs mois.

Une bonne idée pour te lancer. Ou pour offrir à quelqu'un qui galère encore avec sa brosse manuelle.

Pack découverte : 64,90 €.

[CTA]

#brosseadentselectrique #brosseadentsbambou #ideecadeau #pulsecare"""),

# ───────────────────────── 9 · CAROUSEL
dict(date="2026-10-17", kind="carousel", slides=[
  dict(tpl="hero", img="u:1635286771551-9d7241ce7811", kicker="Brosse à dents électrique", title="La routine du soir compte plus que celle du matin", swipe=True),
  dict(tpl="list", img="u:1693693476268-867d0e6eda85", title="Ta routine en 4 étapes", numbered=True, items=[("Fil dentaire","Ou brossettes entre les dents."),("2 minutes de brossage","Mode Nettoyage."),("Tu craches, tu ne rinces pas","Le fluor reste sur les dents."),("Plus rien à manger","Jusqu'au lendemain matin.")], page="2/2"),
],
caption="""La routine du soir compte plus que celle du matin pour ta brosse à dents électrique.

Pourquoi ? La nuit, tu produis moins de salive. Les bactéries ont le champ libre.

Ta routine en 4 étapes :
→ fil dentaire ou brossettes
→ 2 minutes de brossage, mode Nettoyage
→ crache, ne rince pas
→ plus rien à manger après

Enregistre ce post pour ce soir.

[CTA]

#brosseadentselectrique #routinedusoir #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 10 · REEL
dict(date="2026-10-18", kind="carousel", slides=[
  dict(tpl="hero", img="u:1553691158-91a7f9183156", kicker="Le match", title="Manuelle ou *électrique* ?", swipe=True),
  dict(tpl="list", img="u:1553691475-f38e4026275b", title="Ce que l'électrique change", items=[("41 000 vibrations par minute","Tu guides, elle nettoie."),("Minuteur 2 minutes","Plus de brossage bâclé."),("Mode Sensible","Pour les gencives fragiles.")], page="2/3"),
  dict(tpl="product", img=s("bamboo_face"), kicker="Pulse Care Bamboo+", title="Prête à passer à l'électrique ?", sub="2 têtes, étui et câble USB-C inclus.", price="59,90 €", page="3/3"),
],
caption="""Brosse à dents électrique ou manuelle : laquelle choisir ?

La manuelle marche si ta technique est parfaite. Bon angle, bon mouvement, 2 minutes pile.

La brosse à dents électrique sonique te facilite la vie :
→ 41 000 vibrations par minute, tu n'as qu'à guider
→ minuteur intégré, plus de brossage bâclé
→ un mode Sensible pour les gencives fragiles

Team manuelle ou team électrique ?

[CTA]

#brosseadentselectrique #brosseadentssonique #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 11 · PHOTO
dict(date="2026-10-19", kind="photo", slides=[
  dict(tpl="stats", img=s("usb"), title="Recharge USB-C", items=[("2,5 h","de charge environ"),("30 j","d'autonomie"),("500","mAh, batterie lithium"),("USB-C","le câble de ton téléphone")]),
],
caption="""Une brosse à dents électrique qui se recharge en USB-C. Le même câble que ton téléphone.

→ environ 2,5 heures de charge
→ jusqu'à 30 jours d'autonomie
→ batterie lithium 500 mAh

Une charge par mois. Pas de socle encombrant sur le lavabo.

[CTA]

#brosseadentselectrique #usbc #brosseadentsrechargeable #pulsecare"""),

# ───────────────────────── 12 · PHOTO
dict(date="2026-10-20", kind="photo", slides=[
  dict(tpl="hero", img="u:1620626011761-996317b8d101", kicker="Étanche IPX7", title="Sous la douche ?\n*Aucun problème.*", sub="Ta brosse résiste à l'immersion. Sèche juste le port USB-C avant de la recharger."),
],
caption="""IPX7 sur ta brosse à dents électrique, ça veut dire quoi ?

Elle résiste à l'immersion dans l'eau. Concrètement :
→ tu peux te brosser les dents sous la douche
→ tu la rinces sous le robinet sans stress
→ les éclaboussures du lavabo ne posent aucun problème

Pense juste à bien sécher le port USB-C avant de la recharger.

[CTA]

#brosseadentselectrique #ipx7 #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 13 · REEL
dict(date="2026-10-21", kind="carousel", slides=[
  dict(tpl="hero", img=s("p121"), kicker="Pack duo", title="Une brosse pour toi.\n*Une pour l'autre.*", swipe=True),
  dict(tpl="list", img=s("duo_acc"), title="Dans la boîte", items=[("2 manches Bamboo+","41 000 vibrations par minute."),("Des têtes en bambou","Chacun les siennes."),("Étuis de voyage","En bambou.")], page="2/3"),
  dict(tpl="product", img=s("p091"), kicker="Pack duo", title="Une routine pour toute la salle de bain", price="94,90 €", page="3/3"),
],
caption="""Le pack duo : deux brosses à dents électriques Pulse Care Bamboo+ pour la maison.

Pour le couple. Pour les colocs. Pour toi et ton ado.

Chacun son manche. Chacun ses têtes en bambou. Une seule routine pour toute la salle de bain.

Pack duo : 94,90 € les deux.

Identifie la personne avec qui tu partages ton lavabo.

[CTA]

#brosseadentselectrique #packduo #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 14 · PHOTO
dict(date="2026-10-22", kind="photo", slides=[
  dict(tpl="hero", img="u:1629909613654-28e377c37b09", kicker="Rappel", title="Ta brosse ne remplace pas ton dentiste.", sub="Un contrôle par an. Le tartre, seul un pro peut l'enlever."),
],
caption="""Une bonne brosse à dents électrique ne remplace pas le dentiste.

Le rythme conseillé : un contrôle par an, et un détartrage selon ce que ton dentiste recommande.

Ta brosse retire la plaque au quotidien. Le tartre, une fois installé, seul un pro peut l'enlever.

Ton dernier rendez-vous date de quand ?

[CTA]

#brosseadentselectrique #dentiste #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 15 · CAROUSEL
dict(date="2026-10-23", kind="carousel", slides=[
  dict(tpl="statement", img="u:1489278353717-f64c6ee8a4d2", kicker="Vrai ou faux", title="Appuyer fort =\n*dents plus propres ?*", swipe=True),
  dict(tpl="list", img="u:1693692258834-74c62f467cb7", title="FAUX. Voilà la bonne méthode", items=[("Tête posée en douceur","Angle de 45° vers la gencive."),("Tu glisses lentement","D'une dent à l'autre."),("Aucune pression","Les vibrations nettoient, toi tu guides.")], page="2/2"),
],
caption="""Vrai ou faux : plus tu appuies fort avec ta brosse à dents électrique, plus tes dents sont propres ?

FAUX.

Appuyer fort use l'émail et fait reculer les gencives. Avec une brosse sonique, ce sont les vibrations qui nettoient.

Swipe pour la bonne méthode.

[CTA]

#brosseadentselectrique #vraioufaux #conseilsdentaires #pulsecare"""),

# ───────────────────────── 16 · REEL
dict(date="2026-10-24", kind="carousel", slides=[
  dict(tpl="hero", img="u:1502301197179-65228ab57f78", kicker="Vacances de la Toussaint", title="Laisse le chargeur *à la maison*", swipe=True),
  dict(tpl="product", img=s("etui"), kicker="Inclus", title="Un étui de voyage en bambou", sub="Pour protéger la tête dans ta trousse.", page="2/3"),
  dict(tpl="stats", img="u:1764909262009-3dcd5691185c", title="En voyage", items=[("30 j","d'autonomie, pas besoin du chargeur"),("USB-C","le câble de ton téléphone"),("IPX7","douche d'hôtel ok"),("Étui","en bambou, inclus")], page="3/3"),
],
caption="""Partir en vacances avec sa brosse à dents électrique, sans le chargeur.

Avec 30 jours d'autonomie, la Bamboo+ tient tout ton séjour.

Dans la boîte :
→ un étui de voyage en bambou pour protéger la tête
→ un câble USB-C si tu pars longtemps

Vacances de la Toussaint, week-end, déplacement pro : elle rentre dans toutes les trousses.

[CTA]

#brosseadentselectrique #voyage #troussedetoilette #pulsecare"""),

# ───────────────────────── 17 · CAROUSEL
dict(date="2026-10-25", kind="carousel", slides=[
  dict(tpl="hero", img=s("ricin_arriere"), kicker="Brosse à dents électrique", title="3 signes qu'il faut changer ta tête", swipe=True),
  dict(tpl="list", img=s("ricin_solo"), title="Change-la si...", items=[("Les poils s'écartent","Ils nettoient moins bien."),("La couleur a changé","Signe d'usure."),("Ça fait plus de 3 mois","Même si elle a l'air propre.")], page="2/3"),
  dict(tpl="product", img=s("ricin_pack2"), kicker="Têtes de recharge", title="Clip en une seconde", sub="Têtes en bambou, poils ricin ou nylon.", page="3/3"),
],
caption="""3 signes qu'il est temps de changer la tête de ta brosse à dents électrique :

→ les poils s'écartent vers l'extérieur
→ la couleur des poils a changé
→ ça fait plus de 3 mois

Change-la aussi après une angine ou un gros rhume.

Nos têtes de recharge sont en bambou, avec poils ricin ou nylon. Elles se clipsent en une seconde sur le manche Pulse Care.

[CTA]

#brosseadentselectrique #tetederechange #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 18 · PHOTO
dict(date="2026-10-26", kind="photo", slides=[
  dict(tpl="hero", img="u:1494790108377-be9c29b29330", kicker="Astuce haleine fraîche", title="Et ta langue,\n*tu la brosses ?*", sub="3 ou 4 passages doux, de l'arrière vers l'avant."),
],
caption="""Ta brosse à dents électrique fait le boulot sur les dents. Mais tu brosses ta langue ?

Une grande partie des bactéries responsables de la mauvaise haleine vit sur la langue.

Le geste : après tes 2 minutes, passe doucement la brosse de l'arrière vers l'avant de la langue, 3 ou 4 fois. Moteur coupé ou mode Sensible.

10 secondes de plus. Haleine plus fraîche.

[CTA]

#brosseadentselectrique #haleinefraiche #astucesante #pulsecare"""),

# ───────────────────────── 19 · REEL
dict(date="2026-10-27", kind="carousel", slides=[
  dict(tpl="hero", img=s("ricin_fibres"), kicker="Têtes de recharge", title="Poils *ricin* ou poils *nylon* ?", swipe=True),
  dict(tpl="list", img=s("ricin_face"), title="Poils ricin", items=[("Fibre d'origine végétale","À base d'huile de ricin."),("Toucher très doux","Idéal gencives sensibles.")], page="2/3"),
  dict(tpl="list", img=s("nylon_face"), title="Poils nylon", items=[("Brossage plus ferme","Tu sens bien le nettoyage."),("Tête en bambou","Comme la version ricin.")], page="3/3", alt=True),
],
caption="""Têtes de brosse à dents électrique : poils ricin ou poils nylon ?

Les deux sont montés sur une tête en bambou. La différence, c'est la fibre.

→ Ricin : fibre d'origine végétale, toucher très doux. Idéal gencives sensibles.
→ Nylon : sensation de brossage plus ferme, pour ceux qui aiment sentir le nettoyage.

Pas sûr ? Prends une tête de chaque et compare.

[CTA]

#brosseadentselectrique #brosseadentsbambou #tetederechange #pulsecare"""),

# ───────────────────────── 20 · CAROUSEL
dict(date="2026-10-28", kind="carousel", slides=[
  dict(tpl="hero", img="u:1676897288522-e8a081e71430", kicker="Brosse à dents électrique", title="Dans quel ordre faire les choses ?", swipe=True),
  dict(tpl="list", img="u:1631048499052-e6d9f305d2c0", title="L'ordre qui compte", numbered=True, items=[("Fil dentaire","Ou brossettes."),("Brossage 2 minutes","Le minuteur gère le temps."),("Tu craches",""),("Tu ne rinces PAS","Le fluor reste sur les dents.")], page="2/2"),
],
caption="""Brosse à dents électrique : dans quel ordre faire les choses ?

1. Fil dentaire ou brossettes
2. Brossage 2 minutes
3. Tu craches le dentifrice
4. Tu ne rinces PAS à l'eau

Rincer enlève le fluor du dentifrice. En ne rinçant pas, il reste sur les dents plus longtemps.

Tu rinces, toi ? Sois honnête.

[CTA]

#brosseadentselectrique #conseilsdentaires #routinedentaire #pulsecare"""),

# ───────────────────────── 21 · PHOTO
dict(date="2026-10-29", kind="photo", slides=[
  dict(tpl="hero", img=s("p095"), kicker="Pulse Care Bamboo+", title="Rien de plus sur ton lavabo.", sub="41 000 vibrations/min · 4 modes · 30 jours d'autonomie", price="59,90 €"),
],
caption="""La brosse à dents électrique Pulse Care Bamboo+, version salle de bain.

Un manche sobre. Une tête en bambou. Rien de plus sur ton lavabo.

41 000 vibrations par minute, 4 modes, 30 jours d'autonomie.

59,90 € avec 2 têtes en bambou, l'étui de voyage et le câble USB-C.

[CTA]

#brosseadentselectrique #salledebain #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 22 · REEL
dict(date="2026-10-30", kind="carousel", slides=[
  dict(tpl="hero", img="u:1651146494264-1b3a54f71175", kicker="Brosse à dents électrique", title="Une routine qui tient en famille", swipe=True),
  dict(tpl="list", img="u:1780327065542-80cc74036b04", title="Astuces 1 et 2", numbered=True, items=[("Même heure chaque soir","Juste après le pyjama."),("Parents en même temps","Les enfants copient ce qu'ils voient.")], page="2/3"),
  dict(tpl="list", img="u:1611690061822-b707a67bfebb", title="Astuces 3 et 4", numbered=True, start=3, items=[("Le minuteur = un défi","Qui tient les 2 minutes ?"),("Chacun sa tête","Un repère par personne.")], page="3/3", alt=True),
],
caption="""Brosse à dents électrique : 4 astuces pour une routine qui tient en famille.

1. Même heure tous les soirs, juste après le pyjama
2. Les parents se brossent en même temps que les enfants
3. Le minuteur de 2 minutes devient un défi
4. Chacun son repère pour ne pas mélanger les têtes

Pour les enfants, demande à ton dentiste le type de brosse adapté à leur âge.

[CTA]

#brosseadentselectrique #routinefamille #parents #pulsecare"""),

# ───────────────────────── 23 · PHOTO
dict(date="2026-10-31", kind="photo", slides=[
  dict(tpl="statement", img="u:1612715623676-a68370d10596", kicker="Halloween", title="Bonbons ok.\n*Brossage obligatoire.*", sub="Mange-les d'un coup, bois de l'eau, 2 minutes de brossage avant de dormir."),
],
caption="""Halloween et brosse à dents électrique : le plan de survie.

Les bonbons, ce n'est pas le problème. C'est le grignotage toute la soirée.

→ mange-les d'un coup plutôt qu'en continu
→ bois de l'eau après
→ brossage de 2 minutes avant de dormir, sans exception

Et toi, team bonbons acides ou team chocolat ?

[CTA]

#brosseadentselectrique #halloween #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 24 · PHOTO
dict(date="2026-11-01", kind="photo", slides=[
  dict(tpl="hero", img="u:1525124480298-565f20ea00ae", kicker="Pourquoi le bambou ?", title="Il pousse vite.\n*Il résiste à l'eau.*", sub="Sur la Bamboo+, il est sur les têtes et l'étui. Le manche est en plastique ASA."),
],
caption="""Le bambou dans ta brosse à dents électrique, pourquoi ce matériau ?

→ il pousse vite, sans besoin de replanter
→ il est léger et résiste à l'eau
→ il remplace le plastique sur la tête, la partie que tu jettes le plus souvent

Sur la Bamboo+, le bambou est sur les têtes et l'étui de voyage. Le manche, lui, est en plastique ASA pour résister à l'eau et aux chocs.

[CTA]

#brosseadentsbambou #brosseadentselectrique #bambou #pulsecare"""),

# ───────────────────────── 25 · REEL
dict(date="2026-11-02", kind="carousel", slides=[
  dict(tpl="hero", img=s("decouverte_main"), kicker="Tuto", title="Bien utiliser ta brosse à dents électrique", swipe=True),
  dict(tpl="list", img=s("tete_main2"), title="Étape 1 : avant d'allumer", items=[("Dentifrice sur la tête","Une noisette suffit."),("Tête sur les dents, PUIS on allume","Zéro éclaboussure.")], page="2/3"),
  dict(tpl="list", img="u:1693692282136-2eeb24c11856", title="Étapes 2 et 3 : pendant", items=[("Angle de 45°","Poils vers la gencive."),("Dent par dent","Tu glisses, tu ne frottes pas."),("30 s par zone","La micro-pause te dit quand changer.")], page="3/3", alt=True),
],
caption="""Bien utiliser ta brosse à dents électrique en 3 étapes.

1. Mets le dentifrice sur la tête, place-la sur les dents AVANT d'allumer. Sinon, éclaboussures garanties.
2. Angle de 45° vers la gencive. Tu glisses dent par dent, sans frotter.
3. Suis le minuteur : 30 secondes par zone, la micro-pause te dit quand changer.

Enregistre ce post pour l'avoir sous la main.

[CTA]

#brosseadentselectrique #tuto #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 26 · PHOTO
dict(date="2026-11-03", kind="photo", slides=[
  dict(tpl="hero", img=s("p087"), kicker="Pulse Care", title="Un manche qu'on garde.\n*Des têtes qu'on change.*"),
],
caption="""Une brosse à dents électrique. Un manche qu'on garde. Des têtes en bambou qu'on change.

C'est notre façon de voir l'hygiène bucco-dentaire chez Pulse Care.

Tu veux qu'on parle de quoi dans les prochains posts ? Dis-le en commentaire.

[CTA]

#brosseadentselectrique #brosseadentsbambou #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 27 · CAROUSEL
dict(date="2026-11-04", kind="carousel", slides=[
  dict(tpl="hero", img="u:1733425992462-0f674e744ead", kicker="FAQ Pulse Care", title="Tes questions, nos réponses", swipe=True),
  dict(tpl="product", img=s("nylon_pack2"), kicker="Compatibilité", title="Têtes compatibles avec d'autres marques ?", sub="Non. Elles sont conçues uniquement pour les manches Pulse Care.", page="2/4"),
  dict(tpl="hero", img="u:1631889993959-41b4e9c6e3c5", kicker="Étanchéité", title="Sous la douche ?", sub="Oui. La brosse est étanche IPX7.", page="3/4"),
  dict(tpl="product", img=s("p056"), kicker="Autonomie", title="Combien de temps tient la batterie ?", sub="Jusqu'à 30 jours, pour 2 brossages par jour.", page="4/4"),
],
caption="""FAQ brosse à dents électrique Pulse Care : on répond à tes questions.

Les têtes sont-elles compatibles avec d'autres marques ?
Non. Elles sont conçues uniquement pour les manches Pulse Care.

Je peux l'utiliser sous la douche ?
Oui, elle est étanche IPX7.

Combien de temps dure la batterie ?
Jusqu'à 30 jours, pour 2 brossages par jour.

Une autre question ? Pose-la en commentaire.

[CTA]

#brosseadentselectrique #faq #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 28 · REEL
dict(date="2026-11-05", kind="carousel", slides=[
  dict(tpl="hero", img=s("ricin_pack4"), kicker="Têtes de recharge", title="Prends un pack, oublie le sujet", swipe=True),
  dict(tpl="statement", img="u:1609879937493-56540300d8cc", kicker="Une tête tous les 3 mois", title="4 têtes =\n*1 an de brossage*", page="2/3"),
  dict(tpl="product", img=s("ricin_pack4_vue"), kicker="Pack de 4", title="Poils ricin ou nylon", sub="Têtes en bambou, clip en une seconde.", price="14,90 €", page="3/3"),
],
caption="""Têtes de recharge pour brosse à dents électrique : prends un pack, oublie le sujet.

Une tête tous les 3 mois. Un pack de 4, c'est un an de brossage.

→ en poils ricin ou en poils nylon
→ têtes en bambou
→ clip en une seconde sur ton manche Pulse Care

Pack de 4 : 14,90 €.

[CTA]

#brosseadentselectrique #tetederechange #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 29 · PHOTO
dict(date="2026-11-06", kind="photo", slides=[
  dict(tpl="hero", img="u:1617812191081-2a24e3f30e45", kicker="Le vrai secret", title="*La régularité.*", sub="Matin et soir. 2 minutes. Tous les jours."),
],
caption="""Un beau sourire, ça ne se joue pas sur un brossage. Ça se joue sur la régularité, avec ou sans brosse à dents électrique.

Matin et soir. 2 minutes. Tous les jours.

C'est moins une question de matériel que d'habitude. La brosse t'aide juste à tenir le rythme.

Tu brosses déjà 2 fois par jour ? Oui ou non en commentaire.

[CTA]

#brosseadentselectrique #sourire #routinedentaire #pulsecare"""),

# ───────────────────────── 30 · CAROUSEL
dict(date="2026-11-07", kind="carousel", slides=[
  dict(tpl="hero", img=s("p088"), kicker="Le récap", title="Pourquoi la *Bamboo+* ?", swipe=True),
  dict(tpl="stats", img=s("decouverte_contenu"), title="En résumé", items=[("41 000","vibrations par minute"),("4","modes de brossage"),("30 j","d'autonomie, USB-C"),("IPX7","étanche")], page="2/4"),
  dict(tpl="list", img=s("duo_tete"), title="Et aussi", items=[("Minuteur 2 minutes","Pause toutes les 30 s."),("Têtes en bambou","Poils ricin ou nylon."),("Étui de voyage","En bambou, inclus.")], page="3/4", alt=True),
  dict(tpl="product", img=s("p097"), kicker="Pulse Care Bamboo+", title="Le manche reste.\n*La tête se change.*", sub="Avec 2 têtes, l'étui et le câble USB-C.", price="59,90 €", page="4/4"),
],
caption="""Pourquoi choisir la brosse à dents électrique Pulse Care Bamboo+ ? Le récap.

→ 41 000 vibrations par minute
→ 4 modes de brossage
→ minuteur 2 min avec pause toutes les 30 s
→ 30 jours d'autonomie, recharge USB-C
→ étanche IPX7
→ têtes en bambou, poils ricin ou nylon

Swipe pour tout voir.

[CTA]

#brosseadentselectrique #brosseadentsbambou #hygienebuccodentaire #pulsecare"""),
]
