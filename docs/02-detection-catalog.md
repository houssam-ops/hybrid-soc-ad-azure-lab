# Catalogue des détections

Les requêtes sont à valider dans les moteurs SIEM ; les tests locaux ne sont pas des tests SPL/KQL. Les mappings ATT&CK représentent une hypothèse de comportement, pas une preuve de compromission.

## Modules

1. Monitoring : baseline des authentifications.
2. Accès initial : échecs de connexion ; IIS/NPS restent des extensions.
3. Credentials : Kerberos, LSASS, réplication et outils de copie AD.
4. Mouvement latéral : service PsExec et connexion RDP.
5. Post-exploitation : tâches, services et groupes privilégiés.
6. Cloud : identités et changements de rôles, à déployer.

## Baseline des authentifications

Fichier : [baseline-authentication](../detections/splunk/baseline-authentication.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Security collecté sur DC et WS1.

**Signal attendu :** Séries temporelles par événement, sans volume normal inventé.

**Faux positifs / limites :** Activité normale : cette recherche est un rapport, pas une alerte.

**ATT&CK :** Baseline, sans technique attribuée.

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Échecs répétés pour un compte

Fichier : [initial-access-bruteforce](../detections/splunk/initial-access-bruteforce.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Logon en échec; seuil de lab 3 échecs / 5 minutes.

**Signal attendu :** Une ligne par compte et fenêtre de cinq minutes; n’est pas une preuve de password spraying.

**Faux positifs / limites :** Mot de passe oublié, service avec mot de passe expiré.

**ATT&CK :** T1110

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Ticket de service RC4 à examiner

Fichier : [kerberoasting](../detections/splunk/kerberoasting.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Kerberos Service Ticket Operations sur DC; champ résultat vérifié.

**Signal attendu :** Une demande RC4 réussie suffit au triage dans ce petit lab; AES ne déclenche pas cette règle étroite.

**Faux positifs / limites :** Services hérités utilisant RC4; RC4 seul ne prouve pas le vol ou le cassage d’un ticket.

**ATT&CK :** T1558.003

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## TGT émis sans préauthentification

Fichier : [asrep-roasting](../detections/splunk/asrep-roasting.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Kerberos Authentication Service sur DC.

**Signal attendu :** TGT réussi sans préauth; ne pas exiger RC4.

**Faux positifs / limites :** Compte volontairement exempté de préauthentification; pas de preuve de cassage hors ligne.

**ATT&CK :** T1558.004

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Accès à LSASS à qualifier

Fichier : [lsass-access](../detections/splunk/lsass-access.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Sysmon ProcessAccess activé et canal collecté.

**Signal attendu :** Événement Sysmon 10 ciblant LSASS, avec processus source à investiguer.

**Faux positifs / limites :** Antivirus, EDR, outils système légitimes; accès ne signifie pas dump réussi.

**ATT&CK :** T1003.001

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Droits de réplication observés

Fichier : [dcsync](../detections/splunk/dcsync.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Directory Service Access; SACL adaptée sur la racine du domaine.

**Signal attendu :** Usage de droits de réplication à corréler avec le rôle du compte; pas de preuve autonome d’exfiltration.

**Faux positifs / limites :** Réplication normale des DC et comptes de synchronisation; établir une allowlist justifiée, ne pas exclure tous les comptes finissant par $.

**ATT&CK :** T1003.006

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Outils de copie AD à examiner

Fichier : [ntds-extraction](../detections/splunk/ntds-extraction.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Sysmon ProcessCreate avec ligne de commande.

**Signal attendu :** Processus et commande à qualifier; ne pas lire Event 8222 comme un journal de création de processus.

**Faux positifs / limites :** Sauvegardes et administration; création de shadow copy seule n’établit pas un vol NTDS.

**ATT&CK :** T1003.003

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Installation de service de type PsExec

Fichier : [lateral-smb-psexec](../detections/splunk/lateral-smb-psexec.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Canal System collecté; service nommé PSEXESVC pour ce signal précis.

**Signal attendu :** Installation suspecte à corréler avec 4624 type 3 et les événements SMB.

**Faux positifs / limites :** PsExec utilisé légitimement par un administrateur; noms personnalisés non couverts.

**ATT&CK :** T1021.002, T1569.002

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Connexion RDP réussie

Fichier : [lateral-rdp](../detections/splunk/lateral-rdp.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Logon en succès sur la destination.

**Signal attendu :** Connexion distante interactive observée; sans affirmer qu’elle est malveillante.

**Faux positifs / limites :** Administration RDP normale; ce petit lab ne nécessite pas plusieurs destinations.

**ATT&CK :** T1021.001

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Création de tâche planifiée

Fichier : [scheduled-task](../detections/splunk/scheduled-task.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Other Object Access Events en succès.

**Signal attendu :** Nouvelle tâche; examiner son XML et le compte créateur avant de conclure à une persistance.

**Faux positifs / limites :** Installation logicielle, maintenance.

**ATT&CK :** T1053.005

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Création de service

Fichier : [new-service](../detections/splunk/new-service.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Canal System collecté.

**Signal attendu :** Nouveau service avec image à vérifier; signal de triage générique.

**Faux positifs / limites :** Agent de sécurité ou installation approuvée.

**ATT&CK :** T1543.003

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Ajout au groupe Administrators local

Fichier : [local-admin-membership](../detections/splunk/local-admin-membership.spl) · Moteur : splunk · Statut : `lab-validation-pending`

**Prérequis :** Audit Security Group Management en succès sur WS1.

**Signal attendu :** Membre ajouté au groupe intégré; sur DC, vérifier la portée du groupe, pas de SAM locale classique.

**Faux positifs / limites :** Ajout administratif approuvé; le SID évite la dépendance Administrators/Administrateurs.

**ATT&CK :** T1098

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Connexions rapprochées de comptes techniques de test

Fichier : [anomalous-sync-signin](../detections/sentinel/anomalous-sync-signin.kql) · Moteur : sentinel · Statut : `cloud-deployment-pending`

**Prérequis :** Connecteur alimentant SigninLogs; licence et droits vérifiés ; Identifiants de lab configurés si liste Monitored présente.

**Signal attendu :** Résultat à valider dans le tenant; aucune exécution cloud revendiquée.

**Faux positifs / limites :** Automatisation habituelle; fréquence seule non suffisante.

**ATT&CK :** T1078.004

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Connexions de service principals surveillés

Fichier : [service-principal-signins](../detections/sentinel/service-principal-signins.kql) · Moteur : sentinel · Statut : `cloud-deployment-pending`

**Prérequis :** Connecteur alimentant AADServicePrincipalSignInLogs; licence et droits vérifiés ; Identifiants de lab configurés si liste Monitored présente.

**Signal attendu :** Résultat à valider dans le tenant; aucune exécution cloud revendiquée.

**Faux positifs / limites :** Déploiements et applications légitimes; tout succès est un signal de revue.

**ATT&CK :** T1078.004

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Modification de rôle annuaire Entra

Fichier : [entra-role-assignment](../detections/sentinel/entra-role-assignment.kql) · Moteur : sentinel · Statut : `cloud-deployment-pending`

**Prérequis :** Connecteur alimentant AuditLogs; licence et droits vérifiés ; Identifiants de lab configurés si liste Monitored présente.

**Signal attendu :** Résultat à valider dans le tenant; aucune exécution cloud revendiquée.

**Faux positifs / limites :** Attributions administratives ou activations PIM approuvées.

**ATT&CK :** T1098.003

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).

## Attribution de rôle sur une ressource Azure

Fichier : [azure-rbac-changes](../detections/sentinel/azure-rbac-changes.kql) · Moteur : sentinel · Statut : `cloud-deployment-pending`

**Prérequis :** Connecteur alimentant AzureActivity; licence et droits vérifiés ; Identifiants de lab configurés si liste Monitored présente.

**Signal attendu :** Résultat à valider dans le tenant; aucune exécution cloud revendiquée.

**Faux positifs / limites :** Déploiement autorisé; résoudre la définition du rôle avant de parler de privilège élevé.

**ATT&CK :** T1098.003

**Réponse :** vérifier la provenance, identifier acteur et cible, comparer à la baseline et appliquer la [procédure de triage](../playbooks/README.md). Conserver une [fiche de preuve](../evidence/TEMPLATE.md).
