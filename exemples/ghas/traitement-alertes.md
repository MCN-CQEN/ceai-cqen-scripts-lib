# Consulter et traiter les alertes GHAS

## Perimetre et acces

Utiliser le fork cible, pas la bibliotheque ni le depot source. La bibliotheque
centralise les workflows ; les resultats des analyses sont associes au depot
appelant. L'acces aux vues depend des permissions de securite du compte.

Dans le depot, ouvrir `Security` (ou `Security and quality` selon l'interface).
Consulter `Code scanning`, `Secret scanning` et `Dependabot alerts`. Les jobs et
les erreurs de configuration se consultent dans `Actions` et les `Checks` des PR.

## Triage commun

1. Relever l'URL de l'alerte, la regle ou l'avis GHSA, la severite, la branche,
   le fichier, le commit et l'analyse associee. Ne jamais copier une valeur
   de secret dans un ticket, une capture ou un journal partage.
2. Verifier la pertinence pour le projet et attribuer un responsable. Prioriser
   les secrets actifs et les risques critiques/eleves selon le contexte.
3. Ouvrir un suivi avec le responsable, la correction prevue et une echeance
   validee par l'equipe. Ce guide ne definit pas de delai contractuel.
4. Corriger par PR, verifier les controles et conserver les preuves avant/apres.
5. Verifier l'etat sur la branche concernee apres la nouvelle analyse. Documenter
   toute acceptation de risque ou tout faux positif avec une justification.

## Code scanning

Ouvrir l'alerte, lire la regle et les emplacements, puis corriger le code ou le
workflow. Pour une reference d'action mutable, choisir un SHA complet verifie
et organiser sa maintenance. Ne pas simplement masquer le resultat.

Relancer l'analyse et verifier l'instance sur la bonne branche : la vue est
generalement filtree sur la branche par defaut. Une correction sur une branche
de test ne prouve pas que `dev` est corrigee. Un job CodeQL reussi signifie que
l'analyse et l'envoi ont reussi, pas qu'aucune alerte n'existe.

## Secret scanning et Push Protection

Pour un vrai secret expose, le considerer compromis. Coordonner sa revocation
ou rotation avec le proprietaire du service, actualiser les consommateurs et
examiner les acces suspects. Retirer le secret des fichiers ; une suppression
dans un nouveau commit ne le retire pas de l'historique. Evaluer une purge
coordonnee si necessaire, sans reecrire l'historique arbitrairement.

Une fois le traitement effectue, utiliser `Close as` avec le motif approprie et
une justification. Le retrait du fichier ne ferme pas automatiquement l'alerte.
`Used in tests` est reserve aux valeurs effectivement fictives de nos tests ;
ce n'est pas un motif pour ignorer un vrai secret.

Un push refuse ne doit pas etre contourne pour produire une preuve. Retirer la
valeur des commits a envoyer et reutiliser les protections existantes.

## Dependabot et Dependency Review

Dependabot alerts : lire l'avis, la version affectee et le manifeste. Examiner
la correction proposee, sa compatibilite, les notes de version et les tests.
Verifier ensuite la disparition du risque sur la branche par defaut. Une absence
d'alerte ne prouve pas l'absence de vulnerabilites hors de la couverture reconnue.

Dependency Review : examiner le job de la PR qui compare les dependances
introduites. Si le seuil de severite est depasse, corriger ou retirer l'ajout et
attendre le nouveau resultat. Cela ne constitue pas un inventaire complet des
vulnerabilites deja presentes et ne cree pas necessairement une alerte Dependabot.

Dependabot version updates : consulter `Insights > Dependency graph > Dependabot`
et les journaux des mises a jour. Une proposition de version n'est pas
necessairement une correction de securite. Une limite de PR atteinte se traite
par revue des propositions existantes, pas par une fusion aveugle. Un fork
necessite une activation explicite des mises a jour de versions.

## Controles obligatoires et audit

Les analyses automatiques ne rendent pas une fusion impossible a elles seules.
Configurer et tester separement une protection de branche ou un ruleset avec les
controles reellement executes. Ne pas rendre obligatoires les anciens jobs
ignores, ni des noms qui ne seront jamais publies sur les PR ciblees.

Pour bloquer selon de nouvelles alertes CodeQL, evaluer aussi les regles de
resultats code scanning adaptees au plan et a la politique de l'organisation :
le seul succes technique du job d'analyse n'est pas un seuil de vulnerabilite.
La protection des branches et son effet de blocage ne sont pas valides par les
tests du pilote actuel.

Conserver les liens de PR, runs et alertes, leurs commits et conclusions, sans
secrets. Les journaux GitHub ayant une retention limitee, conserver les extraits
utiles selon les regles internes. La bibliotheque est publique : faire approuver
la publication des metadonnees des forks prives et utiliser un espace prive si
ces informations sont confidentielles.

## References

- [Examiner les alertes Code scanning](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/assess-alerts)
- [Traiter les alertes Secret scanning](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-secret-scanning-alerts/resolving-alerts)
- [Erreurs Dependabot et limites de PR](https://docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-errors)
