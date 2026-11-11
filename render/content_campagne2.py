# -*- coding: utf-8 -*-
"""Campagne large, vague 2 : 8 designs complètement différents, inspirés des formats qui marchent sur les réseaux
(formats natifs, anti-pub, damier, une de journal, étiquette, mème, billet). Insérés tôt dans les files pour tester vite."""
from content import s

T = "#brosseadentselectrique #hygienebuccodentaire #pulsecare"

def P(axis, kind, slides, caption, tag):
    return dict(date="x", kind=kind, axis=axis, slides=slides, caption=caption + "\n\n[CTA]\n\n" + T + " " + tag)

CAMP2_AM = [
  P("PEUR", "photo", [dict(tpl="search", query="brosse à dents électrique gencives qui saignent", suggest=[
        "brosse à dents électrique gencives sensibles", "brosse électrique ça fait mal ?", "brosse électrique mode doux"],
        answer="Ce qui irrite, c'est *la pression*", sub="Mode Sensible, poils ricin : tu guides, tu n'appuies pas. Si ça saigne longtemps, parles-en à ton dentiste.")],
    """Brosse à dents électrique et gencives qui saignent : ce que tout le monde tape un jour.

Ce qui irrite, c'est surtout la pression. Avec le mode Sensible, tu poses la brosse et tu guides. Si les saignements durent, parles-en à ton dentiste.""", "#gencivessensibles"),

  P("PRATIQUE", "photo", [dict(tpl="lockscreen", day="Si ta brosse pouvait t'écrire", time="7:42", notifs=[
        ("Pulse Care", "Minuteur", "30 secondes : passe à la zone suivante."),
        ("Pulse Care", "Batterie", "Encore des semaines d'autonomie. Laisse le chargeur à la maison."),
        ("Pulse Care", "Tête de brosse", "3 mois déjà : c'est le moment de la changer.")],
        caption_end="Pas d'appli. Juste une brosse qui pense à tout.")],
    """Brosse à dents électrique : si elle pouvait t'écrire, voilà ce qu'elle te dirait.

Pas d'appli, pas de notification : le minuteur vibre toutes les 30 secondes et une charge tient jusqu'à 30 jours.""", "#routine"),

  P("PREUVE", "photo", [dict(tpl="headline", kicker="Santé", headline="Brosse électrique : jusqu'à 21 % de plaque en moins",
        dek="C'est ce que montre la revue Cochrane des essais comparant brosses électriques et manuelles, après 3 mois d'utilisation.",
        photo=s("bamboo_face"), legend="Brosse sonique Pulse Care, têtes en bambou.")],
    """Brosse à dents électrique : jusqu'à 21 % de plaque en moins.

C'est le résultat de la revue Cochrane qui a compilé les essais comparant brosses électriques et manuelles, après 3 mois d'utilisation.""", "#hygienedentaire"),

  P("TRANSPARENCE", "photo", [dict(tpl="label", kicker="Sans blabla", title="Fiche technique", serving="Pour 1 brosse Pulse Care", rows=[
        ("Prix", "59,90 €", True), ("Vibrations", "41 000 / min"), ("Modes", "4"), ("Minuteur", "2 min, 4 × 30 s"),
        ("Autonomie", "30 jours"), ("Charge", "USB-C"), ("Étanchéité", "IPX7"), ("Têtes incluses", "2, en bambou", True)],
        note="Livraison gratuite en point relais dès 20 €. 30 jours pour changer d'avis.")],
    """Brosse à dents électrique : la fiche technique, sans blabla.

41 000 vibrations par minute, 4 modes, minuteur de 2 minutes, 30 jours d'autonomie, USB-C, IPX7. Et 2 têtes en bambou incluses.""", "#transparence"),

  P("DESIGN", "photo", [dict(tpl="checker", cells=[
        dict(text="Du bambou, *rien de plus*"), dict(img=s("bamboo_face")),
        dict(img=s("etui_voyage")), dict(text="Un étui, *zéro socle*", small="Recharge en USB-C, rangement dans l'étui.")])],
    """Brosse à dents électrique au design bambou : rien de plus, rien de trop.

Pas de socle branché sur le lavabo : un étui, un câble USB-C, et c'est tout.""", "#design"),

  P("CONFIANCE", "photo", [dict(tpl="antiad", kicker="Honnêtement", title="Ne l'achète *pas* si…", no=[
        "Tu aimes jeter ta brosse entière tous les 3 mois", "Tu veux une appli connectée", "Tu tiens 2 minutes pile sans regarder l'heure"],
        yes=["Tu veux un minuteur qui compte pour toi", "Tu pars souvent sans ton chargeur", "Tu préfères changer la tête, pas la brosse"])],
    """Brosse à dents électrique : ne l'achète pas si tu te reconnais ici.

On préfère te le dire : elle n'a pas d'appli, et elle ne sert à rien si tu aimes jeter ta brosse entière. Par contre, si tu veux un minuteur et 30 jours d'autonomie, elle est faite pour toi.""", "#honnete"),

  P("HABITUDE", "photo", [dict(tpl="meme", top_label="Ce que tu crois", top="Je me brosse *2 minutes*",
        bottom_label="Ce qui se passe vraiment", bottom="*45 secondes,* le téléphone dans l'autre main", photo=s("p121"))],
    """Brosse à dents électrique ou pas : on croit tous se brosser 2 minutes.

Le minuteur compte pour toi et vibre toutes les 30 secondes. Tag la personne qui scrolle en se brossant les dents.""", "#humour"),

  P("PRATIQUE", "photo", [dict(tpl="boarding", kicker="Vacances", title="30 jours *sans chargeur*", frm="SDB", frm_name="Ta salle de bain",
        to="ALL", to_name="Partout", fields=[("Passager", "Toi"), ("Bagage", "Brosse + étui"), ("Chargeur", "Non requis"), ("Autonomie", "30 jours")])],
    """Brosse à dents électrique de voyage : 30 jours sans chargeur.

Une charge tient jusqu'à 30 jours. Tu pars avec la brosse dans son étui, le câble reste à la maison.""", "#voyage"),
]

CAMP2_PM = [
  P("PRIX", "photo", [dict(tpl="search", query="combien coûte une tête de brosse à dents électrique", suggest=[
        "tête de brosse à dents électrique pas cher", "tête brosse électrique tous les combien", "pack têtes brosse électrique"],
        answer="*3,73 €* chez Pulse Care", sub="Pack de 4 têtes en bambou à 14,90 €. Une tête tous les 3 mois, soit un an.")],
    """Brosse à dents électrique : combien coûte une tête de rechange ?

Chez Pulse Care : 3,73 € la tête, en pack de 4 à 14,90 €. Une tête tous les 3 mois, donc un pack par an.""", "#budget"),

  P("ADOS", "photo", [dict(tpl="lockscreen", day="mardi 21 h 47", time="21:47", photo=s("deux_brosses"), notifs=[
        ("Messages", "Maman", "Tu t'es brossé les dents ?"),
        ("Messages", "Léo", "Oui, 2 minutes. La brosse a vibré 4 fois."),
        ("Messages", "Maman", "Ok, bonne nuit")],
        caption_end="Le minuteur, c'est aussi une preuve.")],
    """Brosse à dents électrique pour ado : la conversation du soir, version courte.

2 minutes, 4 vibrations, une par zone. Plus besoin de négocier.""", "#ado"),

  P("GASPI", "photo", [dict(tpl="headline", kicker="Consommation", headline="Jusqu'à 4 brosses entières jetées par an, par personne",
        dek="Une brosse changée tous les 3 mois, c'est 4 manches à la poubelle. Avec Pulse Care, seule la tête en bambou se change.",
        photo=s("ricin_pack4_vue"), legend="Pack de 4 têtes en bambou Pulse Care.")],
    """Brosse à dents électrique : et si tu arrêtais de jeter le manche ?

Changer de brosse tous les 3 mois, c'est jusqu'à 4 manches jetés par an. Avec Pulse Care, le manche reste et tu ne changes que la tête en bambou.""", "#antigaspi"),

  P("ENTRETIEN", "photo", [dict(tpl="label", kicker="Les têtes", title="Fiche technique", serving="Pour 1 tête de rechange", rows=[
        ("Prix", "3,73 €", True), ("Support", "Bambou"), ("Poils", "Ricin ou nylon"), ("Durée conseillée", "3 mois"), ("Vendue en", "Pack de 4", True)],
        note="14,90 € le pack : un an de brossage.")],
    """Brosse à dents électrique : la fiche technique des têtes de rechange.

Support en bambou, poils ricin ou nylon, à changer tous les 3 mois. 14,90 € le pack de 4, soit 3,73 € la tête.""", "#entretien"),

  P("CADEAU", "photo", [dict(tpl="checker", cells=[
        dict(img=s("duo_coffret")), dict(text="Le cadeau *qui sert*", small="Matin et soir, toute l'année."),
        dict(text="94,90 € *le duo*", small="2 brosses, 2 étuis, 4 têtes."), dict(img=s("deux_brosses"))])],
    """Brosse à dents électrique en duo : le cadeau qui sert matin et soir.

2 brosses, 2 étuis, 4 têtes en bambou : 94,90 € le pack duo. Livraison gratuite en point relais.""", "#ideecadeau"),

  P("ECO", "photo", [dict(tpl="antiad", kicker="Honnêtement", title="Elle n'est *pas* parfaite", turn="Mais", no=[
        "Le manche n'est pas en bambou", "Elle se recharge à l'électricité", "Les têtes usées partent quand même à la poubelle"],
        yes=["Les têtes sont en bambou", "Tu changes la tête, pas toute la brosse", "Une charge tient jusqu'à 30 jours"])],
    """Brosse à dents électrique : on ne te dira pas qu'elle est parfaite.

Le manche n'est pas en bambou et les têtes usées partent quand même à la poubelle. Mais les têtes sont en bambou, et tu ne jettes plus la brosse entière.""", "#honnete"),

  P("PRATIQUE", "photo", [dict(tpl="meme", top_label="Ma trousse avant", top="Brosse, socle, câble, adaptateur…",
        bottom_label="Ma trousse maintenant", bottom="*Une brosse* dans son étui. Point.", photo=s("etui"))],
    """Brosse à dents électrique de voyage : ta trousse avant, ta trousse maintenant.

Pas de socle, pas d'adaptateur : la brosse tient 30 jours dans son étui.""", "#voyage"),

  P("ROUTINE", "photo", [dict(tpl="boarding", kicker="Week-end", title="Départ vendredi, *sans chargeur*", frm="VEN", frm_name="Vendredi soir",
        to="DIM", to_name="Dimanche soir", fields=[("Bagage", "Brosse + étui"), ("Chargeur", "Pas besoin"), ("Étanche", "IPX7"), ("Autonomie", "30 jours")])],
    """Brosse à dents électrique : le week-end, tu laisses le chargeur.

Une charge tient jusqu'à 30 jours, et l'étui la protège dans le sac.""", "#weekend"),
]
