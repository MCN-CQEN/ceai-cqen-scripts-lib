# Test controle Dependency Review

Verification par API GitHub le 2026-11-03.

## Perimetre

- Depot : `MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`.
- [Pull request 1](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/pull/1).
- Branche source : `test/ghas-dependency-review` ; destination : `dev` du fork.
- Fichier de test : `security-tests/dependency-review/requirements.txt`.
- Dependance volontairement vulnerable : `requests==2.19.1`.
- Le test consiste a declarer la dependance, sans demander son installation.

## Detection

Le controle `dependency-review / Dependency Review` echoue sur le commit
`ae7f69fb5a85f39f1d85861241549966d8c4ba43`, le 2026-11-03 a 16:16:23 UTC.

[Execution de detection](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/41672445787/job/126044080490).

Le journal transmis par l'utilisateur indique cinq vulnerabilites pour
`requests@2.19.1`, une elevee et quatre moderees :

- `GHSA-x84v-xcm2-53pg` (high).
- `GHSA-j8r2-6x86-q33q` (moderate).
- `GHSA-9wx4-h78v-vm56` (moderate).
- `GHSA-9hjg-9r4m-mvj7` (moderate).
- `GHSA-gc5v-m9x4-r6x2` (moderate).

Message rapporte : `Dependency review detected vulnerable packages.`
La conclusion `failure` et les liens de controle ont ete verifies par API ;
la liste ci-dessus provient du journal fourni par l'utilisateur.

## Retour au vert

Apres retrait du fichier de test, le meme controle reussit sur le commit
`af1b7b936ded16667c9b35d7e3f28e5ca6b43ba4`, le 2026-11-03 a 16:21:46 UTC.

[Execution apres nettoyage](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/41673378332/job/126047380156).

Le fichier de test ne figure plus dans le diff final. La PR est fermee depuis
2026-11-03T16:27:45Z et `merged` vaut `false`.

Le diff final contient cependant
`aws/terraform/modules/initial-config-role/bootstrap-contract.yaml`.
Cette modification est hors du perimetre de la preuve : elle n'a pas ete
modifiee ni annulee par l'agent. Le nettoyage valide ici concerne le fichier
de dependance de test, pas un diff final entierement vide.

## Interpretation

Le test valide la detection de dependances vulnerables introduites par une PR,
puis le retour au vert apres leur retrait. Il ne prouve pas une regle obligatoire
de blocage de fusion ni la generation d'alertes Dependabot.

Des controles distincts nommes `Dependency Review` sont `skipped` dans les
executions 41672443815 et 41673377194. Ils ne constituent pas les preuves de
detection ou de correction ; les liens retenus ci-dessus visent le controle
reutilisable effectivement execute.
