# -*- coding: utf-8 -*-
"""Pulse Care — posts de 10h, 30 jours (11/11 → 10/12/2026).

Thèmes du matin : hygiène dentaire, maladies dentaires, têtes de recharge,
abonnement, bambou des têtes, usage de la brosse.
Mêmes gabarits et mêmes DA que le créneau de 18h (voir content.py).
"""
from content import s, S, TAGS  # noqa: F401

POSTS_AM = [
# ───────────────────────── ACTU · Mois sans tabac (novembre 2026)
dict(date="2026-11-11", kind="carousel", da="b", slides=[
  dict(tpl="statement", img="u:1580489944761-15a19d654956", kicker="Mois sans tabac", title="Ce que ta bouche *y gagne*", swipe=True),
  dict(tpl="steps", tone="forest", kicker="En arrêtant", title="4 effets sur les dents", items=[("L'haleine change", "Souvent en quelques jours."), ("Les colorations s'arrêtent", "Le goudron ne se dépose plus sur l'émail."), ("Les gencives cicatrisent mieux", "Le tabac réduit l'irrigation des tissus."), ("Le risque de parodontite baisse", "Le tabac est un de ses premiers facteurs.")]),
  dict(tpl="statement", img="u:1544507888-56d73eb6046e", kicker="Si tu te lances", title="Tu n'es pas *tout seul.*", sub="Tabac info service au 39 89, ou mois-sans-tabac.fr. Kits gratuits en pharmacie."),
],
caption="""Aucune brosse à dents électrique ne compense le tabac. Mais novembre, c'est le Mois sans tabac, et c'est le bon moment pour en parler.

Ce que le tabac fait à la bouche :
→ il colore l'émail, et les taches reviennent vite
→ il réduit l'irrigation des gencives, donc la cicatrisation
→ il est l'un des premiers facteurs de parodontite
→ il masque les saignements, ce qui retarde le diagnostic

En arrêtant, l'haleine change souvent en quelques jours.

Pour se faire aider : 39 89 (gratuit) ou mois-sans-tabac.fr. Kits gratuits en pharmacie.

[CTA]

#moissanstabac #brosseadentselectrique #gencives #pulsecare"""),

# ───────────────────────── ACTU · M'T dents
dict(date="2026-11-13", kind="photo", da="a", tone="mint", slides=[
  dict(tpl="bignum", kicker="M'T dents", big="100 %", title="de 3 à 24 ans, *le contrôle est pris en charge*", sub="Un rendez-vous par an, sans avance de frais. La CPAM envoie un courrier avant chaque date.", img="u:1770871821382-60ea99b0a941"),
],
caption="""Une brosse à dents électrique ne remplace pas le contrôle annuel. Et de 3 à 24 ans, ce contrôle est gratuit.

C'est le dispositif M'T dents de l'Assurance Maladie :
→ un examen de prévention par an, de 3 à 24 ans inclus
→ pris en charge à 100 %, sans avance de frais
→ les soins qui en découlent (carie, détartrage) sont aussi couverts
→ la CPAM envoie un courrier environ un mois avant la date

Les soins doivent commencer dans les 3 mois suivant l'examen.

Si tu as des enfants, le prochain courrier mérite d'être ouvert.

[CTA]

#mtdents #brosseadentselectrique #preventiondentaire #pulsecare"""),
# ───────────────────────── 1 · 11/11 · petit-déj
dict(date="2026-11-11", kind="photo", da="b", tone="sand", slides=[
  dict(tpl="statement", kicker="Le matin", title="Avant ou après *le petit-déj* ?",
       options=["Avant, au réveil", "Après avoir mangé", "Les deux, au choix"], answer=0,
       note="Après un jus ou un fruit acide, attends 30 minutes."),
],
caption="""Brosse à dents électrique le matin : avant ou après le petit-déjeuner ?

Avant. Au réveil, tu retires la plaque formée pendant la nuit, et le fluor protège l'émail avant le repas.

Si tu préfères brosser après avoir mangé, attends 30 minutes quand il y a eu du jus d'orange, du café ou un fruit acide : l'émail est ramolli juste après, et le brossage l'abîme.

Team avant ou team après ?

[CTA]

#brosseadentselectrique #routinedumatin #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 2 · 12/11 · carie
dict(date="2026-11-12", kind="carousel", da="a", slides=[
  dict(tpl="hero", img="u:1606811971618-4486d14f3f99", kicker="Maladies dentaires", title="La carie : *comment elle se forme*", swipe=True),
  dict(tpl="steps", tone="honey", kicker="En 3 étapes", title="Le mécanisme", items=[("Tu manges du sucre", "Les bactéries de la plaque s'en nourrissent."), ("Elles produisent de l'acide", "Pendant environ 20 minutes."), ("L'acide attaque l'émail", "À force, il perce : c'est la carie.")]),
],
caption="""Une brosse à dents électrique sert surtout à casser ce cycle : voilà comment se forme une carie.

1. Tu manges du sucre. Les bactéries de la plaque s'en nourrissent.
2. Elles produisent de l'acide pendant une vingtaine de minutes.
3. Cet acide dissout l'émail. Répété chaque jour, il finit par percer.

C'est pour ça que grignoter toute la journée est pire que manger sucré d'un coup : chaque prise relance l'attaque acide.

[CTA]

#brosseadentselectrique #carie #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 3 · 13/11 · souple medium dure
dict(date="2026-11-13", kind="photo", da="c", slides=[
  dict(tpl="statement", img=s("ricin_face"), kicker="Souple, medium ou dure ?", title="Les dentistes recommandent *le souple.*",
       sub="Une brosse dure n'enlève pas plus de plaque. Elle abîme juste l'émail et la gencive."),
],
caption="""Souple, medium ou dure : quelle dureté de poils pour une brosse à dents électrique ?

Le souple. C'est la recommandation quasi unanime des dentistes.

Une brosse dure ne retire pas plus de plaque. Elle use l'émail, fait reculer les gencives et crée des zones sensibles au collet de la dent.

Les têtes Pulse Care sont en poils souples, en ricin ou en nylon, sur une tête en bambou.

[CTA]

#brosseadentselectrique #poilssouples #gencivessensibles #pulsecare"""),

# ───────────────────────── 4 · 14/11 · noisette
dict(date="2026-11-14", kind="photo", da="a", tone="mint", slides=[
  dict(tpl="bignum", kicker="Dentifrice", big="1", title="noisette, *pas plus*", sub="Trop de dentifrice fait de la mousse, pas un meilleur nettoyage.", img="u:1775642549786-813dc015a495"),
],
caption="""Sur une brosse à dents électrique, une noisette de dentifrice suffit. Pas le boudin des publicités.

Trop de dentifrice crée de la mousse. La mousse donne la sensation que c'est propre, et on s'arrête avant les 2 minutes.

Pour les enfants, la quantité est encore plus petite : un grain de riz avant 3 ans, un petit pois ensuite. Demande à ton dentiste le dosage de fluor adapté à leur âge.

[CTA]

#brosseadentselectrique #dentifrice #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 5 · 15/11 · abonnement
dict(date="2026-11-15", kind="photo", da="b", tone="fresh", slides=[
  dict(tpl="product", img=s("ricin_pack4"), kicker="Abonnement Pulse Care", title="Tes têtes *livrées automatiquement*", sub="Au rythme que tu choisis. Sans engagement."),
],
caption="""L'abonnement têtes de brosse à dents électrique Pulse Care : tu n'y penses plus.

Le principe : tu choisis tes têtes et le rythme de livraison. Elles arrivent chez toi toutes seules, sans commande à repasser.

→ poils ricin ou poils nylon
→ têtes en bambou
→ sans engagement, modifiable ou arrêtable depuis ton compte

La tête de brosse est le truc qu'on oublie toujours de racheter. Problème réglé.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

# ───────────────────────── 6 · 16/11 · mauvaise haleine
dict(date="2026-11-16", kind="carousel", da="c", slides=[
  dict(tpl="arch", img="u:1599566219227-2efe0c9b7f5f", kicker="Haleine", title="Mauvaise haleine : *4 causes* courantes", swipe=True),
  dict(tpl="list", img="u:1595514535316-b8c85bf9bbf9", title="Les coupables", numbered=True, items=[("La langue", "Elle héberge une grande part des bactéries."), ("La bouche sèche", "Moins de salive, plus d'odeurs."), ("Les espaces entre les dents", "Là où la brosse ne passe pas."), ("Le tabac et le café", "Ils s'ajoutent au reste.")]),
],
caption="""Une brosse à dents électrique ne règle pas tout : 4 causes fréquentes de mauvaise haleine.

1. La langue. Elle héberge une bonne partie des bactéries responsables.
2. La bouche sèche. Moins de salive, c'est moins de nettoyage naturel.
3. Les espaces entre les dents, là où aucune brosse ne passe. D'où le fil ou les brossettes.
4. Le tabac et le café, qui s'ajoutent au reste.

Le geste en plus : 3 ou 4 passages doux sur la langue, de l'arrière vers l'avant.

[CTA]

#brosseadentselectrique #haleinefraiche #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 7 · 17/11 · une charge
dict(date="2026-11-17", kind="photo", da="a", tone="forest", slides=[
  dict(tpl="statement", img=s("usb"), kicker="Recharge", title="Une charge.\n*Un mois de brossage.*", sub="2,5 h sur le câble USB-C de ton téléphone, et c'est reparti pour 30 jours."),
],
caption="""Sur une brosse à dents électrique, l'autonomie change tout au quotidien.

La Bamboo+ tient jusqu'à 30 jours pour 2 brossages par jour. Une charge d'environ 2,5 heures, en USB-C.

Résultat : tu la branches une fois par mois, avec le câble que tu as déjà. Pas de socle permanent sur le lavabo, pas de prise mobilisée.

[CTA]

#brosseadentselectrique #autonomie #usbc #pulsecare"""),

# ───────────────────────── 8 · 18/11 · entretien
dict(date="2026-11-18", kind="carousel", da="b", slides=[
  dict(tpl="arch", img=s("p011"), kicker="Entretien", title="3 gestes pour *qu'elle dure*", swipe=True),
  dict(tpl="steps", tone="fresh", kicker="Après chaque brossage", title="Les 3 gestes", items=[("Rince la tête", "Moteur allumé, 2 secondes sous l'eau."), ("Essuie le manche", "Surtout autour du port USB-C."), ("Laisse sécher debout", "À l'air libre, jamais dans l'étui fermé.")]),
],
caption="""Entretenir sa brosse à dents électrique, c'est 10 secondes par jour.

1. Rince la tête sous l'eau, moteur allumé deux secondes, pour chasser le dentifrice
2. Essuie le manche, surtout autour du port USB-C
3. Laisse sécher debout, à l'air libre

Le point important : ne range jamais la brosse humide dans l'étui fermé. L'humidité enfermée favorise les bactéries. L'étui sert au transport, pas au rangement quotidien.

[CTA]

#brosseadentselectrique #entretien #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 9 · 19/11 · gencives qui saignent
dict(date="2026-11-19", kind="photo", da="c", slides=[
  dict(tpl="hero", img="u:1580465446361-8aae5321522b", kicker="Gingivite", title="Des gencives qui saignent, *ce n'est pas normal.*",
       sub="C'est souvent le premier signe d'une gingivite. Brosse en douceur et parles-en à ton dentiste."),
],
caption="""Tes gencives saignent quand tu passes la brosse à dents électrique ? Ce n'est pas un signe que tu brosses bien.

C'est souvent le premier signe d'une gingivite : une inflammation due à la plaque accumulée à la ligne des gencives.

Ce qu'on fait :
→ on ne stoppe pas le brossage de la zone, on le fait en douceur
→ mode Sensible pendant quelques jours
→ fil ou brossettes tous les jours
→ et un avis du dentiste si ça dure plus d'une semaine

[CTA]

#brosseadentselectrique #gingivite #gencives #pulsecare"""),

# ───────────────────────── 10 · 20/11 · abonnement concret
dict(date="2026-11-20", kind="carousel", da="a", slides=[
  dict(tpl="arch", img=s("nylon_pack4_profil"), kicker="Abonnement Pulse Care", title="Comment ça marche, *en 3 points*", swipe=True),
  dict(tpl="steps", tone="sand", kicker="L'abonnement", title="Trois étapes", items=[("Tu choisis tes têtes", "Ricin ou nylon, la quantité que tu veux."), ("Tu choisis le rythme", "Tous les 1, 2 ou 3 mois."), ("Tu modifies quand tu veux", "Depuis ton compte client, sans engagement.")]),
],
caption="""L'abonnement têtes de brosse à dents électrique Pulse Care, concrètement.

1. Tu choisis tes têtes : poils ricin ou poils nylon
2. Tu choisis le rythme : tous les 1, 2 ou 3 mois
3. Tu modifies, mets en pause ou arrêtes quand tu veux depuis ton compte

Pas d'engagement, pas de période minimum. Juste des têtes qui arrivent quand il faut les changer.

[CTA]

#brosseadentselectrique #abonnement #tetederechange #pulsecare"""),

# ───────────────────────── 11 · 21/11 · tartre
dict(date="2026-11-21", kind="photo", da="b", tone="forest", slides=[
  dict(tpl="bignum", kicker="Maladies dentaires", big="72 h", title="pour que la plaque *durcisse*", sub="Passé ce délai, elle devient du tartre et ne part plus au brossage.", img="u:1593022356769-11f762e25ed9"),
],
caption="""Avec une brosse à dents électrique, tu as une fenêtre de 24 à 72 heures. C'est le temps qu'il faut à la plaque pour se minéraliser.

Avant : c'est un film souple, le brossage l'enlève.
Après : c'est du tartre, dur, collé à l'émail. Plus aucune brosse ne le retire.

Le tartre irrite la gencive et accroche encore plus de plaque. D'où le détartrage chez le dentiste, selon ce qu'il te recommande.

[CTA]

#brosseadentselectrique #tartre #detartrage #pulsecare"""),

# ───────────────────────── 12 · 22/11 · ce que tu jettes
dict(date="2026-11-22", kind="carousel", da="c", slides=[
  dict(tpl="hero", img=s("ricin_solo"), kicker="Têtes Pulse Care", title="Tous les 3 mois, *tu jettes tout* ?", swipe=True),
  dict(tpl="versus", kicker="La différence", title="Brosse manuelle *ou Pulse Care*", left=("Brosse manuelle", ["Toute la brosse part", "Pas de minuteur", "Tu rachètes tout tous les 3 mois"]), right=("Pulse Care", ["Seule la tête se change", "Minuteur 2 min intégré", "Le manche, tu le gardes"])),
],
caption="""Avec une brosse manuelle, tous les 3 mois, c'est l'objet entier qui part à la poubelle. Avec une brosse à dents électrique Pulse Care, c'est juste la tête.

Le manche reste des années. La tête, en bambou, se clipse et se déclipse en une seconde.

C'est la logique de la marque depuis le départ : réduire la partie qu'on jette, pas la partie qu'on garde.

[CTA]

#brosseadentselectrique #brosseadentsbambou #tetederechange #pulsecare"""),

# ───────────────────────── 13 · 23/11 · routine du matin
dict(date="2026-11-23", kind="carousel", da="a", slides=[
  dict(tpl="arch", img="u:1610352992666-61acb68b6ad6", kicker="Routine du matin", title="3 étapes, *4 minutes chrono*", swipe=True),
  dict(tpl="steps", tone="mint", kicker="Le matin", title="Dans cet ordre", items=[("Un verre d'eau", "Pour réhydrater la bouche au réveil."), ("2 minutes de brossage", "Mode Nettoyage, le minuteur gère."), ("Tu craches, tu ne rinces pas", "Le fluor reste sur les dents.")]),
],
caption="""Ta routine du matin avec une brosse à dents électrique, en 3 étapes.

1. Un verre d'eau au réveil. La bouche est sèche après la nuit, la salive doit repartir.
2. 2 minutes de brossage en mode Nettoyage. Le minuteur s'arrête seul.
3. Tu craches, tu ne rinces pas. Le fluor reste sur l'émail et continue d'agir.

Quatre minutes montre en main, café compris.

[CTA]

#brosseadentselectrique #routinedumatin #fluor #pulsecare"""),

# ───────────────────────── 14 · 24/11 · dents sensibles
dict(date="2026-11-24", kind="photo", da="b", tone="fresh", slides=[
  dict(tpl="hero", img="u:1626200949108-510618c118c3", kicker="Dents sensibles", title="Une boisson glacée *et ça pique* ?",
       sub="Souvent le signe que la dentine est à nu. Mode Sensible, poils souples, et un avis du dentiste."),
],
caption="""Une gorgée glacée et une douleur brève : la sensibilité dentaire touche beaucoup de monde, et la brosse à dents électrique y est parfois pour quelque chose.

Ce qui se passe : la dentine, sous l'émail, se retrouve exposée. Elle contient des micro-canaux qui transmettent le froid jusqu'au nerf.

Les causes fréquentes : brossage trop appuyé, poils trop durs, gencives qui reculent, aliments acides.

Ce que tu peux faire : mode Sensible, poils souples, aucune pression. Et un avis du dentiste si ça s'installe.

[CTA]

#brosseadentselectrique #dentssensibles #modesensible #pulsecare"""),

# ───────────────────────── 15 · 25/11 · ricin
dict(date="2026-11-25", kind="photo", da="c", slides=[
  dict(tpl="arch", img="u:1601385304565-9a38a051a1a0", kicker="Le ricin", title="C'est *une plante.*",
       sub="L'huile de ses graines sert à fabriquer une fibre souple, utilisée à la place du pétrole."),
],
caption="""Les poils de ricin sur une brosse à dents électrique, ça vient d'où ?

Le ricin est une plante cultivée pour ses graines. On en extrait une huile, transformée ensuite en fibre textile souple et résistante.

Cette fibre remplace une partie du pétrole habituellement utilisé pour les poils de brosse.

Résultat au brossage : un toucher plus doux, apprécié quand les gencives sont sensibles.

[CTA]

#brosseadentselectrique #poilsricin #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 16 · 26/11 · fil ou brossettes
dict(date="2026-11-26", kind="carousel", da="a", slides=[
  dict(tpl="statement", img="u:1677026010083-78ec7f1b84ed", kicker="Entre les dents", title="Ta brosse ne nettoie que *60 % des surfaces.*", swipe=True),
  dict(tpl="versus", tone="mint", kicker="Comment choisir", title="Fil *ou brossettes* ?", both_good=True, left=("Le fil", ["Pour les espaces serrés", "Une fois par jour, le soir", "Très peu cher"]), right=("Les brossettes", ["Pour les espaces plus larges", "Plus rapides à passer", "Taille donnée par ton dentiste"])),
],
caption="""Même la meilleure brosse à dents électrique ne nettoie qu'environ 60 % de la surface des dents. Les 40 % restants sont entre les dents.

D'où le fil dentaire ou les brossettes, une fois par jour, le soir de préférence.

→ Fil : pour les espaces serrés, très peu cher
→ Brossettes : pour les espaces plus larges, plus rapides. Demande la taille à ton dentiste

Tu passes le fil combien de fois par semaine ? Sois honnête.

[CTA]

#brosseadentselectrique #fildentaire #brossettes #pulsecare"""),

# ───────────────────────── 17 · 27/11 · voyage
dict(date="2026-11-27", kind="carousel", da="b", slides=[
  dict(tpl="hero", img="u:1779364815233-84ec09c6d6d5", kicker="Déplacements", title="Laisse le chargeur *à la maison*", swipe=True),
  dict(tpl="mosaic", tone="sand", kicker="Dans la trousse", title="Ce que tu emportes", imgs=[(s("etui_ouvert"), "L'étui en bambou"), (s("p018"), "Le manche"), (s("nylon_face"), "Une tête d'avance")]),
],
caption="""Partir avec sa brosse à dents électrique sans emporter le chargeur, c'est possible avec 30 jours d'autonomie.

Dans la trousse :
→ l'étui de voyage en bambou, qui protège la tête
→ le manche, chargé avant de partir
→ une tête d'avance si le séjour est long

Petit rappel : à l'arrivée, sors la brosse de l'étui pour qu'elle sèche. L'étui sert au transport, pas au rangement.

[CTA]

#brosseadentselectrique #voyage #troussedetoilette #pulsecare"""),

# ───────────────────────── 18 · 28/11 · parodontite
dict(date="2026-11-28", kind="photo", da="a", tone="forest", slides=[
  dict(tpl="statement", img="u:1598256989800-fe5f95da9787", kicker="Maladies dentaires", title="La parodontite *commence aux gencives.*",
       sub="Une gingivite non traitée peut atteindre l'os qui tient la dent. Un contrôle régulier évite d'en arriver là."),
],
caption="""Après la gingivite vient la parodontite. C'est la raison pour laquelle on insiste autant sur la ligne des gencives avec une brosse à dents électrique.

Le mécanisme : la plaque s'installe sous la gencive, l'inflammation s'étend, et elle finit par toucher l'os qui maintient la dent.

Les signes à ne pas ignorer : saignements répétés, gencives qui reculent, dents qui bougent, mauvaise haleine persistante.

Un contrôle chez le dentiste au moindre doute. Plus c'est pris tôt, plus c'est simple.

[CTA]

#brosseadentselectrique #parodontite #gencives #pulsecare"""),

# ───────────────────────── 19 · 29/11 · bain de bouche
dict(date="2026-11-29", kind="photo", da="c", slides=[
  dict(tpl="quiz", kicker="Vrai ou faux", title="Le bain de bouche *remplace le brossage* ?",
       options=["Vrai, si on le fait bien", "Faux, c'est un complément"], answer=1,
       note="Il ne retire pas la plaque. Et pas juste après le brossage : il rince le fluor."),
],
caption="""Vrai ou faux : un bain de bouche peut remplacer un passage de brosse à dents électrique ?

FAUX. Un bain de bouche ne retire pas la plaque, qui est un dépôt collant. Seul le frottement mécanique le fait.

Et le détail que presque personne ne connaît : si tu l'utilises juste après le brossage, tu rinces le fluor que le dentifrice vient de déposer.

Mieux : utilise-le à un autre moment de la journée, si ton dentiste te l'a conseillé.

[CTA]

#brosseadentselectrique #baindebouche #fluor #pulsecare"""),

# ───────────────────────── 20 · 30/11 · famille
dict(date="2026-11-30", kind="carousel", da="b", slides=[
  dict(tpl="hero", img="u:1758687126227-48c2fa04b653", kicker="En famille", title="Une routine qui tient *avec des enfants*", swipe=True),
  dict(tpl="steps", tone="fresh", kicker="4 astuces", title="Ce qui marche vraiment", items=[("Même heure chaque soir", "Juste après le pyjama."), ("Les parents en même temps", "Les enfants copient ce qu'ils voient."), ("Le minuteur devient un jeu", "Qui tient les 2 minutes ?"), ("Chacun sa tête", "Un repère de couleur par personne.")]),
],
caption="""Tenir une routine de brosse à dents électrique avec des enfants : 4 astuces qui marchent.

1. Même heure tous les soirs, juste après le pyjama
2. Les parents se brossent en même temps : les enfants copient ce qu'ils voient
3. Le minuteur de 2 minutes devient un défi
4. Chacun son repère pour ne pas mélanger les têtes

Pour les plus jeunes, demande à ton dentiste le type de brosse et le dosage de fluor adaptés à leur âge.

[CTA]

#brosseadentselectrique #routinefamille #parents #pulsecare"""),

# ───────────────────────── 21 · 01/12 · taches
dict(date="2026-12-01", kind="photo", da="a", tone="honey", slides=[
  dict(tpl="statement", img="u:1623400518712-640c747bd047", kicker="Taches de surface", title="Café, thé, vin :\n*le mode Blanchiment.*",
       sub="Il aide à retirer les taches de surface. Il ne change pas la couleur naturelle de la dent."),
],
caption="""Le mode Blanchiment d'une brosse à dents électrique, qu'est-ce qu'il fait exactement ?

Il augmente le rythme des vibrations pour aider à décrocher les taches de surface : café, thé, vin rouge, tabac.

Ce qu'il ne fait pas : changer la teinte naturelle de ton émail. Ça, c'est le travail d'un dentiste, avec un vrai protocole.

Le réflexe simple : un verre d'eau après le café, pour ne pas laisser le pigment s'installer.

[CTA]

#brosseadentselectrique #blanchiment #tachesdentaires #pulsecare"""),

# ───────────────────────── 22 · 02/12 · changement de tête
dict(date="2026-12-02", kind="photo", da="b", tone="sand", slides=[
  dict(tpl="product", img=s("tete_ricin2"), kicker="Têtes Pulse Care", title="Elle se change *en une seconde*", sub="Tu retires l'ancienne, tu enfonces la nouvelle. C'est tout."),
],
caption="""Changer la tête d'une brosse à dents électrique Pulse Care prend une seconde.

Tu tires l'ancienne vers le haut. Tu enfonces la nouvelle jusqu'au clic. Il n'y a pas de vis, pas de sens à chercher.

Les têtes sont en bambou, avec poils ricin ou nylon, et compatibles uniquement avec les manches Pulse Care.

Astuce : note la date du changement dans ton téléphone, ou prends l'abonnement pour ne plus y penser.

[CTA]

#brosseadentselectrique #tetederechange #brosseadentsbambou #pulsecare"""),

# ───────────────────────── 23 · 03/12 · émail
dict(date="2026-12-03", kind="carousel", da="c", slides=[
  dict(tpl="statement", img="u:1570840934347-4dc56c98b8ef", kicker="Idée reçue", title="Une brosse électrique *abîme l'émail* ?", swipe=True),
  dict(tpl="steps", kicker="Non, si tu l'utilises bien", title="Les 3 conditions", items=[("Tu n'appuies pas", "Les vibrations nettoient seules."), ("Mode Sensible au début", "1 à 2 semaines pour s'habituer."), ("Des poils souples", "Comme les têtes ricin ou nylon Pulse Care.")]),
],
caption="""Une brosse à dents électrique abîme-t-elle l'émail ? C'est la question qui revient le plus souvent.

Non, à trois conditions.

1. Tu n'appuies pas. La force est inutile : ce sont les vibrations qui nettoient.
2. Tu commences en mode Sensible, une à deux semaines, le temps de prendre le geste.
3. Tu utilises des poils souples.

Ce qui abîme l'émail, c'est la pression et les poils durs. Pas la technologie.

[CTA]

#brosseadentselectrique #email #ideerecue #pulsecare"""),

# ───────────────────────── 24 · 04/12 · coût par an
dict(date="2026-12-04", kind="photo", da="a", tone="mint", slides=[
  dict(tpl="stats", img=s("p012"), title="Ça coûte combien *par an* ?", items=[("59,90 €", "la Bamboo+, avec 2 têtes"), ("14,90 €", "le pack de 4 têtes"), ("4", "têtes par an, une tous les 3 mois"), ("1", "manche, gardé des années")]),
],
caption="""Une brosse à dents électrique, ça coûte combien par an ? Faisons le calcul pour la Bamboo+.

→ La brosse : 59,90 €, avec 2 têtes incluses. Le manche se garde des années.
→ Les têtes : 14,90 € le pack de 4, soit une année complète.

La première année, tu paies le manche. Les suivantes, ce sont uniquement les têtes.

C'est précisément le principe : le durable d'un côté, le consommable de l'autre.

[CTA]

#brosseadentselectrique #budget #tetederechange #pulsecare"""),

# ───────────────────────── 25 · 05/12 · bouche sèche
dict(date="2026-12-05", kind="photo", da="b", tone="forest", slides=[
  dict(tpl="bignum", kicker="Salive", big="1,5 L", title="de salive *par jour*", sub="C'est la première défense naturelle de la bouche. Elle neutralise les acides.", img="u:1521207418485-99c705420785"),
],
caption="""Entre deux passages de brosse à dents électrique, c'est la salive qui protège tes dents.

Un adulte en produit environ 1 à 1,5 litre par jour. Elle rince les résidus, neutralise les acides et apporte des minéraux à l'émail.

La nuit, la production chute. C'est pour ça que le brossage du soir compte autant, et qu'il vaut mieux ne rien manger après.

Si tu as souvent la bouche sèche, bois de l'eau régulièrement et parles-en à ton dentiste.

[CTA]

#brosseadentselectrique #salive #hygienebuccodentaire #pulsecare"""),

# ───────────────────────── 26 · 06/12 · sucre
dict(date="2026-12-06", kind="carousel", da="c", slides=[
  dict(tpl="hero", img="u:1499195333224-3ce974eecb47", kicker="Sucre", title="Ce n'est pas la quantité.\n*C'est la fréquence.*", swipe=True),
  dict(tpl="steps", kicker="3 réflexes", title="Limiter la casse", items=[("Mange le sucré d'un coup", "Plutôt qu'étalé sur la journée."), ("Un verre d'eau après", "Il rince les résidus."), ("Attends 30 min pour brosser", "Après quelque chose d'acide.")]),
],
caption="""Face au sucre, une brosse à dents électrique ne peut pas tout. Et le vrai problème n'est pas celui qu'on croit.

Ce n'est pas la quantité, c'est la fréquence. Chaque prise de sucre déclenche une attaque acide d'environ 20 minutes. Dix bonbons d'un coup : une attaque. Dix bonbons étalés sur la journée : dix attaques.

Trois réflexes :
→ regroupe le sucré en fin de repas
→ bois un verre d'eau après
→ attends 30 minutes avant de brosser si c'était acide

[CTA]

#brosseadentselectrique #sucre #carie #pulsecare"""),

# ───────────────────────── 27 · 07/12 · gencives qui reculent
dict(date="2026-12-07", kind="photo", da="a", tone="sand", slides=[
  dict(tpl="arch", img="u:1771442873038-dda05b6ca447", kicker="Gencives", title="Une gencive qui recule *ne revient pas.*",
       sub="D'où l'intérêt d'un brossage sans pression, dès maintenant."),
],
caption="""Un point que peu de gens savent sur le brossage, avec ou sans brosse à dents électrique : une gencive qui a reculé ne repousse pas.

Les deux causes principales : un brossage trop appuyé pendant des années, et la maladie parodontale.

Ce que ça provoque : la racine se découvre, la dent devient sensible au froid, et la zone retient plus de plaque.

La bonne nouvelle : on peut stopper le recul. Zéro pression, poils souples, et un suivi chez le dentiste.

[CTA]

#brosseadentselectrique #gencives #recessiongingivale #pulsecare"""),

# ───────────────────────── 28 · 08/12 · cadeau têtes
dict(date="2026-12-08", kind="photo", da="c", slides=[
  dict(tpl="arch", kicker="Idée cadeau", title="Le petit cadeau *qui fait plaisir*", sub="Un pack de 4 têtes en bambou, pour qui a déjà sa Pulse Care.", img=s("nylon_pack2_profil"), price="14,90 €"),
],
caption="""Pour quelqu'un qui a déjà sa brosse à dents électrique Pulse Care, le cadeau utile existe : un pack de têtes.

→ 4 têtes en bambou
→ poils ricin ou poils nylon
→ un an de brossage
→ 14,90 €

C'est le cadeau qu'on n'achète jamais pour soi et qui sert tous les jours. Parfait pour un petit budget ou un calendrier de l'avent.

[CTA]

#brosseadentselectrique #ideecadeau #tetederechange #pulsecare"""),

# ───────────────────────── 29 · 09/12 · 3 réflexes
dict(date="2026-12-09", kind="carousel", da="b", slides=[
  dict(tpl="arch", img=s("p002"), kicker="Les bases", title="3 réflexes *qui changent tout*", swipe=True),
  dict(tpl="steps", tone="fresh", kicker="À garder", title="Le minimum qui marche", items=[("2 minutes, 2 fois par jour", "Le minuteur s'en occupe."), ("Zéro pression", "Tu poses, tu guides, c'est tout."), ("Une tête tous les 3 mois", "Même si elle a l'air propre.")]),
],
caption="""Si tu ne devais retenir que 3 choses sur la brosse à dents électrique, ce serait celles-là.

1. 2 minutes, 2 fois par jour. Le minuteur s'arrête seul, tu n'as pas à compter.
2. Zéro pression. Tu poses la tête, tu guides, les vibrations font le reste.
3. Une tête tous les 3 mois, même si elle paraît en bon état.

Le reste (modes, accessoires, astuces) vient après. Ces trois-là font 90 % du résultat.

[CTA]

""" + TAGS),

# ───────────────────────── 30 · 10/12 · récap du mois
dict(date="2026-12-10", kind="carousel", da="a", slides=[
  dict(tpl="hero", img="u:1545803928-04e3f4cdd4ed", kicker="Le récap du mois", title="5 choses *à garder en tête*", swipe=True),
  dict(tpl="list", tone="mint", img=s("p005"), title="À retenir", numbered=True, items=[("Brosse avant le petit-déj", "Ou 30 min après si c'était acide."), ("Zéro pression", "Les vibrations nettoient seules."), ("Fil ou brossettes chaque soir", "40 % des surfaces sont entre les dents."), ("Tête tous les 3 mois", "Et après une angine."), ("Un contrôle par an", "Le tartre, seul un pro l'enlève.")]),
],
caption="""Le récap du mois sur la brosse à dents électrique, en 5 points.

1. Brosse avant le petit-déjeuner, ou 30 minutes après s'il y avait du jus ou du café
2. Zéro pression : ce sont les vibrations qui nettoient
3. Fil ou brossettes chaque soir : 40 % des surfaces sont entre les dents
4. Une tête tous les 3 mois, et après une angine
5. Un contrôle chez le dentiste par an

Enregistre ce post, il résume tout le mois.

[CTA]

""" + TAGS),
]
