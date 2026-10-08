# -*- coding: utf-8 -*-
"""Pulse Care — posts de 10h (09/10 → 07/11/2026). Même format que content.py.
Sujets différents des posts de 18h ; aucune photo réutilisée."""
from content import S

def s(k): return "s:" + S[k]

T = "#brosseadentselectrique #hygienebuccodentaire #conseilsdentaires #pulsecare"
T2 = "#brosseadentselectrique #routinedumatin #hygienebuccodentaire #pulsecare"
T3 = "#brosseadentselectrique #brosseadentsbambou #hygienebuccodentaire #pulsecare"

POSTS_AM = [
dict(date="2026-10-09", kind="photo", slides=[
  dict(tpl="hero", img="u:1744970531102-27059b323df4", kicker="Question du matin", title="Avant ou après *le petit-déj* ?", sub="Avant : plus simple. Après : attends 30 minutes, surtout après un jus d'orange."),
], caption="""Brosse à dents électrique : avant ou après le petit-déjeuner ?

Les deux marchent. Ce qui compte :
→ avant le petit-déj : c'est le plus simple, tu n'as rien à attendre
→ après : attends 30 minutes si tu as bu du jus d'orange ou mangé un fruit acide

L'acide ramollit l'émail un court moment. Brosser juste après, c'est frotter un émail fragilisé.

Et toi, tu brosses quand ?

[CTA]

""" + T2),

dict(date="2026-10-10", kind="photo", slides=[
  dict(tpl="statement", img="u:1474722883778-792e7990302f", kicker="Café · thé · vin rouge", title="Des taches ? Le mode *Blanchiment* est là pour ça.", sub="Il aide à retirer les taches de surface. 1 à 2 fois par semaine."),
], caption="""Café, thé, vin rouge : ta brosse à dents électrique a un mode pour ça.

Le mode Blanchiment de la Bamboo+ aide à retirer les taches de surface.

Utilise-le 1 à 2 fois par semaine, à la place du mode Nettoyage. Le reste du temps, garde ta routine habituelle.

[CTA]

""" + T),

dict(date="2026-10-11", kind="carousel", slides=[
  dict(tpl="hero", img="u:1772911141524-d3dc8b1cc97e", kicker="Brosse à dents électrique", title="Souple, medium *ou dure* ?", swipe=True),
  dict(tpl="list", img="u:1590928192338-73e004fad28e", title="Ce qu'il faut savoir", items=[("Souple","La plus conseillée par les dentistes."),("Dure","Elle peut irriter les gencives et user l'émail."),("Avec une sonique","Ce sont les vibrations qui nettoient, pas la dureté.")], page="2/3"),
  dict(tpl="product", img=s("nylon_pack4"), kicker="Têtes Pulse Care", title="Tête en bambou, *poils ricin ou nylon*", sub="Clip en une seconde sur ton manche Pulse Care.", page="3/3"),
], caption="""Brosse à dents électrique : poils souples, medium ou durs ?

Pour la plupart des gens, souple suffit. C'est ce que conseillent les dentistes.

Une brosse dure n'est pas plus efficace. Elle peut même irriter les gencives. Avec une brosse sonique, ce sont les vibrations qui font le travail.

[CTA]

""" + T3),

dict(date="2026-10-12", kind="carousel", slides=[
  dict(tpl="hero", img="u:1515007917921-cad9bf0e2e87", kicker="Maladies dentaires", title="La carie : *comment elle se forme*", swipe=True),
  dict(tpl="list", img="u:1670250492416-570b5b7343b1", title="En 3 étapes", numbered=True, items=[("Le sucre nourrit les bactéries","Celles de la plaque dentaire."),("Elles produisent de l'acide","Après chaque prise sucrée."),("L'acide attaque l'émail","Petit à petit, la carie se creuse.")], page="2/2"),
], caption="""La carie, comment elle se forme ? Et comment ta brosse à dents électrique t'aide à l'éviter.

1. Le sucre nourrit les bactéries de la plaque
2. Elles produisent de l'acide
3. L'acide attaque l'émail, la carie se creuse

Ce qui protège : retirer la plaque 2 fois par jour avec un dentifrice fluoré, limiter le grignotage sucré, voir ton dentiste une fois par an.

[CTA]

#brosseadentselectrique #carie #hygienebuccodentaire #pulsecare"""),

dict(date="2026-10-13", kind="photo", slides=[
  dict(tpl="product", img=s("ricin_pack4_douce"), kicker="Abonnement Pulse Care", title="Tes têtes *livrées automatiquement*", sub="Plus besoin d'y penser."),
], caption="""Les têtes de ta brosse à dents électrique Pulse Care, livrées chez toi sans y penser.

Avec l'abonnement :
→ tu choisis tes têtes, ricin ou nylon
→ elles arrivent automatiquement
→ sans engagement, tu arrêtes quand tu veux depuis ton compte

Fini la tête usée gardée 6 mois.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

dict(date="2026-10-14", kind="photo", slides=[
  dict(tpl="hero", img="u:1626519259050-9284a69bb184", kicker="Tête en bambou", title="Bambou ou plastique : *la tête change tout.*", sub="Tu changes ta tête 4 fois par an. Chez Pulse Care, elle est en bambou."),
], caption="""Sur une brosse à dents électrique, la tête est la pièce que tu jettes le plus.

4 fois par an, en moyenne.

Chez Pulse Care, cette tête est en bambou, pas en plastique. Les poils sont à base d'huile de ricin ou en nylon. Le manche, en plastique ASA, reste.

[CTA]

#brosseadentsbambou #brosseadentselectrique #bambou #pulsecare"""),

dict(date="2026-10-15", kind="photo", slides=[
  dict(tpl="hero", img="u:1676897296672-2bb21aacb342", kicker="La bonne dose", title="Une *noisette* de dentifrice suffit.", sub="Pas besoin de couvrir toute la tête de la brosse."),
], caption="""Combien de dentifrice sur ta brosse à dents électrique ?

Une noisette. Pas plus.

Avec une brosse sonique, trop de dentifrice fait vite de la mousse partout. Et ça ne nettoie pas mieux.

Pour les enfants, demande la bonne quantité à ton dentiste selon leur âge.

[CTA]

""" + T),

dict(date="2026-10-16", kind="carousel", slides=[
  dict(tpl="hero", img="u:1612994451093-c6791c8989cd", kicker="Haleine fraîche", title="Mauvaise haleine : *4 causes* courantes", swipe=True),
  dict(tpl="list", img="u:1594745561149-2211ca8c5d98", title="Les coupables", numbered=True, items=[("La langue","Elle garde les bactéries. Brosse-la."),("La bouche sèche","Bois de l'eau dans la journée."),("Entre les dents","Fil dentaire ou brossettes."),("Une tête usée","On la change tous les 3 mois.")], page="2/2"),
], caption="""Mauvaise haleine malgré ta brosse à dents électrique ? Voici 4 causes courantes.

1. La langue n'est pas brossée
2. La bouche est sèche : bois de l'eau
3. Des restes entre les dents : passe le fil
4. La tête de brosse est trop vieille

Si ça dure, parles-en à ton dentiste.

[CTA]

""" + T),

dict(date="2026-10-17", kind="photo", slides=[
  dict(tpl="statement", img="u:1533093818119-ac1fa47a6d59", kicker="Autonomie", title="Une charge. *Un mois de brossage.*", sub="Jusqu'à 30 jours d'autonomie, recharge USB-C."),
], caption="""Une charge de ta brosse à dents électrique Bamboo+ tient jusqu'à 30 jours.

→ recharge en USB-C, environ 2,5 heures
→ pas de socle sur le lavabo
→ le même câble que ton téléphone

Tu la charges, tu l'oublies pendant un mois.

[CTA]

""" + T3),

dict(date="2026-10-18", kind="carousel", slides=[
  dict(tpl="hero", img="u:1785332500322-8e52876f9ab9", kicker="Tête en bambou", title="3 gestes pour *bien l'entretenir*", swipe=True),
  dict(tpl="list", img="u:1633591056817-6f7b3b067c60", title="L'entretien", numbered=True, items=[("Rince-la","Sous l'eau claire après chaque brossage."),("Laisse-la sécher","Tête en haut, à l'air libre."),("Change-la","Tous les 3 mois.")], page="2/2"),
], caption="""La tête en bambou de ta brosse à dents électrique : 3 gestes d'entretien.

1. Rince-la à l'eau claire après chaque brossage
2. Laisse-la sécher tête en haut, à l'air libre
3. Change-la tous les 3 mois

Simple. Et ta tête reste propre jusqu'au bout.

[CTA]

""" + T3),

dict(date="2026-10-19", kind="photo", slides=[
  dict(tpl="hero", img="u:1685084844860-5d94e6c82939", kicker="Hygiène", title="Ta brosse sèche *à l'air libre* ?", sub="Range-la tête en haut. Évite le placard fermé juste après usage."),
], caption="""Où ranges-tu ta brosse à dents électrique après usage ?

La bonne place : à l'air libre, tête en haut. Elle sèche plus vite.

À éviter : le placard fermé ou l'étui juste après le brossage. L'humidité reste enfermée.

L'étui de voyage, c'est pour le transport. Laisse sécher la tête avant de la ranger dedans.

[CTA]

""" + T3),

dict(date="2026-10-20", kind="carousel", slides=[
  dict(tpl="hero", img="u:1668127039849-c5dd95be3fa5", kicker="Abonnement Pulse Care", title="Comment ça marche, *en 3 points*", swipe=True),
  dict(tpl="list", img=s("nylon_pack4_profil"), title="L'abonnement", numbered=True, items=[("Tu choisis tes têtes","Poils ricin ou nylon."),("Elles arrivent chez toi","Automatiquement, sans commande à repasser."),("Sans engagement","Tu arrêtes quand tu veux depuis ton compte.")], page="2/2"),
], caption="""L'abonnement têtes de brosse à dents électrique Pulse Care, en 3 points.

1. Tu choisis tes têtes : ricin ou nylon
2. Elles arrivent chez toi automatiquement
3. Sans engagement : tu arrêtes à tout moment depuis ton compte client

Tu n'as plus à te demander quand changer ta tête.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

dict(date="2026-10-21", kind="photo", slides=[
  dict(tpl="statement", img="u:1698749778813-ad5f2814e50f", kicker="Maladies dentaires", title="Le tartre, c'est de la plaque *qui a durci.*", sub="Une fois installé, seul ton dentiste peut l'enlever."),
], caption="""Le tartre : ce que ta brosse à dents électrique peut faire, et ce qu'elle ne peut pas faire.

La plaque dentaire se forme chaque jour. Si elle n'est pas retirée, elle durcit et devient du tartre.

→ ta brosse retire la plaque, matin et soir
→ le tartre déjà installé : seul ton dentiste peut l'enlever, lors d'un détartrage

[CTA]

#brosseadentselectrique #tartre #hygienebuccodentaire #pulsecare"""),

dict(date="2026-10-22", kind="carousel", slides=[
  dict(tpl="hero", img="u:1607613009820-a29f7bb81c04", kicker="Brosse manuelle", title="Tous les 3 mois, *tu jettes tout.*", swipe=True),
  dict(tpl="list", img="u:1634068966402-86a27b9d57c1", title="La différence", items=[("Brosse manuelle","Le manche entier part à la poubelle."),("Pulse Care","Seule la tête en bambou se change."),("Le manche","Tu le gardes.")], page="2/2"),
], caption="""Brosse manuelle ou brosse à dents électrique Pulse Care : ce que tu jettes tous les 3 mois.

→ manuelle : toute la brosse, manche compris
→ Pulse Care : seulement la tête, en bambou

Le manche, tu le gardes.

[CTA]

""" + T3),

dict(date="2026-10-23", kind="carousel", slides=[
  dict(tpl="hero", img="u:1775642550110-158263bc1ade", kicker="Brosse à dents électrique", title="Ta routine du matin *en 3 étapes*", swipe=True),
  dict(tpl="list", img="u:1773863120758-172bd05090d2", title="Le matin", numbered=True, items=[("Un verre d'eau","Pour réhydrater ta bouche."),("2 minutes de brossage","Mode Nettoyage, le minuteur gère."),("Tu craches, tu ne rinces pas","Le fluor reste sur les dents.")], page="2/2"),
], caption="""Ta routine du matin avec ta brosse à dents électrique, en 3 étapes.

1. Un verre d'eau au réveil
2. 2 minutes de brossage, mode Nettoyage
3. Tu craches le dentifrice, tu ne rinces pas

Moins de 3 minutes. Tous les matins.

[CTA]

""" + T2),

dict(date="2026-10-24", kind="photo", slides=[
  dict(tpl="hero", img="u:1559703248-dcaaec9fab78", kicker="Dents sensibles", title="Une glace et ça *pique* ?", sub="Passe en mode Sensible et parles-en à ton dentiste."),
], caption="""Dents sensibles au froid ? Ta brosse à dents électrique a un mode pour ça.

Le mode Sensible adoucit les vibrations. Utilise-le tous les jours si tu as les dents ou les gencives sensibles.

Si la douleur revient souvent, parles-en à ton dentiste.

[CTA]

""" + T),

dict(date="2026-10-25", kind="carousel", slides=[
  dict(tpl="hero", img="u:1497700003451-e1df943a194b", kicker="Budget", title="Une brosse électrique, *ça coûte combien* par an ?", swipe=True),
  dict(tpl="stats", img="u:1608145264900-e9905d0d6de8", title="Le calcul", items=[("59,90 €","la Bamboo+, avec 2 têtes"),("14,90 €","le pack de 4 têtes"),("3 mois","par tête"),("30 j","par charge")], page="2/2"),
], caption="""Brosse à dents électrique Pulse Care : combien ça coûte vraiment ?

→ 59,90 € la Bamboo+, avec 2 têtes, l'étui et le câble
→ 14,90 € le pack de 4 têtes de recharge
→ une tête tous les 3 mois

Le manche, tu le gardes. Tu ne rachètes que les têtes.

[CTA]

""" + T3),

dict(date="2026-10-26", kind="photo", slides=[
  dict(tpl="product", img=s("nylon_gauche"), kicker="Têtes Pulse Care", title="Elle se change *en une seconde*", sub="Tu retires l'ancienne, tu enfonces la nouvelle. C'est tout."),
], caption="""Changer la tête de ta brosse à dents électrique Pulse Care prend une seconde.

→ tu tires l'ancienne tête vers le haut
→ tu enfonces la nouvelle jusqu'au bout
→ c'est prêt

Les têtes sont compatibles uniquement avec les manches Pulse Care.

[CTA]

#brosseadentselectrique #tetederechange #brosseadentsbambou #pulsecare"""),

dict(date="2026-10-27", kind="photo", slides=[
  dict(tpl="hero", img="u:1598033594208-5b9d61d5df3c", kicker="Bain de bouche", title="Pas *juste après* le brossage.", sub="Sinon tu rinces le fluor du dentifrice. Utilise-le à un autre moment."),
], caption="""Bain de bouche après ta brosse à dents électrique ? Pas tout de suite.

Juste après le brossage, il rince le fluor du dentifrice.

Utilise-le à un autre moment de la journée. Par exemple après le déjeuner.

Tu en utilises un ?

[CTA]

""" + T),

dict(date="2026-10-28", kind="photo", slides=[
  dict(tpl="statement", img="u:1660737217679-6ddd9768654a", kicker="Gingivite", title="Gencives rouges qui saignent ?", sub="C'est souvent une gingivite. Brosse en douceur et consulte ton dentiste."),
], caption="""Gencives qui saignent avec ta brosse à dents électrique : c'est souvent une gingivite.

Ce qu'il faut faire avec ta brosse à dents électrique :
→ continue de brosser, en mode Sensible
→ n'appuie pas
→ passe le fil chaque jour
→ consulte ton dentiste si ça dure

Prise tôt, la gingivite se soigne bien.

[CTA]

#brosseadentselectrique #gingivite #hygienebuccodentaire #pulsecare"""),

dict(date="2026-10-29", kind="photo", slides=[
  dict(tpl="statement", img="u:1594756154841-ac5d160dbf46", kicker="Abonnement Pulse Care", title="Oublier de changer ta tête ? *Plus possible.*", sub="Tes têtes arrivent chez toi, automatiquement."),
], caption="""Le vrai problème de la brosse à dents électrique ? On oublie de changer la tête.

Avec l'abonnement Pulse Care, tes têtes arrivent chez toi automatiquement. Tu n'as plus à y penser.

Sans engagement, résiliable à tout moment depuis ton compte.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

dict(date="2026-10-30", kind="photo", slides=[
  dict(tpl="hero", img="u:1580580959742-e1fd6cb08867", kicker="Poils ricin", title="Le ricin, *c'est une plante.*", sub="Nos poils ricin sont fabriqués à base d'huile de ricin, d'origine végétale."),
], caption="""D'où viennent les poils ricin de ta brosse à dents électrique Pulse Care ?

De l'huile de ricin, extraite des graines d'une plante.

Résultat : une fibre d'origine végétale, au toucher très doux, montée sur une tête en bambou.

[CTA]

#brosseadentsbambou #brosseadentselectrique #ricin #pulsecare"""),

dict(date="2026-10-31", kind="carousel", slides=[
  dict(tpl="statement", img="u:1600721187850-c944924fd48a", kicker="Entre les dents", title="Fil dentaire ou brossettes ?", swipe=True),
  dict(tpl="list", img="u:1643624050871-fcb133e45037", title="Comment choisir", items=[("Le fil","Pour les espaces serrés."),("Les brossettes","Pour les espaces plus larges."),("La bonne taille","Ton dentiste te la donne en 30 secondes.")], page="2/2"),
], caption="""Ta brosse à dents électrique + quoi entre les dents : fil ou brossettes ?

→ fil dentaire : espaces serrés
→ brossettes : espaces plus larges

Les deux font le job. Demande la bonne taille de brossette à ton dentiste.

[CTA]

""" + T),

dict(date="2026-11-01", kind="carousel", slides=[
  dict(tpl="statement", img="u:1662850886700-4ec19bd30d11", kicker="Mythe ou réalité", title="Une brosse électrique abîme l'émail ?", swipe=True),
  dict(tpl="list", img="u:1656404256001-2ddddacd050f", title="Non, si tu l'utilises bien", items=[("Tu n'appuies pas","Les vibrations nettoient seules."),("Mode Sensible au début","Le temps de t'habituer."),("Poils souples","Comme nos têtes ricin ou nylon.")], page="2/2"),
], caption="""Une brosse à dents électrique abîme-t-elle l'émail ?

Non, si tu l'utilises bien.

Le risque vient de la pression. Pose la tête, ne frotte pas, laisse les vibrations travailler. Et commence en mode Sensible si tu débutes.

Swipe pour les bons réflexes.

[CTA]

""" + T),

dict(date="2026-11-02", kind="photo", slides=[
  dict(tpl="statement", img="u:1611695434369-a8f5d76ceb7b", kicker="Question rapide", title="Ta tête de brosse a quel âge ?", sub="Plus de 3 mois ? Il est temps de la changer."),
], caption="""Question rapide : la tête de ta brosse à dents électrique a quel âge ?

Plus de 3 mois, il est temps de la changer. Même si elle a l'air propre.

Réponds en commentaire : moins de 3 mois ou plus ?

[CTA]

""" + T),

dict(date="2026-11-03", kind="photo", slides=[
  dict(tpl="hero", img="u:1588776814546-1ffcf47267a5", kicker="Maladies dentaires", title="La parodontite, *ça commence aux gencives.*", sub="Une gingivite non soignée peut évoluer. Le contrôle annuel sert à ça."),
], caption="""Parodontite : ce que ta brosse à dents électrique peut faire pour tes gencives.

C'est une maladie des gencives qui commence souvent par une gingivite non soignée.

Elle touche les tissus qui tiennent les dents.

Ce qui aide à la prévenir :
→ brosse à dents électrique 2 fois par jour
→ fil ou brossettes chaque jour
→ un contrôle chez le dentiste chaque année

[CTA]

#brosseadentselectrique #parodontite #hygienebuccodentaire #pulsecare"""),

dict(date="2026-11-04", kind="photo", slides=[
  dict(tpl="hero", img="u:1707944145479-12755f0434d8", kicker="Idée cadeau", title="Une brosse *qu'on garde.*", sub="Le pack découverte Pulse Care, à 64,90 €.", price="64,90 €"),
], caption="""Une brosse à dents électrique en cadeau ? C'est utile tous les jours.

Le pack découverte Pulse Care :
→ le manche Bamboo+
→ des têtes en bambou à poils de ricin

64,90 €. À offrir, ou à t'offrir.

[CTA]

#brosseadentselectrique #ideecadeau #brosseadentsbambou #pulsecare"""),

dict(date="2026-11-05", kind="photo", slides=[
  dict(tpl="product", img=s("nylon_pack2_profil"), kicker="Abonnement Pulse Care", title="Sans engagement. *Tu arrêtes quand tu veux.*", sub="Depuis ton compte client ou par mail à contact@pulsecarefrance.com."),
], caption="""Abonnement têtes de brosse à dents électrique Pulse Care : sans engagement.

→ tu arrêtes à tout moment depuis ton compte client
→ ou par mail à contact@pulsecarefrance.com
→ l'arrêt prend effet à la fin de la période en cours

Tu testes, et tu gardes si ça te va.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

dict(date="2026-11-06", kind="carousel", slides=[
  dict(tpl="hero", img="u:1562337404-3044c84ac061", kicker="Gencives sensibles", title="3 réflexes *qui changent tout*", swipe=True),
  dict(tpl="list", img="u:1548382131-e0ebb1f0cdea", title="Les réflexes", numbered=True, items=[("Mode Sensible","Vibrations adoucies."),("Poils ricin","Toucher très doux."),("Zéro pression","Tu poses, tu guides.")], page="2/2"),
], caption="""Gencives sensibles ? 3 réflexes avec ta brosse à dents électrique.

1. Le mode Sensible tous les jours
2. Des poils doux, comme nos têtes ricin
3. Aucune pression sur la brosse

Si l'inconfort dure, parles-en à ton dentiste.

[CTA]

""" + T),

dict(date="2026-11-07", kind="carousel", slides=[
  dict(tpl="hero", img="u:1761558913086-0ac892d6fe78", kicker="Le récap", title="5 astuces du mois *à garder*", swipe=True),
  dict(tpl="list", img="u:1508002366005-75a695ee2d17", title="À retenir", numbered=True, items=[("2 min, 2 fois par jour","Le minuteur gère."),("Fil ou brossettes","Une fois par jour."),("Tu ne rinces pas","Le fluor reste."),("Une tête tous les 3 mois",""),("Mode Sensible","Si tes gencives sont fragiles.")], page="2/2"),
], caption="""Brosse à dents électrique : les 5 astuces du mois à garder.

1. 2 minutes, 2 fois par jour
2. Fil ou brossettes une fois par jour
3. Tu craches, tu ne rinces pas
4. Une nouvelle tête tous les 3 mois
5. Mode Sensible si tes gencives sont fragiles

Enregistre ce post.

[CTA]

""" + T),
]
