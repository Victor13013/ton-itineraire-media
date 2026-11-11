# -*- coding: utf-8 -*-
"""Campagne large : 8 nouveaux axes de test, chacun décliné en photo et en carrousel, à 10h et à 18h.
Axes : MYTHES, HABITUDE, TRANSPARENCE, PRIX, ENTRETIEN, ADOS, QUESTION, ROUTINE.
Ajoutés au bout des files : la publication continue sans trou."""
from content import s

T = "#brosseadentselectrique #hygienebuccodentaire #pulsecare"

def P(axis, kind, slides, caption, tag):
    return dict(date="x", kind=kind, axis=axis, slides=slides, caption=caption + "\n\n[CTA]\n\n" + T + " " + tag)

CAMP_AM = [
  P("MYTHES", "photo", [dict(tpl="quiz", kicker="Vrai ou faux ?", title="Une électrique *use l'émail*",
        options=["Vrai", "Faux", "Ça dépend de la pression", "Aucune idée"])],
    """Brosse à dents électrique et émail : vrai ou faux ?

La bonne réponse : ça dépend surtout de la pression. Avec une électrique, tu poses la tête et tu guides, sans frotter. Le mode Sensible est fait pour ça.

Réponds en commentaire avant de lire la réponse.""", "#vraioufaux"),

  P("HABITUDE", "carousel", [
     dict(tpl="fear", kicker="Ce que tu te dis", fear="Je me brosse 2 minutes, promis.", kicker2="Ce qui se passe souvent",
          answer="Sans minuteur, on s'arrête *avant*", sub="Le minuteur compte pour toi : 4 zones, 30 secondes chacune.", swipe=True),
     dict(tpl="schema", kind="zones", kicker="Le minuteur", title="4 zones, *30 secondes chacune*", sub="Une vibration, tu changes de zone. Au bout de 2 minutes, c'est fini.")],
    """Brosse à dents électrique avec minuteur : tu te brosses vraiment 2 minutes ?

Sans montre, on s'arrête souvent avant. Le minuteur découpe les 2 minutes en 4 zones de 30 secondes et vibre à chaque changement.""", "#routine"),

  P("TRANSPARENCE", "photo", [dict(tpl="versus", kicker="Pas de surprise", title="Ce qui est inclus, *ce que tu rachètes*", both_good=True,
        left=["Dans la boîte", ["Le manche sonique", "2 têtes en bambou", "Étui et câble USB-C"]],
        right=["Ensuite", ["Les têtes, c'est tout", "14,90 € le pack de 4", "Une tous les 3 mois"]])],
    """Brosse à dents électrique à 59,90 € : ce qui est inclus, et ce que tu rachètes ensuite.

Dans la boîte : le manche sonique, 2 têtes en bambou, l'étui de voyage et le câble USB-C. Ensuite, tu ne rachètes que les têtes.""", "#transparence"),

  P("PRIX", "photo", [dict(tpl="bignum", kicker="Le calcul", big="0,16 €", title="par jour, *la première année*",
        sub="59,90 € divisé par 365 jours. Ensuite, seules les têtes se changent.")],
    """Brosse à dents électrique : 0,16 € par jour la première année.

59,90 € divisé par 365 jours. Ensuite, tu ne changes que la tête : 14,90 € le pack de 4, soit un an de brossage.""", "#budget"),

  P("ENTRETIEN", "photo", [dict(tpl="notespost", title="Tête à changer ?", img=s("p088"), items=[
        ("Les poils s'écartent", ""), ("La couleur a passé", ""), ("Plus de 3 mois", ""), ("Tu changes la tête, pas la brosse", "total")])],
    """Brosse à dents électrique : 3 signes que ta tête est à changer.

Les poils s'écartent, la couleur a passé, elle a plus de 3 mois. Tu changes la tête, le manche reste.""", "#entretien"),

  P("ADOS", "photo", [dict(tpl="chatpost", kicker="Tous les soirs, la même scène", contact="Léo", msgs=[
        ("out", "Tu t'es brossé les dents ?"), ("in", "Oui"), ("out", "La brosse est sèche…"), ("in", "Ok j'y vais")],
        caption_end="Le minuteur, lui, ne négocie pas.")],
    """Brosse à dents électrique pour ado : la conversation que tous les parents connaissent.

Avec le minuteur, il sait quand il a fini : 2 minutes, une vibration toutes les 30 secondes.

Tag un parent qui a déjà eu cette conversation.""", "#ado"),

  P("QUESTION", "photo", [dict(tpl="commentpost", comment="Elle passe sous la douche ?", kicker2="Notre réponse",
        answer="Oui : *étanche IPX7.*", sub="Douche, lavabo, rinçage sous le robinet. Et une charge tient jusqu'à 30 jours.")],
    """Brosse à dents électrique sous la douche : la question qu'on reçoit souvent.

Oui, elle est étanche IPX7. Douche, lavabo, rinçage : aucun souci.

Une autre question ? Écris-la en commentaire.""", "#faq"),

  P("ROUTINE", "carousel", [
     dict(tpl="steps", kicker="Ta routine du soir", title="2 minutes, *4 zones*", items=[
        ["Haut gauche", "30 secondes, puis une vibration."], ["Haut droite", "30 secondes."], ["Bas gauche", "30 secondes."], ["Bas droite", "Fin des 2 minutes."]]),
     dict(tpl="tracker", kicker="Le défi", title="7 jours, *matin et soir*", sub="Enregistre ce post et coche tes cases chaque soir.", rows=["Matin", "Soir"], done=0)],
    """Brosse à dents électrique : ta routine du soir en 2 minutes.

4 zones, 30 secondes chacune, le minuteur te guide. Enregistre le défi et coche tes cases pendant 7 jours.""", "#defi"),

  P("MYTHES", "carousel", [
     dict(tpl="fear", kicker="Idée reçue n°1", fear="Une électrique, ça abîme les gencives.", kicker2="En vrai",
          answer="Ce qui irrite, c'est *la pression*", sub="Tu guides la brosse, tu n'appuies pas. Mode Sensible pour les gencives fragiles.", swipe=True),
     dict(tpl="fear", kicker="Idée reçue n°2", fear="Ça coûte cher à l'usage.", kicker2="En vrai",
          answer="*3,73 €* la tête en pack de 4", sub="Une tête tous les 3 mois : 14,90 € pour l'année."),
     dict(tpl="fear", kicker="Idée reçue n°3", fear="Faut tout le temps la recharger.", kicker2="En vrai",
          answer="Jusqu'à *30 jours* par charge", sub="En USB-C, le même câble que ton téléphone.")],
    """Brosse à dents électrique : 3 idées reçues qu'on entend souvent.

Les gencives, le prix des têtes, la batterie : swipe pour voir ce qu'il en est.

Tu en croyais combien ?""", "#vraioufaux"),

  P("HABITUDE", "photo", [dict(tpl="tracker", kicker="Le défi", title="7 jours, *2 brossages par jour*",
        sub="Enregistre ce post et coche tes cases. Le minuteur s'occupe du chrono.", rows=["Matin", "Soir"], done=2)],
    """Brosse à dents électrique : le défi des 7 jours.

Matin et soir, 2 minutes, pendant 7 jours. Enregistre ce post, coche tes cases, et dis-nous en commentaire si tu as tenu.""", "#defi"),

  P("TRANSPARENCE", "photo", [dict(tpl="note", img=s("p083"), kicker="Ce qu'on voit souvent", bad="Livraison offerte… mais à partir de 50 €.",
        hand="chez nous :", good="Gratuite en point relais *dès 20 €*", sub="La brosse est à 59,90 € : la livraison est offerte.")],
    """Brosse à dents électrique : la livraison, sans astérisque.

Livraison gratuite en point relais dès 20 € d'achat. La brosse est à 59,90 € : tu ne paies pas le port.""", "#livraisongratuite"),

  P("PRIX", "photo", [dict(tpl="versus", kicker="Sur un an", title="Ce que tu paies *en têtes*", both_good=False,
        left=["Ailleurs", ["Jusqu'à 15 € la tête", "4 têtes par an", "Jusqu'à 60 €"]],
        right=["Pulse Care", ["3,73 € la tête", "Pack de 4", "14,90 € l'année"]])],
    """Brosse à dents électrique : ce que tu paies vraiment en têtes de rechange.

Ailleurs, une tête peut coûter jusqu'à 15 €. Il en faut 4 par an. Chez Pulse Care, le pack de 4 coûte 14,90 €.""", "#budget"),

  P("ENTRETIEN", "photo", [dict(tpl="steps", kicker="Entretien", title="Ta brosse, *en 3 gestes*", items=[
        ["Rince la tête", "Sous le robinet, après chaque brossage."], ["Laisse sécher", "Tête en haut, à l'air libre."], ["Change la tête", "Tous les 3 mois."]])],
    """Brosse à dents électrique : l'entretien en 3 gestes.

Tu rinces la tête, tu la laisses sécher à l'air libre, tu la changes tous les 3 mois. Le manche, lui, reste.""", "#entretien"),

  P("ADOS", "photo", [dict(tpl="fear", kicker="Ce qu'il te dit", fear="Je me suis brossé les dents, promis.", kicker2="Ce qui l'aide",
        answer="Un minuteur qui *compte à sa place*", sub="Une vibration toutes les 30 secondes. 2 minutes, sans négocier.")],
    """Brosse à dents électrique pour ado : « je me suis brossé les dents, promis ».

Le minuteur compte à sa place : 2 minutes, une vibration toutes les 30 secondes pour changer de zone.""", "#ado"),

  P("QUESTION", "carousel", [
     dict(tpl="quiz", kicker="Une question qu'on reçoit souvent", title="Elle tient *combien de temps* sur une charge ?",
          options=["1 semaine", "2 semaines", "1 mois", "Aucune idée"], swipe=True),
     dict(tpl="bignum", kicker="La réponse", big="30 j", title="sur une charge, *en USB-C*", sub="Pour 2 brossages de 2 minutes par jour.")],
    """Brosse à dents électrique : elle tient combien de temps sur une charge ?

Jusqu'à 30 jours pour 2 brossages par jour. La recharge se fait en USB-C, le même câble que ton téléphone.""", "#faq"),

  P("ROUTINE", "photo", [dict(tpl="editorial", img=s("p091"), over="7 h 42", kicker="Matin pressé", title="2 minutes, *chrono*",
        sub="Un bouton, 4 modes, et le minuteur compte pour toi. Tu te prépares, elle travaille.")],
    """Brosse à dents électrique : la routine du matin pressé.

Un bouton, 4 modes, un minuteur de 2 minutes. Tu brosses, elle compte.""", "#routinematin"),
]

CAMP_PM = [
  P("MYTHES", "photo", [dict(tpl="commentpost", comment="Une électrique, c'est pas un peu un gadget ?", kicker2="Notre réponse",
        answer="Elle sert *matin et soir,* tous les jours", sub="Minuteur, 4 modes, 30 jours d'autonomie. Un gadget finit dans un tiroir.")],
    """Brosse à dents électrique : gadget ou vrai outil ?

Elle sert matin et soir, tous les jours. Minuteur de 2 minutes, 4 modes, 30 jours d'autonomie.""", "#vraioufaux"),

  P("HABITUDE", "photo", [dict(tpl="quiz", kicker="Sois honnête", title="Tu te brosses *combien de temps* ?",
        options=["Moins d'1 minute", "1 à 2 minutes", "2 minutes pile", "Je n'ai jamais compté"])],
    """Brosse à dents électrique ou pas : tu te brosses combien de temps ?

Réponds en commentaire, sans tricher. La recommandation, c'est 2 minutes, 2 fois par jour.""", "#routine"),

  P("TRANSPARENCE", "carousel", [
     dict(tpl="steps", kicker="Avant de payer", title="Tu sais *tout*", items=[
        ["59,90 €", "Brosse, 2 têtes, étui, câble USB-C."], ["Livraison", "Gratuite en point relais dès 20 €."], ["30 jours", "Pour changer d'avis."]]),
     dict(tpl="bignum", kicker="Sans risque", big="30 j", title="pour *changer d'avis*", sub="Elle ne te plaît pas ? Tu as 30 jours.")],
    """Brosse à dents électrique : tout ce que tu dois savoir avant de payer.

59,90 € avec 2 têtes, l'étui et le câble. Livraison gratuite en point relais. 30 jours pour changer d'avis.""", "#transparence"),

  P("PRIX", "photo", [dict(tpl="notespost", title="Mon budget dents", img=s("p016"), items=[
        ("Brosse : 59,90 €, une fois", ""), ("Têtes : 14,90 € par an", ""), ("Avant : une brosse jetée tous les 3 mois", "barre"),
        ("74,80 € max la 1re année", "total")])],
    """Brosse à dents électrique : le vrai budget de la première année.

Brosse 59,90 € + pack de 4 têtes 14,90 € : au plus 74,80 € la première année. Ensuite, seules les têtes se changent.""", "#budget"),

  P("ENTRETIEN", "carousel", [
     dict(tpl="fear", kicker="Ce que tu te dis", fear="Je change ma brosse quand elle est cassée.", kicker2="En vrai",
          answer="Les poils s'usent *avant*", sub="Au bout de 3 mois, ils s'écartent et nettoient moins bien.", swipe=True),
     dict(tpl="ticket", kicker="Pack de 4", title="Un an *de têtes*", head="Pulse Care · pack de 4 têtes",
          lines=[["4 têtes en bambou", "incluses"], ["Poils", "ricin ou nylon"], ["Durée", "12 mois"]],
          total=["À payer", "14,90 €"], note="Soit 3,73 € la tête.")],
    """Brosse à dents électrique : pourquoi changer la tête tous les 3 mois.

Les poils s'usent avant que la brosse casse : ils s'écartent et nettoient moins bien. Le pack de 4 têtes couvre un an pour 14,90 €.""", "#entretien"),

  P("ADOS", "photo", [dict(tpl="bignum", kicker="Le compte est bon", big="2 min", title="sans *négocier*",
        sub="Le minuteur vibre toutes les 30 secondes. Plus besoin de compter à voix haute.")],
    """Brosse à dents électrique pour ado : 2 minutes, sans négocier.

Le minuteur vibre toutes les 30 secondes. Tu arrêtes de compter, il arrête de discuter.""", "#ado"),

  P("QUESTION", "photo", [dict(tpl="chatpost", kicker="Une question qu'on reçoit souvent", contact="Service client", msgs=[
        ("out", "Il y a combien de modes ?"), ("in", "4 : Sensible, Nettoyage, Blanchiment, Polissage"),
        ("out", "Et pour les gencives sensibles ?"), ("in", "Le mode Sensible, sans appuyer")],
        caption_end="Une autre question ? Écris-nous.")],
    """Brosse à dents électrique : quel mode choisir ?

4 modes : Sensible, Nettoyage, Blanchiment, Polissage. Gencives fragiles : le mode Sensible, et tu n'appuies pas.""", "#faq"),

  P("ROUTINE", "photo", [dict(tpl="split", img=s("p090"), kicker="Pack duo", title="Ta routine, *et la sienne*",
        items=["2 brosses, 2 étuis", "4 têtes en bambou", "Minuteur sur les deux"], price="94,90 €",
        sub="Livraison gratuite en point relais dès 20 € d'achat.", dark=True)],
    """Brosse à dents électrique en duo : ta routine, et la sienne.

2 brosses, 2 étuis, 4 têtes en bambou : 94,90 € le pack duo, soit 47,45 € la brosse.""", "#duo"),
]
