# Réponse : triage avant confinement

`triage-workflow.json` est une **définition de workflow Logic Apps Consumption** à importer dans un workflow de lab. Ce n'est ni un déploiement ARM complet ni un export d'une exécution réussie. Son déclencheur est HTTP manuel, pas le connecteur Sentinel incident.

Le workflow accepte un identifiant d'incident et de règle, construit un dossier de revue et répond HTTP 202. Il **ne désactive aucun compte**, ne nécessite pas d'identifiants Graph et n'accorde aucun rôle. Le déploiement et le raccordement à une règle d'automatisation Sentinel restent à valider dans Azure. Garder l'URL de déclenchement secrète et utiliser les contrôles d'accès proposés par Azure.

Exemple de corps de requête de lab :

```json
{"incidentId":"SYNTHETIC-001","ruleName":"azure-rbac-changes"}
```

## Procédure analyste

1. Relever l'heure UTC, la règle, l'ID de corrélation et l'artefact brut.
2. Distinguer **acteur** (qui a fait l'action) et **cible** (qui reçoit un rôle / est modifié). Ne jamais désactiver aveuglément `TargetResources[0]`.
3. Confirmer le tenant de lab, la provenance du signal et l'absence de changement administratif approuvé.
4. Examiner les connexions et rôles ; vérifier l'impact sur la synchronisation avant toute action sur un compte technique.
5. Faire approuver une action ciblée sur une identité de test explicitement autorisée. Exclure les comptes d'urgence et les comptes de synchronisation réels.
6. Consigner l'action, le résultat et le retour arrière. Exporter uniquement une preuve expurgée.

Une future automatisation de confinement devra ajouter un déclencheur Sentinel authentifié, une véritable approbation externe au corps fourni par l'appelant, une allowlist d'identités de test, une identité managée à permissions minimales et un mécanisme de reprise. Aucune de ces capacités n'est revendiquée comme déployée ici.
