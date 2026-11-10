# Validation des actions composites GHAS

Verification des metadonnees GitHub par API le 2026-11-10.
Les [donnees JSON filtrees](./composite-actions-validation.json) conservent les
commits, liens, conclusions et sources des observations, sans credential.

## Perimetre

- Bibliotheque : `MCN-CQEN/ceai-cqen-scripts-lib`.
- Commit des actions teste : `8c108cedf0faa03e3ff6cf153ef1b62484a6d8c7`.
- Fork : `MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`, ID `1435756700`.
- Branche par defaut : `dev`.
- [PR de migration des appels 12](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/pull/12), ouverte et non fusionnee lors de la verification.

Les appels figurent dans les steps des jobs du fork, et non dans des appels de
jobs a des workflows reutilisables. Le fork garde ses evenements, runners,
permissions, matrice et checkout. La preparation s'execute depuis un workflow
d'administration avec un jeton App cible ; la cle PEM n'est pas transmise aux scans.

## CodeQL et Dependency Review

| Etape | Commit du fork | Execution | Resultat |
| --- | --- | --- | --- |
| Premiere execution composite | `c5fff2125f13ed19e1025f7bb4d6250937e40613` | [42104014913](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/42104014913) | CodeQL Actions/Python et Dependency Review : success |
| Dependance vulnerable ajoutee | `589b4be28c842e6fe17fa7ce8576259a9da49a43` | [42111852327](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/42111852327) | CodeQL : success ; Dependency Review : failure attendue |
| Retrait de la fixture sur la branche de test | `4d98c9ce1fa8a4311c46716886fbc02db692e5f5` | [42642946897](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/42642946897) | CodeQL Actions/Python et Dependency Review : success |

Le journal fourni par l'utilisateur confirme `requests@2.19.1` dans
`security-tests/dependency-review/requirements.txt`, avec cinq avis :
`GHSA-x84v-xcm2-53pg`, `GHSA-j8r2-6x86-q33q`, `GHSA-9wx4-h78v-vm56`,
`GHSA-9hjg-9r4m-mvj7`, `GHSA-gc5v-m9x4-r6x2`.
L'echec contient `Dependency review detected vulnerable packages.`
Le resultat n'est donc pas un simple echec technique.

Un controle vert de PR n'atteste pas l'absence de vulnerabilites deja presentes
dans la branche par defaut. Une verification separee avait trouve la fixture sur
`dev` ; la [PR de nettoyage 13](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/pull/13)
a ete fusionnee le 2026-11-09 a 16:32:56 UTC. L'absence du fichier sur dev a
ensuite ete verifiee par API avant installation de la proposition.

## Preparation composite

| Mode | Execution dans la bibliotheque | Resultat |
| --- | --- | --- |
| Preview | [42645562795](https://github.com/MCN-CQEN/ceai-cqen-scripts-lib/actions/runs/42645562795) | success, inspection et preview sans modification demandes |
| Install | [42887091191](https://github.com/MCN-CQEN/ceai-cqen-scripts-lib/actions/runs/42887091191) | success, branche de proposition creee |
| Variables | [42889724127](https://github.com/MCN-CQEN/ceai-cqen-scripts-lib/actions/runs/42889724127) | success, les deux valeurs true relues et verified |

Les resumes transmis par l'utilisateur montrent Code Security, Secret scanning
et Push Protection actives sur cette cible. Le preview emploie un jeton read-only.
Install emploie Contents/Workflows write, sans demande d'activation ; le test des
variables n'installe aucun fichier et ne demande aucune activation. Pour les
variables, create-github-app-token v2 herite des permissions de l'installation,
en restant limite au seul fork. Les valeurs enregistrees ont ete relues par API :
`CODEQL_ENABLED=true`, `DEPENDENCY_REVIEW_ENABLED=true`.

### Proposition inspectee

- Branche : `feature/ghas-setup-bbcbf3f66f20-8c108cedf0fa`.
- Commit : `da29b6219e441c8f70fab3683145791b4dcb3845`.
- Parent et dev lors de la verification : `bbcbf3f66f2025090e96d7f7204621c698f9bec3`.
- Un commit d'avance, aucun retard, un seul fichier modifie :
  `.github/workflows/ghas-security.yml`.
- [Comparaison inspectee](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/compare/dev...feature%2Fghas-setup-bbcbf3f66f20-8c108cedf0fa).

La proposition utilise des jobs locaux, une matrice Actions/Python et les deux
actions de scan au SHA teste. Les evenements PR, push vers dev, calendrier et
lancement manuel sont presents. Dev est restee au commit parent : l'installation
n'a pas fusionne la proposition. La configuration Dependabot existante est
preservee. Apres nettoyage, l'inventaire ne contient plus de manifeste pip de test
et compte GitHub Actions a la racine et cinq repertoires Terraform.

## Cloture technique et limites

Les executions composites de scan, la detection Dependency Review suivie du
retour au vert, le preview, la proposition et la verification des variables sont
valides sur ce fork. Les references d'exemples et d'adaptateurs sont figees au
commit teste ; le workflow temporaire de test est retire dans le nettoyage final.
La publication de ce nettoyage et la revue de la PR 38 restent necessaires.

L'activation facturable avec l'action composite n'a pas ete rejouee sur un depot
desactive. Les gardes et refus sont testes localement ; l'activation du service,
Secret Scanning et Push Protection possedent des preuves historiques distinctes.
Une vulnerabilite Python controlee et un nouveau cycle CodeQL detection/correction
via composite ne sont pas demontres par ces executions reussies seules.
Le calendrier est configure mais pas valide par un run planifie dans cette preuve.

Les regles de fusion obligatoire, les langages compiles, registres prives et
l'activation complete sur plusieurs forks ne sont pas valides ici. Le verrou
de facturation du deuxieme fork reste une reserve historique a lever par un
administrateur. Aucun vrai secret ni droit AWS n'est necessaire a ces tests.
Exporter les preuves selon les regles internes avant suppression des forks :
les liens GitHub seuls ne survivront pas a la suppression de leurs depots.
