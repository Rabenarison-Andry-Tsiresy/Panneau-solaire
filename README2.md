# README2 - Formules Simples De Calcul

Ce document explique la logique avec les formules de base de l'electricite.

Formule principale:
- E = P * t

Ou:
- E en Wh
- P en W
- t en heures

## 1. Regle simple d'utilisation

- 06:00 -> 17:00: panneau a 40%
- 17:00 -> 19:00: panneau a 20%
- 19:00 -> 06:00: batterie

Interpretation metier:
- Le matin/jour, le panneau alimente les appareils connectes.
- En meme temps, le panneau recharge la batterie pour la nuit.

## 2. Energies calculees

- E6_17: energie des appareils entre 06:00 et 17:00
- E17_19: energie des appareils entre 17:00 et 19:00
- Ebatt_nuit: energie des appareils entre 19:00 et 06:00

Consommation totale:
- E24 = E6_17 + E17_19 + Ebatt_nuit

## 3. Puissance panneau recommandee

Le panneau doit:
- tenir le pic de charge instantane
- produire assez d'energie pour le jour + la recharge batterie

Contrainte pic:
- Ppv_pic = max(Pic6_17 / 0.40, Pic17_19 / 0.20)

Contrainte energie:
- Heures solaires equivalentes:
- H_eq = 11*0.40 + 2*0.20 = 4.8 h

- Energie a fournir par panneau:
- E_pv = E6_17 + E17_19 + Ebatt_nuit

- Puissance mini par energie:
- Ppv_energie = E_pv / H_eq

Nouveau mecanisme (recharge continue en journee):
- Puissance moyenne de recharge batterie:
- P_recharge = Ebatt_nuit / t_recharge

Avec ce mecanisme, la contrainte de pic devient:
- Ppv_pic = max((Pic6_17 + P_recharge)/0.40, (Pic17_19 + P_recharge)/0.20)

Ou:
- t_recharge = duree de recharge batterie pendant la journee
- Par defaut: t_recharge = duree(06:00->19:00) = 13h

Proposition panneau:
- Ppv_reco = max(Ppv_pic, Ppv_energie)

## 4. Capacite batterie recommandee

La batterie alimente la nuit (19:00 -> 06:00):
- Ebatt_nuit

On considere 50% utilisable:
- Cbatt_nominale = Ebatt_nuit / 0.50

Puis on ajoute +50% pour la proposition:
- Cbatt_reco = Cbatt_nominale * 1.50
- Cbatt_reco = Ebatt_nuit * 3

## 5. Modele de configuration (nouveau)

Pour faciliter les changements, tous les parametres sont centralises dans:
- models/configuration.py

Classe:
- ConfigurationCalcul

Parametres modifiables:
- Horaires des plages (HH:MM:SS)
- Facteur panneau fort/faible
- Fraction batterie utilisable
- Marge proposition batterie
- recharge_continue_en_journee (active le nouveau mecanisme)
- duree_recharge_batterie_heures (optionnel, pour forcer un t_recharge)

Exemple d'utilisation:

```python
from models.configuration import ConfigurationCalcul
from utils.CalculFonction import CalculFonction

config = ConfigurationCalcul(
	panneau_fort_debut_hms="06:00:00",
	panneau_fort_fin_hms="17:00:00",
	panneau_faible_debut_hms="17:00:00",
	panneau_faible_fin_hms="19:00:00",
	batterie_debut_hms="19:00:00",
	batterie_fin_hms="06:00:00",
	facteur_panneau_fort=0.40,
	facteur_panneau_faible=0.20,
	fraction_batterie_utilisable=0.50,
	marge_proposition_batterie=1.50,
	recharge_continue_en_journee=True,
	duree_recharge_batterie_heures=0.0,
)

calculateur = CalculFonction(configuration=config)
```

## 6. Sorties finales

- consommation_24h_wh
- puissance_panneau_recommandee_w
- capacite_batterie_recommandee_wh
