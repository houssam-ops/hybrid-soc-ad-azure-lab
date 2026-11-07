# Extension Azure / Entra ID — à déployer et valider

Aucun abonnement, tenant, connecteur ou rôle cloud n'a été vérifié dans cette version du dépôt. Cette partie est une procédure de mise en place et quatre recherches prêtes à adapter, pas un compte rendu de déploiement.

## Conditions avant de créer des ressources

Utiliser un tenant de test, vérifier les licences des journaux et estimer le coût Log Analytics, Sentinel et Logic Apps. D'après le [connecteur Microsoft](https://learn.microsoft.com/en-us/azure/sentinel/connect-azure-active-directory), les journaux de connexion nécessitent les licences Entra adaptées ; un crédit Azure Students ne remplace pas automatiquement ces licences.

Créer un groupe de ressources dédié avec des tags de propriétaire et de date de fin. Configurer un budget et des alertes, la rétention, et les limites d'ingestion adaptées. Un [budget Azure](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets) ne stoppe pas les ressources. Ne pas présenter un daily cap comme une garantie de coût nul.

## Synchronisation hybride

Vérifier les [prérequis Entra Connect](https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-install-prerequisites) et choisir une topologie supportée. Préférer un serveur Windows dédié plutôt que d'ajouter la synchronisation et le SIEM au contrôleur de domaine. Le rôle d'installation et les comptes de service ont des fonctions différentes ; utiliser les droits documentés et limiter les OU synchronisées aux objets de test.

Une synchronisation de comptes ne démontre pas un chemin Domain Admin → Global Administrator. Les droits de réplication AD, les rôles Entra, Azure RBAC et les permissions Graph doivent être examinés séparément. Aucune compromission du vrai compte de synchronisation n'est nécessaire pour démontrer les recherches.

## Connecter les bonnes sources

1. Créer le workspace et activer Sentinel selon les écrans et prérequis Microsoft actuels.
2. Installer/configurer le connecteur Entra et sélectionner les catégories nécessaires.
3. Vérifier `SigninLogs` pour les utilisateurs, `AADServicePrincipalSignInLogs` pour les applications et `AuditLogs` pour les changements d'annuaire.
4. Connecter séparément **Azure Activity** pour les attributions de rôles sur les ressources.
5. Vérifier heure, compteurs, droits de lecture et délai d'ingestion sur chaque table avant d'utiliser les recherches.

Les valeurs `MonitoredUsers` et `MonitoredServicePrincipals` des KQL sont vides volontairement. Les renseigner dans le tenant avec des UPN de test en minuscules ou des **object IDs de service principals**, pas des client IDs. Conserver la configuration réelle hors du dépôt public.

`entra-role-assignment.kql` observe les modifications de rôles d'annuaire. `azure-rbac-changes.kql` observe les écritures de role assignments et conserve `Properties_d` pour résoudre rôle et cible. Une attribution Reader n'est pas assimilée à Owner. `service-principal-signins.kql` ne cherche pas les applications dans la table des connexions humaines.

## Valider et répondre

Produire une connexion autorisée avec un compte de test puis une activité d'administration à faible privilège dans un périmètre de test. Conserver résultat positif/négatif, corrélation et contexte. Ne pas créer un service principal Owner sur tout l'abonnement pour obtenir une capture.

La [procédure de triage](../playbooks/README.md) et son workflow manuel peuvent ensuite être testés séparément. Le raccordement à Sentinel exige un déclencheur et les permissions documentés ; le modèle HTTP livré n'est pas présenté comme déjà branché à une automation rule.

## BloodHound et fin du lab

Collecter seulement le périmètre autorisé avec les versions compatibles et vérifier les chemins proposés. Les exports d'annuaire et les informations de relations restent privés. Une image publique doit indiquer date, périmètre, anonymisation et si le chemin est simplement possible ou effectivement démontré.

À la fin, inventorier les ressources portant les tags du lab, exporter les preuves et demander une suppression ciblée après revue des dépendances. Ne pas lancer une suppression globale depuis ce guide. Les données de facturation peuvent arriver avec retard : vérifier les coûts résiduels plutôt qu'annoncer « facturation à zéro ».
