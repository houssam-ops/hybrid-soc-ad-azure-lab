# Durcissement et enseignements

## Réduire le risque sans perdre la télémétrie

- Séparer les comptes d'administration et les comptes utilisés pour les essais ; limiter les privilèges des services et de la synchronisation.
- Maintenir les systèmes à jour et vérifier le support de chaque OS et produit. Préserver Defender et les protections d'identifiants ; évaluer Credential Guard selon l'édition et le matériel.
- Inventorier les comptes avec préauthentification désactivée, les SPN et les dépendances RC4. Corriger après vérification de compatibilité, sans activer de faiblesse uniquement pour obtenir une alerte.
- Auditer les droits de réplication et la délégation Kerberos, surtout les comptes non-DC. Ne pas exclure globalement les comptes techniques de la surveillance.
- Contrôler les groupes privilégiés, les chemins de service, les tâches planifiées et l'accès RDP. Appliquer la segmentation du réseau de lab.
- Côté cloud : MFA, rôles minimaux, PIM lorsque disponible, revue des service principals et de leurs credentials, journalisation des changements de permissions.
- Enrichir les signaux par une baseline, le contexte des changements et l'identité de l'opérateur avant un confinement.

## Corrections apportées au scénario initial

**Collecte Windows.** Un canal Windows n'est pas un chemin de fichier à surveiller avec `add monitor`. Utiliser des stanzas `WinEventLog://...`, confirmer la configuration effective et éviter la double collecte.

**Rôles serveur et client.** `Install-WindowsFeature` vise Windows Server. L'activation IIS sur Windows client relève de ses fonctionnalités optionnelles et de l'édition installée. NPS requiert un rôle serveur et une configuration RADIUS réelle ; aucune stratégie « accepter tout » n'est nécessaire. IIS/NPS sont des extensions hors du socle à deux VM, pas des composants supposés actifs.

**Authentifications.** Un test SMB ne démontre pas un accès initial IIS ou NPS. Il faut relier la simulation au canal réellement généré. Un `runas /netonly` ne prouve pas à lui seul une extraction AS-REP : observer la requête, le succès et la préauthentification dans 4768.

**Kerberoasting.** Une demande de ticket ne force pas nécessairement RC4 : le résultat dépend des clés et capacités du service. Le signal 0x17 justifie une revue mais n'est pas une preuve de ticket cassé. La règle étroite RC4 ne couvre pas toutes les formes de Kerberoasting.

**DCSync et NTDS.** 4662 dépend de la SACL, des droits de contrôle et de l'audit. Une ligne de commande `ntdsutil` ou `vssadmin` est un indice à contextualiser. Event 8222 n'est pas un substitut générique à Sysmon ProcessCreate.

**Mouvement latéral.** Grouper par timestamp exact rend une détection multi-hôtes fragile. Le pack utilise des fenêtres de cinq minutes ; RDP produit un signal exploitable avec une seule destination dans ce petit lab.

**Frontière hybride.** Répliquer des secrets AD n'attribue pas automatiquement Global Administrator dans Entra. Une image d'architecture n'est ni un chemin BloodHound observé ni une preuve d'accès cloud. Le privilège Owner sur des ressources Azure est distinct d'un rôle annuaire Entra.

**Réponse.** Le compte cible d'un changement de rôle n'est pas nécessairement son initiateur. Un playbook qui désactive la mauvaise entité peut interrompre un service légitime ; la première version reste un workflow de triage.

## Ce qu'il reste à mesurer

Ingestion réelle par hôte/canal, qualité des extractions FR/XML, retard d'ingestion, faux positifs par règle, déduplication des alertes, import du workflow et coûts cloud. Aucun chiffre de ces catégories n'est publié sans expérience et preuve associées.
