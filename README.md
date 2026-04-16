# Panneau Solaire
Projet vise à proposer panneau solaire + batterie pour les clients

## Remarque:
  -materiel:
   -puissance panneau (40%)
   -puissance batterie (50%)
  
  -usage:
   -consommation 24H
   -6h-17h:consommation panneau solaire(puissance:40% recharge batterie incluse pendant l'usage panneau )
   -17h-19h:consommation panneau (puissance:20% recharge batterie incluse pendant l'usage panneau)
   -19h-6h:consommation batterie
  
  -format appareil demande:
    -appareil : (heure de debut, heure de fin, puissance)
    -exemple: (6, 19, 100) => appareil consomme 100W de 6h à 19h

## Objectif:
    -faire une proposition de panneau solaire et batterie pour les clients
    
# Code structure:
    -dossier models :
        -appareil.py : classe appareil


    -dossier utils:
        -CalculFonction.py : classe calcul fonction(estimation de la puissance necessaire grace au appareil fournis par le client avec charge de la batterie en journée incluse)
        -Databaseconnection.py : classe pour la connexion à la base de données(mysql locahost:3306 pour le moment)
       
    -dossier data :(mysql locahost:3306 pour le moment)
        -init.sql : tableau de base de données pour les appareils
        -data.sql : données d'exemple pour les appareils

    -dossier GUI:
        -main.py : interface graphique pour l'utilisateur
        -tableau.py : classe pour afficher les résultats dans un tableau(panneau solaire et batterie proposés)
        -liste_appareil.py : classe pour afficher la liste des appareils fournis par le client(option ajout et supprimer aussi)