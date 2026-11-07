# Validation : du code à une preuve de lab

## Ce que les tests locaux prouvent

`python3 -m unittest discover -s tests -v` vérifie le traitement de vrais formats XML sur des **fixtures synthétiques** : namespace Windows, UTF-16 avec BOM, comptes sujet/cible, champs répétés, entrées invalides et rejet des DTD. Il vérifie aussi le catalogue, les liens locaux, le XML Sysmon et le comportement déclaratif du workflow de triage.

Ces tests ne compilent pas SPL/KQL, ne valident pas l'import dans Logic Apps et ne prouvent pas qu'une attaque déclenche une alerte. PowerShell doit être vérifié sous Windows avant emploi. Aucun taux de détection ou temps de réponse n'est mesuré ici.

## Critère d'acceptation de chaque détection

Pour chaque entrée du catalogue :

1. Identifier le canal, le fournisseur, l'hôte et la politique d'audit qui génèrent l'événement.
2. Vérifier l'ingestion puis les champs nécessaires sur un événement brut.
3. Exécuter la recherche sans erreur dans le SIEM avec l'index et la fenêtre du lab.
4. Réaliser un test contrôlé sur une identité ou une machine de lab ; noter l'heure UTC.
5. Conserver un résultat positif et un cas bénin / négatif avec la même requête.
6. Qualifier les faux positifs et le résultat réellement observé, même s'il est nul.
7. Ajouter une capture expurgée et un extrait minimal dans une fiche de preuve.

Les SPL ont une recherche interactive de 15 minutes et certaines agrégations de 5 minutes. Pour une alerte planifiée, commencer par une exécution toutes les 5 minutes avec un lookback de 15 minutes pour le retard d'ingestion, puis dédupliquer/supprimer les doublons par règle, compte, hôte et fenêtre. Ne pas programmer les rapports de baseline comme des alertes. Tester le comportement selon la licence Splunk.

## Parcours initial à faible impact

**Baseline** : se connecter normalement au lab, attendre la collecte puis relever la répartition 4624/4768/4769. Ne pas fixer un volume « normal » à partir d'un exemple théorique.

**Échec d'authentification** : relever d'abord le seuil de verrouillage du compte de test. Produire manuellement quelques échecs bornés sans approcher ce seuil, puis une connexion valide. Le seuil de recherche de lab est trois échecs pour le même compte dans cinq minutes ; si le verrouillage est plus strict, abaisser temporairement le seuil de recherche, pas la protection du domaine. Ne pas lancer de boucle de mots de passe.

**RDP** : utiliser une session RDP autorisée vers WS1 si son édition et sa configuration le permettent. Attendre 4624 type 10 sur la destination ; une connexion locale de type 2 ne doit pas apparaître dans cette recherche.

**Tâches/services/groupes** : examiner d'abord les événements d'administration existants. Toute création de tâche ou de service de test doit avoir un nom distinct, une action inoffensive et une suppression documentée. Un signal sur une action bénigne n'est pas un faux négatif : la règle peut être volontairement une recherche de triage.

**Kerberos et accès sensibles** : utiliser les comptes de test du lab et les procédures approuvées. Les fixtures ne remplacent pas les événements du DC. Pas de collecte de mots de passe, dumps LSASS/NTDS ou affaiblissement de Defender dans ce dépôt. Les scénarios avancés nécessitent leurs prérequis et un retour arrière, puis leurs propres preuves.

## Export local

```powershell
.\scripts\Export-LabEvents.ps1 -LogName Security -LastMinutes 15 -MaxEvents 500 -OutputPath .\artifacts\security-run01.xml
```

Le script refuse d'écraser un fichier existant. `MaxEvents` est une borne, pas une promesse de couverture exhaustive. L'export brut peut contenir des noms, IP et identifiants de sécurité. Le conserver localement ; anonymiser une copie destinée à GitHub.

```bash
python3 scripts/normalize_events.py artifacts/security-run01.xml --output artifacts/security-run01.json
```

## Démo de 60 à 90 secondes après validation

Montrer l'architecture, l'horloge UTC, une action de test autorisée, l'événement reçu, la recherche et son résultat, puis une phrase sur les faux positifs. Présenter Azure comme extension prévue tant que le tenant et les connecteurs ne sont pas validés. Ne pas utiliser un graphe d'attaque illustratif comme preuve d'un chemin réellement exploitable.
