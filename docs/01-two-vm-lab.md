# Déployer le socle avec deux VM

## 1. Inventorier avant de modifier

Périmètre confirmé par le propriétaire : une VM Windows Server et WS1 sous VirtualBox. Les fichiers VirtualBox indiquent un type invité Windows Server 2022 et Windows 10 pour WS1 ; cela ne confirme pas la version réellement installée, son support, son démarrage ou les rôles actifs.

Lancer `scripts/Get-LabReadiness.ps1` sur chaque VM. Relever localement : OS/build, appartenance au domaine, services NTDS/DNS/Splunk/Sysmon et état des trois canaux d'événements. La commande ne modifie pas la machine. Ne pas contourner une politique de scripts d'entreprise ; lire le script et le lancer uniquement selon les règles de son lab.

L'accès VirtualBox depuis l'environnement de préparation du dépôt n'a pas permis de lancer une validation invitée. Les noms et états doivent donc être confirmés dans VirtualBox sur l'hôte. Une erreur d'IPC ou un pilote VirtualBox absent doit être traitée avant le test réseau, pas interprétée comme un échec Splunk.

## 2. Topologie proposée

- **Windows Server / DC1** : AD DS + DNS, audit Security/System, Universal Forwarder ; Sysmon si installé et validé.
- **WS1** : poste joint au domaine, station de test et, seulement si son OS est compatible, instance Splunk de lab. Ce cumul simplifie un lab de deux VM mais n'est pas une architecture SOC de production.
- **Extension recommandée** : un collecteur Splunk dédié sur un OS supporté et, pour la synchronisation, un serveur Windows dédié. Ces machines ne sont pas déclarées déployées.

Utiliser un réseau interne/host-only isolé pour le trafic du lab. Si un accès de mise à jour est nécessaire, ajouter temporairement une sortie NAT contrôlée. Ne pas exposer AD, RDP, Splunk Web ou le port de réception sur Internet. Faire un snapshot avant les changements de configuration.

Exemples à adapter, pas des valeurs découvertes : DC1 `192.168.56.10`, WS1 `192.168.56.20`, domaine `lab.test`. Si le domaine existe déjà, le conserver ; ne pas recréer la forêt. Utiliser le DNS AD sur WS1 et vérifier la synchronisation horaire. Une adresse DNS publique sur le client peut empêcher la découverte du domaine.

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Name,Domain,PartOfDomain
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.lab.test
w32tm /query /status
```

## 3. Installer et vérifier la collecte

Télécharger Splunk et son Universal Forwarder depuis l'éditeur. Vérifier la matrice OS et la licence choisie : disponibilité de la recherche, des alertes et quotas ne doivent pas être supposés identiques entre éditions.

Sur le récepteur Splunk :

1. Installer le Splunk Add-on for Microsoft Windows et vérifier ses instructions de placement.
2. Créer une app locale `soc_lab` sous `$SPLUNK_HOME/etc/apps/`, puis son dossier `local/`.
3. Examiner et fusionner `configs/splunk/server/indexes.conf` et `inputs.conf` dans cette app. L'index `ad_lab` conserve au plus sept jours, avec une borne de taille d'environ 2 Go ; ajuster au disque disponible.
4. Autoriser TCP/9997 uniquement depuis les adresses du lab. Le modèle livré utilise TCP sans TLS pour un réseau isolé ; hors de ce périmètre, configurer TLS et valider les certificats.
5. Redémarrer Splunk après revue de la configuration effective.

Sur le DC, placer les stanzas de `configs/splunk/forwarder/inputs.conf` dans l'app locale d'un Universal Forwarder. Copier `outputs.conf.example` en `outputs.conf` dans cette app et remplacer l'adresse par celle du récepteur. Ne pas laisser de doublon Security/System dans une autre app.

Si Splunk Enterprise tourne sur WS1, lui faire collecter **ses propres** canaux avec les mêmes stanzas WinEventLog. Il n'est pas nécessaire d'installer aussi un forwarder sur WS1 pour relire les mêmes événements. Sinon, installer le forwarder sur WS1 et envoyer vers le collecteur dédié.

Contrôle de configuration, depuis le dossier `bin` du produit installé :

```powershell
.\splunk.exe btool inputs list --debug
.\splunk.exe btool outputs list --debug
```

Puis dans Splunk :

```spl
index=ad_lab earliest=-15m
| stats count latest(_time) as last_event by host source sourcetype
| convert ctime(last_event)
```

Attendu : le DC et WS1, les canaux attendus et des événements récents. Zéro résultat exige de vérifier le service, le réseau, le chemin des configurations et les droits de lecture du canal Security. Ne pas continuer vers les scénarios tant que la collecte est incomplète.

## 4. Audit Windows et Sysmon

Configurer l'audit avancé dans une GPO de lab ciblée, après snapshot : Logon succès/échec, Kerberos Authentication Service, Kerberos Service Ticket Operations, Security Group Management et Other Object Access Events. DCSync nécessite aussi Directory Service Access **et une SACL adaptée sur l'objet de domaine** ; activer seulement l'audit ne garantit pas 4662.

Pour les processus, le pack utilise Sysmon 1 et 10. Le modèle `configs/sysmon/lab.xml` collecte les créations de processus et les accès ciblant LSASS. Vérifier le schéma accepté par la version installée avec `sysmon64.exe -s`, puis revoir le modèle avant installation ou modification. L'acceptation de la licence Sysmon doit être faite par l'opérateur. Ne pas installer aveuglément une deuxième instance ni désactiver Defender.

```powershell
# Vérifications en lecture seule après installation approuvée
Get-Service Sysmon* -ErrorAction SilentlyContinue
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 5
```

## 5. Champs et passage des anciennes recherches

Les nouvelles recherches utilisent `index=ad_lab`. Si l'historique est dans `main`, remplacer explicitement l'index pour la recherche historique ou migrer la collecte ; ne pas interpréter un index vide comme une absence d'activité.

Les filtres reposent sur `EventCode` fourni par le TA Windows et les sources `WinEventLog:*` / `XmlWinEventLog:*`. Vérifier les valeurs réelles par la requête précédente. Les extractions `rex` de champs nommés visent le XML Windows standard ; valider les événements réels avant de programmer des alertes.

L'ancien champ français `Nom_du_compte` peut contenir le sujet puis la cible. Le repli sur sa dernière valeur est une compatibilité à vérifier, pas un contrat universel. Le XML `TargetUserName` est prioritaire. Pour 4662, utiliser le sujet de l'opération ; pour 4768/4769, le compte de la requête.
