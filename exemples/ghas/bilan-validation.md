# Bilan de validation GHAS

> Mise a jour du 2026-11-05 : ce bilan decrit le pilote historique base sur les
> workflows reutilisables. Le kit a ete migre localement vers des actions composites
> sous `actions/`. Les tests GitHub de cette nouvelle integration restent a faire ;
> voir [migration et plan de test](./migration-actions.md). Les preuves ci-dessous
> ne doivent pas etre presentees comme une validation distante de la migration.

Etat du pilote au 2026-11-03. Cible :
`MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`, branche par defaut `dev`.
Ce bilan ne vaut pas activation sur le depot source ni validation de tous les
depots de l'organisation.

## Criteres d'acceptation

| Critere | Etat dans le pilote | Preuve ou reserve |
| --- | --- | --- |
| GHAS active et configure | Valide sur le fork | Code Security, Secret scanning et Push Protection constates actifs ; analyses et alertes obtenues |
| Analyse CodeQL reussie | Valide : Actions et Python | [Detection et correction Actions](./preuves/codeql-controlled-test.md) ; Python execute, pas de vulnerabilite Python controlee |
| Secret scanning fonctionnel | Valide pour le motif fictif | [Alerte 1 et refus GH013](./preuves/secret-scanning-controlled-test.md) ; alerte cloturee, fichier retire |
| Controles de dependances | Valide sur PR et propositions de versions | [Dependency Review](./preuves/dependency-review-controlled-test.md), [Dependabot](./preuves/dependabot-validation.md) |
| Execution automatique en developpement | Valide sur PR | PR de test et PR Dependabot ; le declenchement planifie est configure mais pas prouve par un run planifie dans ces fiches |
| Problemes consultables | Valide CodeQL et Secret scanning | Alertes GitHub conservees ; vulnerabilites de dependances visibles dans les Checks de la PR 1, pas de preuve controlee d'alerte Dependabot |
| Probleme controle detecte | Valide | Reference mutable, valeur fictive et requests 2.19.1 ; correction/nettoyage verifies |
| Configuration et traitement documentes | Redige, a relire et publier | README, preparation multi-depot, fiches de preuve et [procedure](./traitement-alertes.md) |

## Ce que le pilote demontre

Les workflows reutilisables centralisent CodeQL et Dependency Review. Le fork
porte les reglages de securite et les alertes. L'application GitHub permet une
preparation ciblee, avec activation, variables et fichiers sur demande explicite.
Le depot source n'est pas la cible de ces operations.

Les PR de configuration Dependabot (2) et GitFlow (11) sont fusionnees dans le
fork. La PR Dependabot 9 reste ouverte lors de la verification, ses controles
centralises et GitFlow reussissent. La fusion de cette mise a jour n'est pas un
critere de reussite du test.

## Restes et limites

1. Revoir et publier la documentation dans la branche de travail de la
   bibliotheque selon le processus de PR habituel. Aucun commit ni push de cette
   documentation n'a ete realise par l'agent pendant sa redaction.
2. Le 2026-11-04, le pilote local a ete remis en inspection sur le deuxieme fork :
   `enable_security: false`, `configure_variables: false`, `files_mode: preview`.
   Le retour en inspection a ete publie et constate dans le resume fourni par
   l'utilisateur. Le pilote temporaire est maintenant retire localement au
   profit du lancement manuel apres integration ; ce retrait reste a publier.
3. Stabiliser les references de workflows par SHA et traiter les alertes
   preexistantes de references mutables. L'exemple manuel a ete fige localement
   le 2026-11-04 au SHA publie `221333ee22916ac85d18c6d3c604d02339e9b6cd`.
   Le generateur produit deja des SHA. Cette modification de l'exemple ne met
   pas a jour les appels sur `feature/ghas-toolkit` du fork cluster existant.
4. Revoir les anciens workflows ignores et les workflows d'infrastructure
   herites. Leur absence d'execution AWS n'est pas garantie par le kit.
5. Si le blocage avant fusion est exige, configurer et tester les protections
   de branche/rulesets ; elles ne sont pas mises en place par cette documentation.
6. La preparation de fichiers sur un autre fork est validee, mais son activation
   et ses analyses restent bloquees par le verrou de facturation constate le
   2026-10-29 : voir [preuve multi-depot](./preuves/preparation-projects.md).
7. Les projets compiles, registres prives et manifestes non reconnus exigent des
   profils supplementaires. Un fork manuel ne garantit pas une seule licence.
8. Les reglages Dependabot ont ete confirmes par l'utilisateur et des PR de
   versions existent ; une alerte Dependabot controlee et son cycle de correction
   n'ont pas ete testes. Terraform est suivi pour les mises a jour, pas analyse
   par CodeQL comme un langage pris en charge.

## Suite proposee

Relire ces preuves et limites avec le responsable de la tache, puis decider si
la livraison attendue est le pilote sur fork ou le deploiement generalise.
Ne pas annoncer la tache initiale terminee sur le depot source : l'utilisateur
a choisi de garder l'activation dans les forks uniquement.
