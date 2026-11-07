# Registre des preuves

## Statut de cette version

- Deux VM ciblées : Windows Server et WS1 sous VirtualBox, déclarées par le propriétaire et repérées dans les fichiers de configuration de l'hôte.
- Trois recherches d'authentification préexistantes dans l'historique Git ; les commentaires historiques ne constituent pas des preuves d'exécution indépendantes.
- Validation locale réalisée : tests Python du normaliseur et contrôles statiques du dépôt. Rejouer la commande du README pour obtenir le résultat de cette version.
- Validation Splunk réelle : **en attente**, pour les 12 recherches du catalogue.
- Déploiement Entra/Sentinel et exécution KQL : **en attente**.
- Import/exécution du workflow Logic Apps : **en attente**.
- Graphe BloodHound/AzureHound et vidéo : **en attente**.

Aucun événement de `fixtures/` ne doit être transféré ici comme preuve réelle. Ne pas renommer un résultat de test local en résultat Splunk.

## Une fiche par expérience

Copier [TEMPLATE.md](TEMPLATE.md) pour chaque recherche, puis remplir les observations. Ne passer un statut à « validé en lab » que si la requête exacte, les données, le contrôle négatif et le résultat sont traçables. En cas de publication, relier une capture expurgée ; laisser les exports bruts dans `artifacts/`.

Les captures doivent montrer la recherche, la fenêtre temporelle et le résultat, sans mot de passe, token, URL de webhook signée ou données d'identités réelles. Expliquer toute anonymisation. Les IP et noms utilisés dans la documentation sont des exemples, pas des relevés de production.
