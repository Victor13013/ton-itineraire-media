# -*- coding: utf-8 -*-
"""Pulse Care — plan de test des axes marketing (nov.-déc. 2026).

Chaque axe = une hypothèse sur ce qui fait acheter. Chaque axe est décliné dans les trois
formats : post simple (18h), carrousel (18h) et vidéo avec voix off (créneau vidéo).
On compare ensuite les axes entre eux sur les mêmes indicateurs (portée, enregistrements,
partages, visites du profil, clics).

Voix off : ElevenLabs. Le nom de la marque est écrit « Poulsse Kèr » dans le texte lu,
pour que la voix le prononce comme Victor le veut ; l'écran garde l'orthographe Pulse Care.
Les fichiers audio sont téléchargés par GitHub Actions dans media/vo/<id>.mp3 (render/vo.json).
"""
from content import s, LIV, RET

AXES = {
    "ECO":       "Économie : le coût caché des têtes de rechange",
    "PREUVE":    "Efficacité prouvée : la science plutôt que la promesse",
    "PEUR":      "Peur d'abîmer : gencives sensibles, eau, panne",
    "PARENTS":   "Parents : la bagarre du brossage des enfants",
    "DESIGN":    "Design : l'objet sur le lavabo",
    "GASPI":     "Anti-gaspillage : on ne jette que la tête",
    "CONFIANCE": "Confiance : acheter à une marque qu'on ne connaît pas",
    "CADEAU":    "Cadeau : l'objet utile qui ne finit pas au tiroir",
    "PRATIQUE":  "Pratique : voyage, autonomie, compatibilité",
    "RESULTAT":  "Résultat visible : haleine, taches, tartre",
}

# Axe de chacun des 33 posts du soir, dans l'ordre de content.POSTS
AXIS_18H = ["ECO", "PREUVE", "GASPI", "CONFIANCE", "ECO", "CONFIANCE", "DESIGN", "PEUR", "PARENTS",
            "PREUVE", "PRATIQUE", "PRATIQUE", "RESULTAT", "CADEAU", "PREUVE", "GASPI", "CONFIANCE",
            "PARENTS", "CONFIANCE", "ECO", "RESULTAT", "PRATIQUE", "PEUR", "PRATIQUE", "RESULTAT",
            "CADEAU", "ECO", "RESULTAT", "PREUVE", "PRATIQUE", "PREUVE", "CONFIANCE", "RECAP"]

TAGS_T = "#brosseadentselectrique #hygienebuccodentaire #pulsecare"

# Trois posts ajoutés pour que chaque axe existe en post simple ET en carrousel.
# (position d'insertion dans la file du soir, post)
NEW_18H = [
    (9, dict(date="x", kind="photo", axis="CONFIANCE", slides=[
        dict(tpl="bignum", kicker="Le moment où on hésite", big="30 j", title="pour *changer d'avis*",
             sub="Tu la testes chez toi, à ton rythme. Les conditions sont détaillées sur la page Retours."),
    ], caption="""Brosse à dents électrique d'une marque que tu ne connais pas : c'est normal d'hésiter.

Alors on a mis en face 30 jours pour changer d'avis. Tu la reçois, tu l'utilises matin et soir, et tu décides.

Et les avis clients sont publics sur la fiche produit, critiques comprises.

[CTA]

""" + TAGS_T + " #achatsansrisque")),

    (14, dict(date="x", kind="carousel", axis="DESIGN", slides=[
        dict(tpl="fear", kicker="Ce qu'on entend", fear="Les électriques, c'est moche et ça prend toute la place.",
             kicker2="Ce qu'on a fait", answer="Pas de socle, *un design sobre*",
             sub="Elle se recharge en USB-C et se range dans son étui. Rien ne reste branché sur le lavabo.", swipe=True),
        dict(tpl="note", kicker="Le socle", bad="Il faut la laisser branchée tous les soirs.", hand="avec la Bamboo+ :",
             good="*Une charge,* un mois de brossage.", sub="30 jours d'autonomie. Le câble reste dans le tiroir.", swipe=True),
        dict(tpl="bignum", kicker="Sur ton lavabo", big="0", title="socle branché *en permanence*",
             sub="C'est le compliment qui revient le plus dans les avis : le design, et rien qui traîne."),
    ], caption="""Brosse à dents électrique et salle de bain soignée, ça peut aller ensemble.

Pas de socle qui reste branché, une recharge USB-C qui tient 30 jours, et un étui pour la ranger.

Swipe pour voir ce qu'on a changé.

[CTA]

""" + TAGS_T + " #salledebain")),

    (19, dict(date="x", kind="photo", axis="PARENTS", slides=[
        dict(tpl="fear", kicker="Le soir, 20h40", fear="Compter jusqu'à 120 à voix haute, tous les soirs.",
             kicker2="Ce qui change", answer="Le minuteur *compte à ta place*",
             sub="Il vibre toutes les 30 secondes : l'enfant change de zone tout seul, tu n'as plus rien à surveiller."),
    ], caption="""Brosse à dents électrique et enfants : le minuteur change tout.

Plus besoin de compter à voix haute. Toutes les 30 secondes, la brosse vibre et l'enfant passe à la zone suivante. Au bout de 2 minutes, c'est fini.

[CTA]

""" + TAGS_T + " #parents")),
]

# Quatre posts « natifs » de plus : ils ressemblent à ce qu'on voit sur son téléphone
NEW_18H += [
    (22, dict(date="x", kind="photo", axis="CADEAU", slides=[
        dict(tpl="chatpost", kicker="Chaque année, la même conversation", contact="Maman", msgs=[
            ("in", "Tu veux quoi pour Noël ?"), ("out", "Rien, j'ai tout"),
            ("in", "Même pas une nouvelle brosse à dents ?"), ("out", "Une électrique ? Ok, celle-là je l'utiliserai vraiment")],
            caption_end="Le cadeau qui sert matin et soir."),
    ], caption="""Brosse à dents électrique : le cadeau qu'on utilise vraiment.

Pas un gadget qui finit au fond d'un tiroir en janvier. Une brosse qui sert matin et soir, avec l'étui de voyage dans la boîte.

[CTA]

""" + TAGS_T + " #ideecadeau")),

    (26, dict(date="x", kind="photo", axis="ECO", slides=[
        dict(tpl="notespost", title="Budget brosse à dents", img=s("tete_main"), items=[
            ("Tête de rechange ailleurs : jusqu'à 15 €", ""), ("Une tous les 3 mois", ""),
            ("Jusqu'à 60 € par an", "barre"), ("Pulse Care : 14,90 € l'année", "total")]),
    ], caption="""Brosse à dents électrique : on a fait le calcul des têtes de rechange.

Ailleurs, une tête peut coûter jusqu'à 15 €, et il en faut 4 par an. Chez Pulse Care, le pack de 4 têtes coûte 14,90 €.

[CTA]

""" + TAGS_T + " #budget")),

    (29, dict(date="x", kind="photo", axis="PEUR", slides=[
        dict(tpl="commentpost", comment="J'ai les gencives qui saignent un peu. Une électrique, ça va empirer ?",
             kicker2="Notre réponse", answer="Ce qui blesse, c'est *la pression,* pas les vibrations.",
             sub="Mode Sensible, poils ricin, aucune force à appliquer. Si les saignements durent, parles-en à ton dentiste."),
    ], caption="""Brosse à dents électrique et gencives qui saignent : la question qu'on reçoit souvent.

Ce qui irrite les gencives, c'est surtout la pression. Avec le mode Sensible, tu poses la brosse et tu guides, sans frotter. Et si les saignements durent, parles-en à ton dentiste.

[CTA]

""" + TAGS_T + " #gencivessensibles")),

    (32, dict(date="x", kind="photo", axis="CONFIANCE", slides=[
        dict(tpl="reviewpost", kicker="Avis clients", title="Ce qu'ils en disent, *mot pour mot*", quotes=[
            "J'étais sceptique au début.", "Le minuteur est hyper pratique.",
            "Elle est stylée, légère et tient hyper bien la charge.", "Je l'ai emmenée en voyage sans même recharger."]),
    ], caption="""Brosse à dents électrique : ce que disent les clients, mot pour mot.

Quatre avis publiés sur la fiche produit. Le design et l'autonomie reviennent le plus souvent.

[CTA]

""" + TAGS_T + " #avisclients")),
]

# ───────────────────────────── Vidéos avec voix off
# Une vidéo par axe. Chaque scène porte la phrase lue pendant qu'elle est à l'écran ("say") :
# la durée de la scène suit la longueur de sa phrase, et l'ensemble est calé sur la durée réelle
# de la voix. Types de scènes : photo, split, list, counter, timer, compare, end (render.py).
VOICES = {"agathe": "SptHT9PQ49isQvxFm28t", "maxence": "GGkMUTZaJ8IyPwaHimUq"}

VIDEOS = [
  # PARENTS · format POV (plan filmé + texte natif), puis carte avec le plan qui joue dedans
  dict(id="v-parents", music="Feeling Happy", date="2026-11-14", axis="PARENTS", voice="agathe", pal="corail", fmt="POV", scenes=[
    dict(t="pov", clip="fillette", title="POV : il est 20h40 et tu négocies chaque seconde de brossage", sub="« Encore 30 secondes ! »",
         say="Tous les soirs, c'est la même négociation. « Encore trente secondes ! »"),
    dict(t="card", clip="fille-matin", kicker="Le minuteur", title="Il *compte à ta place*", sub="Une vibration toutes les 30 secondes.",
         say="Avec Poulsse Kèr, le minuteur vibre toutes les trente secondes. Ton enfant change de zone tout seul… et toi, tu arrêtes de compter à voix haute."),
    dict(t="end", img=s("p121"), title="Deux minutes. Sans bagarre.", sub="pulsecarefrance.com",
         say="Deux minutes, sans bagarre. Le lien est en bio."),
  ], caption="""Brosse à dents électrique et enfants : la fin de la négociation du soir.

Le minuteur vibre toutes les 30 secondes. L'enfant change de zone tout seul, et toi tu arrêtes de compter.

[CTA]

""" + TAGS_T + " #parents"),

  # ÉCONOMIE · format Notes (le calcul qui s'écrit), puis grille des prix
  dict(id="v-eco", music="Sounds Good", date="2026-11-17", axis="ECO", voice="maxence", pal="lime", fmt="Notes", scenes=[
    dict(t="counter", clip="dentifrice", kicker="Une tête de rechange", value=15, suffix=" €", label="jusqu'à 15 € pièce, ailleurs",
         say="Tu as déjà regardé le prix des têtes de rechange ? Jusqu'à quinze euros pièce."),
    dict(t="notes", title="Budget brosse à dents", items=[("Une tête : jusqu'à 15 €", ""), ("Une tous les 3 mois", ""), ("Jusqu'à 60 € par an", "barre")],
         say="Et il en faut une tous les trois mois."),
    dict(t="grid", shots=[s("ricin_pack4"), s("nylon_pack4_noir"), s("tete_ricin2"), s("p012")], labels=["Ricin", "Nylon", "3,73 € la tête", "14,90 € l'an"], kicker="Chez Pulse Care", title="*3,73 €* la tête",
         say="Chez Poulsse Kèr, c'est trois euros soixante-treize la tête. Quatorze euros quatre-vingt-dix pour toute l'année."),
    dict(t="end", img=s("duo_tete"), title="Le vrai prix, affiché.", sub="pulsecarefrance.com", say="Le lien est en bio."),
  ], caption="""Brosse à dents électrique : le prix qu'on oublie, ce sont les têtes.

Ailleurs, une tête de rechange peut coûter jusqu'à 15 €. Chez Pulse Care : 3,73 € la tête en pack de 4, soit 14,90 € pour l'année.

[CTA]

""" + TAGS_T + " #budget"),

  # PEUR · format question reçue + réponse, sur plan filmé
  dict(id="v-peur", music="Curiosity", date="2026-11-20", axis="PEUR", voice="agathe", pal="creme", fmt="Question / réponse", scenes=[
    dict(t="comment", clip="femme-brosse", comment="J'ai les gencives sensibles. Une électrique, ça ne va pas être trop agressif ?",
         title="Ce qui blesse, c'est *la pression.*",
         say="« J'ai les gencives sensibles, une électrique, ça ne va pas être trop agressif ? » En vrai, ce qui blesse, c'est la pression. Pas les vibrations."),
    dict(t="burst", shots=[s("modes_main"), "clip:homme-gros-plan", s("ricin_face")], kicker="Mode Sensible", title="Tu poses. *Elle travaille.*",
         say="Avec le mode Sensible de Poulsse Kèr, tu poses la brosse, tu guides, et le minuteur te dit quand changer de zone."),
    dict(t="end", img=s("ricin_profil"), title="Douce là où il faut.", sub="pulsecarefrance.com", say="Le lien est en bio."),
  ], caption="""Brosse à dents électrique et gencives sensibles : ce qui blesse, c'est la pression.

Avec le mode Sensible, tu poses la brosse et tu guides, sans frotter. Le minuteur découpe le brossage en 4 zones de 30 secondes.

[CTA]

""" + TAGS_T + " #gencivessensibles"),

  # CADEAU · format conversation SMS (petite scène de la vie)
  dict(id="v-cadeau", music="A Very Happy Christmas", date="2026-11-23", axis="CADEAU", voice="agathe", pal="nuit", fmt="Conversation", scenes=[
    dict(t="chat", contact="Maman", msgs=[("in", "Tu veux quoi pour Noël ?"), ("out", "Rien, j'ai tout"), ("in", "Même pas une nouvelle brosse à dents ?"), ("out", "Une électrique ? Ok, ça je l'utiliserai vraiment")],
         say="« Tu veux quoi pour Noël ? » « Rien, j'ai tout. » « Même pas une nouvelle brosse à dents ? » … Bon. Celle-là, je l'utiliserai vraiment."),
    dict(t="grid", shots=["u:1627130595904-ebeeb6540a93", s("boite_bambou"), s("etui_ouvert")], labels=["Matin et soir", "Prêt à emporter", "Étui inclus"], kicker="Celui-là sert", title="*Matin et soir,* toute l'année",
         say="Une brosse Poulsse Kèr, ça sert matin et soir, toute l'année. Un seul bouton, quatre modes, et l'étui de voyage dans la boîte."),
    dict(t="end", img="u:1545608444-f045a6db6133", title="Le cadeau qui ne finit pas au tiroir.", sub="59,90 € · pulsecarefrance.com",
         say="Cinquante-neuf euros quatre-vingt-dix. Le lien est en bio."),
  ], caption="""Brosse à dents électrique : l'idée cadeau qui sert matin et soir.

Pas un gadget qu'on range après Noël. Un seul bouton, 4 modes, et l'étui de voyage inclus.

[CTA]

""" + TAGS_T + " #ideecadeau"),

  # PREUVE · format expert / statistique : la phrase du dentiste, le comparatif, le chiffre
  dict(id="v-preuve", music="Raising Me Higher", date="2026-11-26", axis="PREUVE", voice="maxence", pal="foret", fmt="Statistique", scenes=[
    dict(t="hook", clip="dentiste-geste", kicker="Chez le dentiste", title="« Il faudrait *mieux brosser.* »",
         say="Chez le dentiste, on te dit toujours la même chose : il faudrait mieux brosser."),
    dict(t="compare", left=("À la main", ["Tu choisis la durée", "Tu choisis la pression", "Tu oublies le fond"]),
         right=("Pulse Care", ["Minuteur 2 min", "41 000 vibrations/min", "4 zones de 30 s"]),
         say="À la main, tu décides de tout : la durée, la pression, les zones oubliées."),
    dict(t="counter", clip="dentiste-radio", kicker="Plaque en moins au-delà de 3 mois", value=21, suffix=" %", label="Revue Cochrane : électrique contre manuelle",
         say="Les essais compilés par Cochrane montrent jusqu'à vingt et un pour cent de plaque en moins avec une brosse électrique."),
    dict(t="end", img=s("p004"), title="La technique, c'est elle qui l'applique.", sub="pulsecarefrance.com",
         say="Poulsse Kèr. Le lien est en bio."),
  ], caption="""Brosse à dents électrique ou manuelle : ce que disent les essais.

La revue Cochrane compile des dizaines d'essais : jusqu'à 21 % de plaque en moins au-delà de 3 mois avec une électrique.

[CTA]

""" + TAGS_T + " #sciencedentaire"),

  # CONFIANCE · format avis client (vrai avis de la fiche produit)
  dict(id="v-confiance", music="Smile", date="2026-11-29", axis="CONFIANCE", voice="agathe", pal="ocre", fmt="Avis client", scenes=[
    dict(t="hook", img=s("p029"), kicker="Le moment où on hésite", title="Panier rempli, *doigt en l'air*.",
         say="Une marque que tu ne connais pas, à cinquante-neuf euros quatre-vingt-dix… c'est normal d'hésiter."),
    dict(t="review", kicker="Avis client", quote="J'étais sceptique au début.",
         say="D'ailleurs, la phrase qu'on lit le plus dans nos avis, c'est celle-là : « J'étais sceptique au début. »"),
    dict(t="card", img=s("p021"), kicker="Sans risque", title="*30 jours* pour changer d'avis", sub="pulsecarefrance.com",
         say="Alors on a mis trente jours pour changer d'avis, et la livraison gratuite en point relais. Le lien est en bio."),
  ], caption="""Brosse à dents électrique d'une marque que tu ne connais pas ? On comprend.

« J'étais sceptique au début » : c'est l'avis qu'on lit le plus. 30 jours pour changer d'avis, et la livraison gratuite en point relais dès 20 €.

[CTA]

""" + TAGS_T + " #avisclients"),

  # DESIGN · format POV sur plan filmé, puis grille
  dict(id="v-design", music="Tech House vibes", date="2026-12-02", axis="DESIGN", voice="maxence", pal="creme", fmt="POV", scenes=[
    dict(t="pov", clip="homme-miroir", title="POV : tout est rangé dans ta salle de bain… sauf le socle branché sur le lavabo",
         say="Ta salle de bain est nickel… sauf ce socle branché en permanence sur le lavabo."),
    dict(t="grid", shots=[s("p087"), s("bamboo_face"), s("etui_voyage"), s("usb")], labels=["Sans socle", "Design sobre", "Étui", "USB-C"], kicker="Ce qu'on a changé", title="*Pas de socle.* Un étui.",
         say="Poulsse Kèr, c'est pas de socle : une recharge en USB-C qui tient un mois, un étui pour la ranger, et des têtes en bambou."),
    dict(t="card", img=s("p084"), kicker="Sur le lavabo", title="Rien ne traîne. *Tout est beau.*", sub="pulsecarefrance.com",
         say="Le lien est en bio."),
  ], caption="""Brosse à dents électrique sans socle branché en permanence.

Une recharge USB-C qui tient 30 jours, un étui pour la ranger, des têtes en bambou. Rien ne traîne sur le lavabo.

[CTA]

""" + TAGS_T + " #salledebain"),

  # GASPI · format statistique + carte
  dict(id="v-gaspi", music="Rising Forest", date="2026-12-05", axis="GASPI", voice="agathe", pal="nuit", fmt="Statistique", scenes=[
    dict(t="counter", img="u:1583642037383-861ac716c3f0", kicker="Par an", value=4, suffix=" ×", label="tu jettes une brosse entière",
         say="Quatre fois par an, tu jettes une brosse entière. Alors que le manche marchait encore."),
    dict(t="card", img=s("tete_main2"), kicker="Avec Pulse Care", title="Le manche reste. *Seule la tête part.*",
         say="Avec Poulsse Kèr, le manche reste. Tu changes seulement la tête, et elle est en bambou."),
    dict(t="end", img=s("p095"), title="Tu changes ce qui est usé. Pas le reste.", sub="pulsecarefrance.com",
         say="On ne te dit pas que c'est parfait. Juste qu'on jette moins. Le lien est en bio."),
  ], caption="""Brosse à dents électrique : tu changes ce qui est usé, pas le reste.

Le manche reste des années. Tous les 3 mois, seule la tête part, et elle est en bambou. On ne te dit pas que c'est parfait, juste qu'on jette moins.

[CTA]

""" + TAGS_T + " #moinsjeter"),

  # PRATIQUE · format POV (la valise qui ne ferme pas)
  dict(id="v-pratique", music="Motivating Mornings", date="2026-12-08", axis="PRATIQUE", voice="maxence", pal="lime", fmt="POV", scenes=[
    dict(t="pov", clip="valise-zip", title="POV : la valise est pleine et il reste le socle de ta brosse à dents",
         say="Partir trois jours, et devoir encore caser le socle, le câble, l'adaptateur…"),
    dict(t="counter", clip="valise-pliage", kicker="Une charge", value=30, suffix=" j", label="d'autonomie, en USB-C",
         say="Poulsse Kèr tient trente jours sur une charge. Tu pars, tu laisses le chargeur à la maison."),
    dict(t="grid", shots=[s("etui_plat"), s("p085"), "u:1719782758766-f0a4a3808afe"], labels=["Étui inclus", "Léger", "Étanche IPX7"], kicker="Dans la trousse", title="Étui inclus. *Étanche IPX7.*",
         say="L'étui est inclus, et elle est étanche."),
    dict(t="end", img=s("etui"), title="Tu pars léger.", sub="pulsecarefrance.com", say="Le lien est en bio."),
  ], caption="""Brosse à dents électrique pour voyager : 30 jours sur une charge.

Tu laisses le chargeur à la maison. L'étui de voyage est inclus, et elle est étanche IPX7.

[CTA]

""" + TAGS_T + " #voyage"),

  # RÉSULTAT · format démonstration rapide (plans filmés coupés vite)
  dict(id="v-resultat", music="Summer Fun", date="2026-12-11", axis="RESULTAT", voice="agathe", pal="corail", fmt="Démo rapide", scenes=[
    dict(t="counter", clip="cafe-gorgee", kicker="Par jour", value=3, suffix=" cafés", label="et ça finit par se voir",
         say="Trois cafés par jour… et ça finit par se voir sur les dents."),
    dict(t="burst", shots=["clip:cafe-fumant", s("p019"), "clip:sourire"], kicker="Mode Blanchiment", title="Café, thé, vin : *les taches de surface*",
         say="Le mode Blanchiment de Poulsse Kèr travaille les taches de surface : café, thé, vin. Ce n'est pas un produit chimique, c'est un polissage, tous les jours."),
    dict(t="card", img="u:1552650272-b8a34e21bc4b", title="Garde ton café. *Pas les taches.*", sub="pulsecarefrance.com", say="Le lien est en bio."),
  ], caption="""Brosse à dents électrique et café : le mode Blanchiment.

Il travaille les taches de surface (café, thé, vin) par un polissage quotidien, sans produit chimique.

[CTA]

""" + TAGS_T + " #cafe"),
]

def vo_text(v):
    return " ".join(sc["say"] for sc in v["scenes"])


def apply(posts):
    """Tague les posts du soir par axe et insère les posts qui complètent la matrice."""
    base = [p for p in posts if not p["date"].startswith("test")]
    for p, a in zip(base, AXIS_18H):
        p.setdefault("axis", a)
    for pos, p in sorted(NEW_18H, key=lambda x: x[0], reverse=True):
        posts.insert(pos, p)
