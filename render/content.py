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

# ─────────────────────────────────────────────────────────────────────────────
# Créneau de 18h : posts commerciaux. Un angle = un besoin client identifié.
# Structure : accroche sur la situation → objection levée → preuve → offre.
# Les avis cités sont des avis clients publiés sur la fiche produit (Opinew).
# ─────────────────────────────────────────────────────────────────────────────
LIV = "Livraison gratuite en point relais dès 20 € d'achat."
RET = "30 jours pour changer d'avis."

POSTS = [
# ── 0a · ANGLE : le coût caché des têtes de rechange (source Que Choisir)
dict(date="x", kind="carousel", slides=[
  dict(tpl="bignum", kicker="Le coût qu'on oublie", big="4 à 15 €", title="la tête de rechange, *ailleurs*", sub="À changer tous les 3 mois. Que Choisir parle d'un coût d'usage « non négligeable ».", swipe=True),
  dict(tpl="versus", kicker="Chez Pulse Care", title="Ce que tu paies *par tête*", both_good=True, left=("À l'unité", ["5,50 € la tête", "Pour tester une fibre", "Ricin ou nylon"]), right=("Pack de 4", ["3,73 € la tête", "Un an de brossage", "14,90 € le pack"])),
  dict(tpl="arch", img=s("ricin_pack4_vue"), kicker="Pack de 4 têtes", title="Un an, *14,90 €*", sub=LIV, price="14,90 €"),
],
caption="""Avant d'acheter une brosse à dents électrique, regarde le prix des têtes de rechange. C'est là que se joue le vrai budget.

Que Choisir chiffre la brossette entre 4 et 15 € selon les marques, à changer tous les 3 mois, et parle d'un coût d'usage « non négligeable ».

Chez Pulse Care :
→ 5,50 € la tête à l'unité
→ 3,73 € la tête en pack de 4, soit 14,90 €

Une tête tous les 3 mois, donc 14,90 € pour l'année. Et le manche, tu le gardes.

[CTA]

#brosseadentselectrique #tetederechange #budget #pulsecare"""),

# ── 0b · ANGLE : est-ce vraiment plus efficace ? (revue Cochrane)
dict(date="x", kind="carousel", slides=[
  dict(tpl="fear", kicker="Ce que tu te dis", fear="Je brosse bien à la main, je vois pas ce que ça changerait.", kicker2="Ce que disent les essais", answer="L'écart se creuse *avec le temps*", sub="11 % de plaque en moins à 3 mois. 21 % au-delà. Revue Cochrane, des dizaines d'essais.", swipe=True),
  dict(tpl="bignum", kicker="Revue Cochrane", big="- 21 %", title="de plaque dentaire *au-delà de 3 mois*", sub="Et environ 11 % de gingivite en moins. Preuves de qualité modérée, sur des dizaines d'essais."),
  dict(tpl="steps", kicker="Ce que ça veut dire", title="À retenir", items=[("L'écart est réel", "Mesuré sur des milliers de participants."), ("Il grandit avec le temps", "11 % de plaque à 3 mois, 21 % après."), ("Le geste compte toujours", "2 minutes, zéro pression, tous les jours.")]),
],
caption="""« Une brosse à dents électrique, c'est vraiment mieux ? » La réponse honnête existe, et elle est chiffrée.

La revue Cochrane, qui compile des dizaines d'essais cliniques, a comparé brosses électriques et manuelles :
→ environ 11 % de plaque en moins entre 1 et 3 mois
→ environ 21 % en moins au-delà de 3 mois
→ environ 6 % puis 11 % de gingivite en moins

Les auteurs classent ces preuves en qualité modérée et rappellent que la portée clinique reste à préciser.

Traduction : l'écart est réel et il grandit avec le temps. Mais le geste reste décisif.

[CTA]

#brosseadentselectrique #cochrane #hygienebuccodentaire #pulsecare"""),

# ── 0c · ANGLE : transparence, ce qu'on ne te dira pas
dict(date="x", kind="carousel", slides=[
  dict(tpl="editorial", img="u:1583642037383-861ac716c3f0", over="Notre parti pris", kicker="Transparence", title="On réduit *la partie qu'on jette*", sub="Pas de label inventé, pas de promesse invérifiable. Un manche gardé des années, et 4 grammes de bambou tous les 3 mois.", swipe=True),
  dict(tpl="steps", kicker="Ce qui est vrai", title="Les faits, sans enrobage", items=[("La tête est en bambou", "C'est la partie remplacée tous les 3 mois."), ("Les poils viennent du ricin", "Une fibre végétale, à la place du pétrole."), ("Le manche est en plastique ASA", "Choisi pour durer des années, pas pour être joli à dire.")]),
  dict(tpl="offer", img=s("p006"), kicker="Notre parti pris", title="Réduire la partie *qu'on jette*", price="59,90 €", perks=["Tête en bambou", "Poils en ricin", "Manche gardé des années"]),
],
caption="""Beaucoup de marques de brosse à dents électrique à tête en bambou promettent beaucoup. On préfère être clairs sur ce que fait la nôtre, et sur ce qu'elle ne fait pas.

Ce qui est vrai :
→ la tête, remplacée tous les 3 mois, est en bambou
→ les poils sont à base d'huile de ricin, une fibre végétale qui remplace une partie du pétrole
→ le manche est en plastique ASA, choisi pour durer des années

Ce qu'on ne dira pas : que des poils en fibre végétale disparaissent tout seuls dans la nature. Ce n'est pas le cas, chez nous comme ailleurs.

Notre parti pris tient en une phrase : réduire la partie qu'on jette, pas l'objet entier.

[CTA]

#brosseadentselectrique #brosseadentsbambou #transparence #pulsecare"""),

# ── 0d · ANGLE : assumer les défauts
dict(date="x", kind="carousel", slides=[
  dict(tpl="note", img=s("p017"), kicker="Ce qu'on pense des marques", bad="Elles ne montrent que les bons avis.", hand="chez nous :", good="Les *deux reproches* sont sur la fiche produit.", sub="On ne masque rien, tu lis tout avant de payer.", swipe=True),
  dict(tpl="versus", kicker="Ce qu'on nous dit", title="Les critiques, *telles quelles*", both_good=True, left=("Le manche", ["« Un peu plus épais que prévu »", "Gênant les premiers jours", "On s'y habitue vite"]), right=("Les vibrations", ["« Vibre un peu plus fort »", "Surtout si tu viens d'une autre brosse", "Le mode Sensible les adoucit"])),
  dict(tpl="arch", img="u:1706951413911-a4477e18ccd5", kicker="Avis vérifiés", title="Tout est public *sur la fiche produit*", sub=RET, price="59,90 €"),
],
caption="""On publie tous les avis sur notre brosse à dents électrique, y compris les critiques. Voici les deux qui reviennent.

1. « Le manche est un peu plus épais que ce que j'imaginais, ce qui peut gêner au début. » C'est vrai. La prise en main est large, et l'habitude vient en quelques jours.

2. « Elle vibre un peu plus fort que ma précédente brosse électrique. » Vrai aussi, surtout en mode Nettoyage. Le mode Sensible adoucit nettement.

Les deux clients concernés ont quand même gardé la brosse et laissé un avis positif.

On préfère que tu saches avant d'acheter. 30 jours pour changer d'avis, dans tous les cas.

[CTA]

""" + TAGS),

# ── 1 · ANGLE : le vrai coût d'une brosse manuelle
dict(date="x", kind="carousel", slides=[
  dict(tpl="bignum", kicker="Le calcul", big="4 ×", title="par an, tu rachètes *une brosse entière*", sub="Manche compris. Alors que seule la tête est usée.", swipe=True),
  dict(tpl="versus", kicker="La différence", title="Ce que tu paies *vraiment*", left=("Brosse manuelle", ["Tout part tous les 3 mois", "Manche racheté 4 fois par an", "Pas de minuteur"]), right=("Pulse Care", ["Seule la tête se change", "Le manche reste des années", "Minuteur 2 min intégré"])),
  dict(tpl="arch", img="u:1593183230686-69876b0cb240", kicker="Pack de 4 têtes", title="Un an de brossage, *14,90 €*", sub=LIV, price="14,90 €"),
],
caption="""Une brosse à dents électrique coûte cher au départ. Mais fais le calcul sur l'année.

Avec une manuelle, tu rachètes l'objet entier 4 fois par an. Manche compris, alors que seule la tête est usée.

Avec la Pulse Care Bamboo+, tu gardes le manche pendant des années. Tu ne remplaces que la tête en bambou : 14,90 € le pack de 4, soit un an de brossage.

La brosse : 59,90 €, avec 2 têtes, l'étui et le câble.
Livraison gratuite en point relais dès 20 € d'achat.

[CTA]

#brosseadentselectrique #brosseadentsbambou #tetederechange #pulsecare"""),

# ── 2 · ANGLE : le scepticisme avant achat
dict(date="x", kind="carousel", slides=[
  dict(tpl="fear", kicker="Ta crainte", fear="Une marque que je connais pas, à 59,90 €, je le sens moyen.", kicker2="Ce qu'on a mis en face", answer="*30 jours* pour changer d'avis", sub="« J'étais sceptique au début » est l'avis le plus fréquent qu'on reçoit. La suite est toujours la même.", swipe=True),
  dict(tpl="mosaic", kicker="Ce qui arrive chez toi", title="Pour 59,90 €", imgs=[(s("bamboo_face"), "Le manche sonique"), (s("ricin_pack2"), "2 têtes en bambou"), (s("etui_voyage"), "L'étui de voyage"), (s("chargeur"), "Le câble USB-C")]),
  dict(tpl="offer", img=s("p014"), kicker="Sans risque", title="30 jours *pour changer d'avis*", price="59,90 €", perks=[RET, LIV, "Avis publics sur la fiche"]),
],
caption="""« J'étais sceptique au début. » C'est ce qu'on lit le plus souvent dans les avis sur notre brosse à dents électrique.

Normal. 59,90 €, une marque que tu ne connais pas, et une tête en bambou : ça interroge.

Ce qui revient juste après, dans les mêmes avis : la qualité de la matière, la prise en main, l'autonomie, le design.

Pour décider sans te tromper :
→ 2 têtes, l'étui de voyage et le câble sont inclus
→ 30 jours pour changer d'avis
→ les avis clients sont publics sur la fiche produit

[CTA]

""" + TAGS),

# ── 3 · ANGLE : le design sur le lavabo
dict(date="x", kind="photo", slides=[
  dict(tpl="editorial", img=s("p084"), over="Sur le lavabo", kicker="Design", title="Mieux qu'un *bloc de plastique blanc*", sub="Bambou, lignes sobres, pas de socle branché en permanence. C'est le compliment n°1 dans les avis."),
],
caption="""Le compliment qui revient le plus sur notre brosse à dents électrique ? Pas la puissance. Le design.

« Elle est stylée », « ça change du design de celle en plastique », « le design naturel en bambou » : ce sont des avis clients, mot pour mot.

La Bamboo+ reste posée sur le lavabo toute la journée. Autant qu'elle soit belle.

→ manche sobre, finition bambou
→ pas de socle encombrant, recharge USB-C une fois par mois
→ 59,90 € avec 2 têtes, l'étui et le câble

[CTA]

#brosseadentselectrique #brosseadentsbambou #salledebain #pulsecare"""),

# ── 4 · ANGLE : les gencives sensibles
dict(date="x", kind="carousel", slides=[
  dict(tpl="fear", kicker="Ta crainte", fear="Mes gencives saignent déjà, une électrique va empirer ça.", kicker2="Ce qui change", answer="C'est la *pression* qui blesse, pas les vibrations", sub="Mode Sensible, poils ricin, et aucune force à appliquer : tu guides, la brosse travaille.", swipe=True),
  dict(tpl="steps", kicker="Ce qui change", title="Deux réglages, une tête", items=[("Mode Sensible", "Vibrations adoucies, dès le premier jour."), ("Zéro pression à appliquer", "Les vibrations nettoient, tu guides."), ("Poils ricin", "Fibre végétale, toucher très doux.")]),
  dict(tpl="arch", img=s("ricin_profil"), kicker="Têtes poils ricin", title="La plus douce *de la gamme*", sub=LIV, price="5,50 €"),
],
caption="""Si tu évites certaines zones en te brossant, c'est que quelque chose ne va pas. Et une brosse à dents électrique mal réglée peut aggraver les choses.

Sur la Bamboo+ :
→ le mode Sensible adoucit les vibrations
→ tu n'as aucune pression à appliquer, ce sont les vibrations qui nettoient
→ les têtes à poils de ricin ont le toucher le plus doux de la gamme

Si les saignements durent plus d'une semaine, parles-en à ton dentiste. Une brosse ne remplace pas un avis pro.

Tête poils ricin : 5,50 €. Pack de 4 : 14,90 €.

[CTA]

#brosseadentselectrique #gencivessensibles #poilsricin #pulsecare"""),

# ── 5 · ANGLE : la bagarre du brossage avec les enfants
dict(date="x", kind="carousel", slides=[
  dict(tpl="editorial", img="u:1758687126877-b37052a20a4d", over="Le soir, 20h40", kicker="Parents", title="« Encore 30 secondes ! » *tous les soirs*", sub="Le minuteur vibre toutes les 30 secondes. L'enfant change de zone tout seul, tu arrêtes de compter à voix haute.", swipe=True),
  dict(tpl="schema", kind="zones", kicker="Ce qui débloque", title="4 zones, *30 secondes chacune*", sub="Le minuteur décide à ta place. Plus de négociation."),
  dict(tpl="split", img=s("p092"), kicker="Pack duo", title="Une brosse chacun, *une seule routine*", items=["Deux manches, deux étuis", "Minuteur sur les deux", "Têtes interchangeables"], price="94,90 €", sub=LIV, dark=True),
],
caption="""Le brossage du soir avec les enfants, c'est souvent une négociation. Une brosse à dents électrique règle une partie du problème.

Le minuteur tourne, il s'arrête seul à 2 minutes, avec une pause toutes les 30 secondes pour changer de zone. Ce n'est plus toi qui décides quand c'est fini : c'est la brosse.

Et les enfants copient ce qu'ils voient. Quand les parents se brossent en même temps, la routine tient toute seule.

Pack duo : 94,90 € les deux brosses.

Pour les plus jeunes, demande à ton dentiste le modèle adapté à leur âge.

[CTA]

#brosseadentselectrique #parents #routinefamille #pulsecare"""),

# ── 6 · ANGLE : après le rendez-vous chez le dentiste
dict(date="x", kind="photo", slides=[
  dict(tpl="fear", kicker="Chez le dentiste", fear="Il faudrait mieux brosser. D'accord, mais comment ?", kicker2="Ce qui s'en charge", answer="La *technique*, c'est la brosse qui l'applique", sub="41 000 vibrations par minute, un minuteur qui découpe les 4 zones, un mode Sensible. Toi, tu guides."),
],
caption="""Ton dentiste t'a dit de mieux brosser. Une brosse à dents électrique sonique fait une bonne partie du travail à ta place.

Le problème d'une brosse manuelle, ce n'est pas l'outil. C'est que la technique parfaite, personne ne la tient 2 minutes, 2 fois par jour, pendant des années.

Avec la Bamboo+ :
→ 41 000 vibrations par minute, tu guides seulement
→ minuteur 2 minutes, pause toutes les 30 s par zone
→ mode Sensible si les gencives sont fragiles

59,90 € avec 2 têtes en bambou, l'étui et le câble USB-C.

[CTA]

#brosseadentselectrique #detartrage #conseilsdentaires #pulsecare"""),

# ── 7 · ANGLE : voyage
dict(date="x", kind="carousel", slides=[
  dict(tpl="bignum", kicker="Avis client", big="30 j", title="« emmenée en voyage *sans même recharger* »", sub="Un avis publié sur la fiche produit. L'autonomie est l'argument n°2 après le design.", swipe=True),
  dict(tpl="mosaic", kicker="Dans la trousse", title="Ce que tu emportes", imgs=[(s("etui_plat"), "L'étui en bambou"), (s("p085"), "Le manche"), (s("nylon_gauche"), "Une tête d'avance")]),
  dict(tpl="offer", img=s("boite_bambou"), kicker="Inclus dans la boîte", title="L'étui de voyage, *sans supplément*", price="59,90 €", perks=["Étui en bambou", "30 jours d'autonomie", LIV]),
],
caption="""« Je l'ai emmenée en voyage sans même recharger. » C'est un avis client sur notre brosse à dents électrique, et c'est exactement l'idée.

30 jours d'autonomie pour 2 brossages par jour. Sur un week-end, une semaine, ou trois, tu ne touches pas au chargeur.

Et l'étui de voyage en bambou est inclus dans la boîte, pas vendu à part.

→ recharge en USB-C, le câble du téléphone suffit
→ étanche IPX7, la douche d'hôtel ne pose aucun problème

59,90 €, livraison gratuite en point relais dès 20 € d'achat.

[CTA]

#brosseadentselectrique #voyage #autonomie #pulsecare"""),

# ── 8 · ANGLE : l'oubli de racheter les têtes
dict(date="x", kind="carousel", slides=[
  dict(tpl="quiz", kicker="Sois honnête", title="Ta tête de brosse, *elle a quel âge* ?", options=["Moins de 3 mois", "Entre 3 et 6 mois", "Plus de 6 mois", "Aucune idée"], swipe=True),
  dict(tpl="schema", kind="calendar", kicker="Le rythme", title="4 changements *par an*", sub="Une tête tous les 3 mois. C'est la seule règle."),
  dict(tpl="arch", img=s("nylon_pack4_noir"), kicker="Abonnement Pulse Care", title="Livrées *sans y penser*", sub="Tu choisis le rythme. Sans engagement, arrêt depuis ton compte.", price="14,90 €"),
],
caption="""Ta tête de brosse à dents électrique a quel âge ? Si la réponse est « aucune idée », elle est trop vieille.

Au-delà de 3 mois, les poils s'écartent et retirent moins bien la plaque. Même quand la tête a l'air propre.

Le problème n'est pas le prix. C'est qu'on y pense jamais au bon moment.

L'abonnement Pulse Care règle ça :
→ tu choisis tes têtes, ricin ou nylon
→ tu choisis le rythme : tous les 1, 2 ou 3 mois
→ sans engagement, tu arrêtes quand tu veux depuis ton compte

Pack de 4 : 14,90 €.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

# ── 9 · ANGLE : le café et les taches
dict(date="x", kind="photo", slides=[
  dict(tpl="editorial", img="u:1652594286350-47f2213f5c92", over="3 cafés par jour", kicker="Taches de surface", title="Le café *se voit sur l'émail*", sub="Le mode Blanchiment travaille les taches de surface : café, thé, vin. Pas un blanchiment chimique, un polissage quotidien."),
],
caption="""Le café laisse des taches sur l'émail. Une brosse à dents électrique ne les efface pas d'un coup, mais elle évite qu'elles s'installent.

Le mode Blanchiment de la Bamboo+ accélère les vibrations pour décrocher les pigments de surface : café, thé, vin rouge.

Ce qu'il ne fait pas : changer la teinte naturelle de ta dent. Ça, c'est le travail du dentiste, avec un vrai protocole.

Le réflexe qui aide : un verre d'eau après le café, pour ne pas laisser le pigment poser.

4 modes sur la Bamboo+, 59,90 €.

[CTA]

#brosseadentselectrique #blanchiment #cafe #pulsecare"""),

# ── 10 · ANGLE : idée cadeau, petit budget
dict(date="x", kind="carousel", slides=[
  dict(tpl="split", img="u:1512909006721-3d6018887383", kicker="Idée cadeau", title="Utilisé *deux fois par jour*", items=["Pas un gadget qu'on range", "Un seul bouton, 4 modes", "L'étui dans la boîte"], price="59,90 €", sub="Livraison gratuite en point relais dès 20 € d'achat.", dark=True, swipe=True),
  dict(tpl="mosaic", kicker="Trois budgets", title="Pour qui, à quel prix", imgs=[(s("ricin_pack4_douce"), "Pack de 4 têtes · 14,90 €"), (s("decouverte_neutre"), "Pack découverte · 64,90 €"), (s("duo_coffret"), "Pack duo · 94,90 €")]),
  dict(tpl="statement", img="u:1545608444-f045a6db6133", kicker="L'argument", title="Il ne finira pas *au fond d'un tiroir.*", sub=LIV),
],
caption="""Une brosse à dents électrique en cadeau, c'est l'idée qu'on trouve bête jusqu'à ce qu'on y réfléchisse.

C'est un objet utilisé deux fois par jour, tous les jours, pendant des années. Peu de cadeaux à moins de 100 € peuvent en dire autant.

Trois budgets :
→ pack de 4 têtes en bambou : 14,90 €
→ pack découverte : 64,90 €
→ pack duo, deux brosses : 94,90 €

Livraison gratuite en point relais dès 20 € d'achat.

Tu offres à qui cette année ?

[CTA]

#brosseadentselectrique #ideecadeau #cadeaunoel #pulsecare"""),

# ── 11 · ANGLE : manuelle vs électrique
dict(date="x", kind="carousel", slides=[
  dict(tpl="hero", img="u:1676897288522-e8a081e71430", kicker="Le match", title="Manuelle ou *électrique* ?", swipe=True),
  dict(tpl="versus", kicker="Ce qui change au quotidien", title="Lequel est *fait pour toi* ?", left=("Brosse manuelle", ["Technique à soigner", "Pas de minuteur", "Tout part à la poubelle"]), right=("Pulse Care", ["Les vibrations nettoient", "Minuteur 2 min intégré", "Seule la tête se change"])),
  dict(tpl="split", img="u:1552650272-b8a34e21bc4b", side="right", kicker="Bamboo+", title="Prête à passer *à l'électrique* ?", items=["41 000 vibrations par minute", "Minuteur 2 min intégré", "2 têtes en bambou incluses"], price="59,90 €", sub=RET),
],
caption="""Brosse à dents électrique ou manuelle : la vraie différence n'est pas la puissance, c'est la régularité.

La manuelle fait le travail si ta technique est parfaite : bon angle, bon mouvement, 2 minutes pile, deux fois par jour. Dans la vraie vie, ça n'arrive pas.

La sonique corrige ça :
→ 41 000 vibrations par minute, tu n'as qu'à guider
→ minuteur intégré, plus de brossage bâclé
→ un mode Sensible pour les gencives fragiles

59,90 € avec 2 têtes, l'étui et le câble. 30 jours pour changer d'avis.

[CTA]

#brosseadentselectrique #brosseadentssonique #hygienebuccodentaire #pulsecare"""),

# ── 12 · ANGLE : le plastique qu'on jette
dict(date="x", kind="photo", slides=[
  dict(tpl="callout", img=s("p087"), kicker="Le principe", notes=[("Le manche : gardé des années", 0.5, 0.62), ("La tête : changée tous les 3 mois", 0.5, 0.12)], strike=("toute la brosse", "la tête"), title="Un seul manche, *une tête à changer*", sub="C'est la seule pièce qui part à la poubelle, et elle est en bambou.", cta="Voir la recharge"),
],
caption="""La partie d'une brosse à dents électrique qu'on jette le plus souvent, c'est la tête. C'est là que Pulse Care a mis le bambou.

→ la tête, remplacée tous les 3 mois, est en bambou
→ les poils sont à base d'huile de ricin, une fibre d'origine végétale
→ le manche est en plastique ASA, choisi pour durer des années

Tu ne rachètes pas l'objet entier à chaque fois. Juste la tête.

Pack de 4 têtes : 14,90 €. La brosse : 59,90 €.

[CTA]

#brosseadentselectrique #brosseadentsbambou #poilsricin #pulsecare"""),

# ── 13 · ANGLE : le pack découverte pour tester
dict(date="x", kind="carousel", slides=[
  dict(tpl="editorial", img=s("decouverte_main"), over="Le point de départ", kicker="Pack découverte", title="Tester *avant de t'engager*", sub="Le manche, les têtes, l'étui. Tout ce qu'il faut pour démarrer, et 30 jours pour changer d'avis.", swipe=True),
  dict(tpl="mosaic", kicker="Dans le pack", title="Tout pour démarrer", imgs=[(s("decouverte_contenu"), "Le manche"), (s("decouverte_tetes"), "Les têtes ricin"), (s("dec_etui_tetes"), "L'étui")]),
  dict(tpl="offer", img=s("p046"), kicker="Pack découverte", title="Le point de départ", price="64,90 €", perks=["Le manche sonique", "Têtes poils ricin", "L'étui de voyage"]),
],
caption="""Passer à la brosse à dents électrique sans se tromper : c'est à ça que sert le pack découverte Pulse Care.

Dedans : le manche sonique, des têtes en bambou à poils de ricin et l'étui de voyage. De quoi tenir plusieurs mois sans rien racheter.

→ 64,90 €
→ 30 jours pour changer d'avis
→ livraison gratuite en point relais dès 20 € d'achat

C'est aussi le pack à offrir à quelqu'un qui hésite depuis des mois.

[CTA]

#brosseadentselectrique #packdecouverte #brosseadentsbambou #pulsecare"""),

# ── 14 · ANGLE : deux personnes, un lavabo
dict(date="x", kind="carousel", slides=[
  dict(tpl="callout", img=s("p121"), kicker="Pack duo", notes=[("Deux manches, deux couleurs", 0.5, 0.22), ("Têtes interchangeables", 0.5, 0.72)], title="Deux brosses, *un seul lavabo*", sub="Chacun la sienne, et les têtes se changent sur n'importe quel manche.", cta="Voir le duo", swipe=True),
  dict(tpl="mosaic", kicker="Dans le coffret", title="Chacun la sienne", imgs=[(s("duo_etuis"), "2 manches"), (s("duo_acc"), "Les accessoires"), (s("deux_brosses"), "2 étuis")]),
  dict(tpl="ticket", kicker="Pack duo", title="Le détail, *ligne par ligne*", head="Pulse Care · pack duo", lines=[("2 manches sonique", "—"), ("4 têtes en bambou", "incluses"), ("2 étuis de voyage", "inclus"), ("Câble USB-C", "inclus")], total=("À payer", "94,90 €"), note="Soit 47,45 € la brosse. " + LIV),
],
caption="""Deux brosses à dents électriques pour la maison : le pack duo Pulse Care.

Pour le couple, les colocs, ou toi et ton ado. Chacun son manche, chacun ses têtes en bambou.

94,90 € les deux, soit 47,45 € la brosse. Contre 59,90 € à l'unité.

Chaque brosse arrive avec ses têtes et son étui de voyage.

Identifie la personne avec qui tu partages ton lavabo.

[CTA]

#brosseadentselectrique #packduo #brosseadentsbambou #pulsecare"""),

# ── 15 · ANGLE : ce que disent les clients
dict(date="x", kind="carousel", slides=[
  dict(tpl="note", img=s("p055"), kicker="Ce qu'on imagine", bad="Le minuteur, c'est un gadget.", hand="les clients disent :", good="« Le minuteur est *hyper pratique.* »", sub="C'est la fonction qui revient le plus dans les avis, devant l'autonomie.", swipe=True),
  dict(tpl="statement", img=s("p021"), kicker="Avis clients", title="« Elle est stylée, légère *et tient hyper bien la charge.* »"),
  dict(tpl="offer", img="u:1595428774752-c87f23e7fcee", kicker="Avis vérifiés", title="Lis-les *avant d'acheter*", price="59,90 €", perks=["Avis publics", "Critiques comprises", RET]),
],
caption="""Ce que les clients disent de la brosse à dents électrique Pulse Care, dans leurs mots.

« Le minuteur est hyper pratique. »
« Elle est stylée, légère et tient hyper bien la charge. »
« J'étais sceptique au début, mais après quelques semaines je suis convaincu. »

Les avis sont publics et vérifiés sur la fiche produit. Y compris les critiques : un client trouve le manche un peu épais au début.

On préfère que tu les lises avant d'acheter.

[CTA]

""" + TAGS),

# ── 16 · ANGLE : le prix d'entrée
dict(date="x", kind="photo", slides=[
  dict(tpl="stats", img=s("duo_tete"), title="59,90 €. *On détaille.*", items=[("41 000", "vibrations par minute"), ("4", "modes de brossage"), ("30 j", "d'autonomie, USB-C"), ("2", "têtes en bambou incluses")]),
],
caption="""59,90 € pour une brosse à dents électrique sonique : voilà exactement ce que ça comprend.

→ 41 000 vibrations par minute
→ 4 modes : Sensible, Nettoyage, Blanchiment, Polissage
→ minuteur 2 min, pause toutes les 30 s
→ jusqu'à 30 jours d'autonomie, recharge USB-C
→ étanche IPX7
→ 2 têtes en bambou, l'étui de voyage et le câble inclus

Pas d'accessoire à racheter avant 6 mois. Et 30 jours pour changer d'avis.

[CTA]

""" + TAGS),

# ── 17 · ANGLE : haleine du matin
dict(date="x", kind="carousel", slides=[
  dict(tpl="editorial", img="u:1611695434369-a8f5d76ceb7b", over="Au réveil", kicker="Haleine", title="Le brossage du soir *décide de ton réveil*", sub="La nuit, la salive baisse et les bactéries travaillent sans frein. Ce que tu laisses le soir, tu le retrouves le matin.", swipe=True),
  dict(tpl="steps", kicker="Le soir", title="L'ordre qui marche", items=[("Fil dentaire", "Ou brossettes entre les dents."), ("2 minutes, mode Nettoyage", "Le minuteur gère le temps."), ("La langue", "3 passages doux, de l'arrière vers l'avant."), ("Plus rien à manger", "Jusqu'au lendemain.")]),
  dict(tpl="arch", img="u:1564540579594-0930edb6de43", kicker="Pulse Care Bamboo+", title="Le minuteur fait *le travail ingrat*", sub=LIV, price="59,90 €"),
],
caption="""L'haleine du matin se joue la veille au soir. Une brosse à dents électrique aide, à condition de suivre l'ordre.

La nuit, tu produis moins de salive. Ce que tu laisses le soir reste 8 heures en place.

L'ordre qui marche :
→ fil dentaire ou brossettes
→ 2 minutes de brossage, mode Nettoyage
→ 3 passages doux sur la langue, c'est là que vivent beaucoup de bactéries
→ plus rien à manger après

Le minuteur de la Bamboo+ s'occupe du temps. Toi, tu suis l'ordre.

[CTA]

#brosseadentselectrique #haleinefraiche #routinedusoir #pulsecare"""),

# ── 18 · ANGLE : ricin ou nylon, aider à choisir
dict(date="x", kind="carousel", slides=[
  dict(tpl="product", img=s("ricin_fibres"), kicker="Avant d'acheter", title="Poils *ricin* ou poils *nylon* ?", swipe=True),
  dict(tpl="versus", kicker="Têtes Pulse Care", title="Lequel est *fait pour toi* ?", both_good=True, left=("Poils nylon", ["Brossage plus ferme", "Tu sens bien le nettoyage", "Tête en bambou"]), right=("Poils ricin", ["Fibre d'origine végétale", "Toucher très doux", "Idéal gencives sensibles"])),
  dict(tpl="split", img=s("nylon_pack4"), kicker="Pack de 4", title="Un an de *brossage*", items=["3,73 € la tête", "Ricin ou nylon, au choix", "Une tête tous les 3 mois"], price="14,90 €", sub=LIV),
],
caption="""Têtes de brosse à dents électrique : ricin ou nylon ? La question qu'on nous pose le plus avant l'achat.

Les deux sont montées sur une tête en bambou et se clipsent en une seconde. La différence tient à la fibre.

→ Ricin : fibre d'origine végétale, toucher très doux. Le bon choix si tes gencives sont sensibles.
→ Nylon : brossage plus ferme, pour ceux qui aiment sentir le nettoyage.

Pas sûr ? Prends une tête de chaque à 5,50 € et compare sur deux semaines.

Pack de 4 : 14,90 €.

[CTA]

#brosseadentselectrique #tetederechange #poilsricin #pulsecare"""),

# ── 19 · ANGLE : la douche
dict(date="x", kind="photo", slides=[
  dict(tpl="fear", kicker="Ta crainte", fear="Si je la prends sous la douche, je vais la griller.", kicker2="Ce qu'elle supporte", answer="Étanche *IPX7*", sub="Elle encaisse l'eau de la douche sans broncher. Sèche juste le port USB-C avant de la recharger."),
],
caption="""Se brosser les dents sous la douche : une brosse à dents électrique le supporte, à condition d'être étanche.

La Bamboo+ est certifiée IPX7. Concrètement :
→ elle résiste à l'immersion
→ tu la rinces sous le robinet sans stress
→ les éclaboussures du lavabo ne posent aucun problème

Le seul réflexe à garder : bien sécher le port USB-C avant de la brancher.

59,90 €, livraison gratuite en point relais dès 20 € d'achat.

[CTA]

#brosseadentselectrique #ipx7 #brosseadentsbambou #pulsecare"""),

# ── 20 · ANGLE : la panne de l'ancienne brosse
dict(date="x", kind="carousel", slides=[
  dict(tpl="note", img=s("p095"), kicker="Le moment du changement", bad="Elle tient encore, je la garde.", hand="le vrai signe :", good="Si tu la recharges *toutes les semaines*, elle est finie.", sub="Une batterie en fin de vie perd d'abord son autonomie, puis sa puissance de brossage.", swipe=True),
  dict(tpl="bignum", kicker="Batterie", big="500", title="mAh, *30 jours d'autonomie*", sub="Une charge d'environ 2,5 h, en USB-C."),
  dict(tpl="offer", img="u:1667550177726-96da7c257853", kicker="Bamboo+", title="Le câble que *tu as déjà*", price="59,90 €", perks=["Recharge USB-C", "2,5 h de charge", "30 jours d'autonomie"]),
],
caption="""Une brosse à dents électrique qui ne tient plus la charge, c'est le signe qu'il est temps de changer.

Sur la Bamboo+ :
→ batterie lithium 500 mAh
→ jusqu'à 30 jours d'autonomie pour 2 brossages par jour
→ recharge complète en 2,5 h environ
→ en USB-C, le même câble que ton téléphone

Pas de socle propriétaire à garder branché sur le lavabo.

59,90 € avec 2 têtes, l'étui et le câble. 30 jours pour changer d'avis.

[CTA]

#brosseadentselectrique #usbc #autonomie #pulsecare"""),

# ── 21 · ANGLE : le tartre revient vite
dict(date="x", kind="carousel", slides=[
  dict(tpl="schema", kind="plaque", kicker="Pourquoi ça revient", title="De la plaque *au tartre*", swipe=True),
  dict(tpl="steps", kicker="La fenêtre", title="Tu as 24 à 72 heures", items=[("Avant : c'est souple", "Le brossage l'enlève."), ("Après : c'est du tartre", "Plus aucune brosse ne le retire."), ("Ensuite : détartrage", "Chez le dentiste, selon son avis.")]),
  dict(tpl="arch", img=s("p097"), kicker="2 minutes, 2 fois par jour", title="Le minuteur *s'en charge*", sub=LIV, price="59,90 €"),
],
caption="""Un détartrage à peine fait et le tartre revient ? Le problème se joue dans les 72 heures, et une brosse à dents électrique change la donne.

La plaque se dépose en permanence. Souple, elle part au brossage. Mais elle se minéralise en 24 à 72 heures. Là, c'est du tartre : dur, collé, impossible à retirer avec une brosse.

Tout se joue donc sur la régularité, pas sur la force.

→ minuteur 2 minutes, pause toutes les 30 s
→ 41 000 vibrations par minute
→ mode Sensible pour la ligne des gencives

[CTA]

#brosseadentselectrique #tartre #plaquedentaire #pulsecare"""),

# ── 22 · ANGLE : offrir à ses parents
dict(date="x", kind="photo", slides=[
  dict(tpl="split", img="u:1627130595904-ebeeb6540a93", side="right", kicker="Idée cadeau", title="Le cadeau qui *fait vraiment plaisir*", items=["Un seul bouton", "L'étui pour les déplacements", "Deux têtes dans la boîte"], price="59,90 €", sub=LIV, dark=True),
],
caption="""Offrir une brosse à dents électrique à ses parents, c'est un cadeau utile qu'ils n'achèteront jamais pour eux.

Pourquoi la Bamboo+ fonctionne bien pour eux :
→ un seul bouton pour changer de mode
→ le mode Sensible pour les gencives qui ont vécu
→ 30 jours d'autonomie, donc une seule recharge par mois
→ l'étui de voyage inclus

59,90 € avec 2 têtes en bambou, l'étui et le câble USB-C.

Livraison gratuite en point relais dès 20 € d'achat.

[CTA]

#brosseadentselectrique #ideecadeau #parents #pulsecare"""),

# ── 23 · ANGLE : combien ça coûte par an
dict(date="x", kind="carousel", slides=[
  dict(tpl="bignum", kicker="Le budget", big="14,90 €", title="par an, *après la première année*", sub="Un pack de 4 têtes, c'est un an de brossage.", swipe=True),
  dict(tpl="stats", img=s("ricin_arriere"), title="Le détail", items=[("59,90 €", "la brosse, avec 2 têtes"), ("14,90 €", "le pack de 4 têtes"), ("4", "têtes par an, une tous les 3 mois"), ("1", "manche, gardé des années")]),
],
caption="""Une brosse à dents électrique, ça coûte combien par an ? Le calcul, sans arrondi.

Première année : 59,90 € pour la brosse, avec 2 têtes, l'étui et le câble. Ces 2 têtes tiennent environ 6 mois, donc un seul pack à ajouter.

Années suivantes : 14,90 €. C'est le prix d'un pack de 4 têtes, soit un an de brossage.

Le manche, lui, se garde. C'est tout le principe.

[CTA]

#brosseadentselectrique #budget #tetederechange #pulsecare"""),

# ── 24 · ANGLE : les 4 modes, aider à choisir
dict(date="x", kind="photo", slides=[
  dict(tpl="mosaic", kicker="Le réglage unique", title="Tes dents n'ont pas *le même besoin* chaque jour", sub="Gencives sensibles le matin, taches de café le soir. Un bouton pour passer de l'un à l'autre.", imgs=[(s("modes_main"), "Sensible"), (s("icones"), "Nettoyage"), (s("p019"), "Blanchiment"), ("u:1542013936693-884638332954", "Polissage")]),
],
caption="""4 modes sur une brosse à dents électrique, ça sert à quoi exactement ?

→ Sensible : vibrations adoucies, pour les gencives qui saignent ou les dents réactives
→ Nettoyage : le mode de tous les jours, matin et soir
→ Blanchiment : aide à retirer les taches de surface (café, thé, vin)
→ Polissage : la sensation de dents lisses en fin de brossage

Un seul bouton pour passer de l'un à l'autre. Si tu viens du manuel, reste 1 à 2 semaines en mode Sensible.

Bamboo+ : 59,90 €.

[CTA]

#brosseadentselectrique #modesdebrossage #brosseadentssonique #pulsecare"""),

# ── 25 · ANGLE : le fil dentaire qu'on zappe
dict(date="x", kind="carousel", slides=[
  dict(tpl="bignum", kicker="Entre les dents", big="40 %", title="des surfaces *qu'aucune brosse n'atteint*", sub="C'est là que commencent la plupart des caries entre deux dents.", swipe=True),
  dict(tpl="versus", kicker="Comment choisir", title="Fil *ou brossettes* ?", both_good=True, left=("Le fil", ["Pour les espaces serrés", "Une fois par jour, le soir", "Très peu cher"]), right=("Les brossettes", ["Pour les espaces plus larges", "Plus rapides à passer", "Taille donnée par ton dentiste"])),
  dict(tpl="arch", img=s("p056"), kicker="Les 60 % restants", title="C'est le travail *de ta brosse*", sub=LIV, price="59,90 €"),
],
caption="""Même la meilleure brosse à dents électrique ne nettoie qu'environ 60 % de la surface des dents. Les 40 % restants sont entre les dents.

D'où le fil ou les brossettes, une fois par jour, le soir de préférence.

→ Fil : pour les espaces serrés, très peu cher
→ Brossettes : pour les espaces plus larges, plus rapides. Demande la taille à ton dentiste

Pour les 60 % restants, la Bamboo+ fait le travail : 41 000 vibrations par minute et un minuteur de 2 minutes.

[CTA]

#brosseadentselectrique #fildentaire #brossettes #pulsecare"""),

# ── 26 · ANGLE : le doute sur la compatibilité
dict(date="x", kind="photo", slides=[
  dict(tpl="product", img=s("nylon_pack2"), kicker="La question qu'on reçoit le plus", title="Compatible avec *d'autres manches* ?", sub="Non. Les têtes Pulse Care sont conçues uniquement pour les manches Pulse Care.", price="14,90 €"),
],
caption="""La question qu'on reçoit le plus souvent sur nos têtes de brosse à dents électrique : sont-elles compatibles avec d'autres manches ?

Non. Elles sont conçues uniquement pour les manches Pulse Care. Le clip et le moteur sont dimensionnés ensemble, et une tête mal ajustée perd en efficacité.

Ce que tu as à la place :
→ têtes en bambou, poils ricin ou nylon
→ clip en une seconde, sans vis ni sens à chercher
→ 5,50 € l'unité, 14,90 € le pack de 4

[CTA]

#brosseadentselectrique #tetederechange #faq #pulsecare"""),

# ── 27 · ANGLE : la régularité plutôt que le matériel
dict(date="x", kind="photo", slides=[
  dict(tpl="tracker", kicker="Le défi", title="7 jours, *2 brossages par jour*", sub="Capture ce post et coche tes cases chaque soir.", rows=["Matin", "Soir"], done=3),
],
caption="""Un sourire en bonne santé ne dépend pas du prix de ta brosse à dents électrique. Il dépend de la régularité.

Matin et soir. 2 minutes. Tous les jours. C'est tout.

Le matériel ne fait qu'une chose : t'aider à tenir le rythme. Le minuteur s'arrête seul, tu n'as plus à compter ni à estimer.

Le défi : capture ce post, coche une case matin et soir pendant 7 jours. Au bout d'une semaine, l'habitude tient toute seule.

Tu relèves ?

[CTA]

#brosseadentselectrique #defi7jours #routinedentaire #pulsecare"""),

# ── 28 · ANGLE : la livraison et la garantie
dict(date="x", kind="carousel", slides=[
  dict(tpl="split", img=s("p029"), side="right", kicker="Le moment où on hésite", title="Panier rempli, *doigt en l'air*", items=["Livraison gratuite dès 20 €", "30 jours pour changer d'avis", "Suivi par e-mail à chaque étape"], swipe=True),
  dict(tpl="steps", kicker="Les 3 points", title="Simple et sans piège", items=[("Livraison gratuite", "En point relais, dès 20 € d'achat."), ("30 jours pour changer d'avis", "Hors têtes déjà ouvertes, pour raison d'hygiène."), ("Une question ?", "Par mail, réponse sous 24 à 48 h.")]),
],
caption="""Commander une brosse à dents électrique chez Pulse Care : les 3 choses à savoir avant de cliquer.

→ Livraison gratuite en point relais dès 20 € d'achat
→ 30 jours pour changer d'avis, au-delà des 14 jours légaux
→ Exception : les têtes de recharge déjà ouvertes ne sont pas reprises, pour raison d'hygiène

Une question avant d'acheter ? Écris-nous, on répond sous 24 à 48 h.

[CTA]

""" + TAGS),

# ── 29 · ANGLE : le récap, dernier appel
dict(date="x", kind="carousel", slides=[
  dict(tpl="editorial", img=s("p004"), over="Le récap", kicker="Bamboo+", title="Pourquoi *celle-là* ?", sub="Un mois d'arguments, remis dans l'ordre : ce qu'elle fait, ce qu'elle coûte, ce qu'elle ne promet pas.", swipe=True),
  dict(tpl="stats", img=s("etui"), title="En résumé", items=[("41 000", "vibrations par minute"), ("4", "modes de brossage"), ("2 min", "de minuteur intégré"), ("30 j", "d'autonomie")]),
  dict(tpl="steps", kicker="Et le reste", title="Ce que tu ne paies qu'une fois", items=[("Le manche", "Gardé pendant des années."), ("L'étui de voyage", "En bambou, inclus."), ("Le câble USB-C", "Inclus aussi.")]),
  dict(tpl="ticket", kicker="Récapitulatif", title="Ce que tu reçois *pour 59,90 €*", head="Pulse Care · Bamboo+", lines=[("Manche sonique bambou", "—"), ("2 têtes en bambou", "incluses"), ("Étui de voyage", "inclus"), ("Câble USB-C", "inclus")], total=("À payer", "59,90 €"), note=LIV + " " + RET),
],
caption="""Pourquoi choisir la brosse à dents électrique Pulse Care Bamboo+ ? Le récap complet, pour décider.

→ 41 000 vibrations par minute, technologie sonique
→ 4 modes : Sensible, Nettoyage, Blanchiment, Polissage
→ minuteur 2 min, pause toutes les 30 s
→ 30 jours d'autonomie, recharge USB-C
→ étanche IPX7
→ têtes en bambou, poils ricin ou nylon

Tout est dans la boîte : 2 têtes, l'étui de voyage et le câble. 59,90 €.

Livraison gratuite en point relais dès 20 € d'achat. 30 jours pour changer d'avis.

[CTA]

""" + TAGS),
]
