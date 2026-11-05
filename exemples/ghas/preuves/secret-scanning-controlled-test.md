# Test controle Secret Scanning et Push Protection

Date de preparation : 2026-10-29 (America/Toronto).

## Etat actuel

Secret Scanning et Push Protection sont actives sur le depot
`MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`, comme verifie par API.
Le 2026-10-30, la publication du motif et la detection de la valeur fictive ont
ete confirmees par API. La protection du motif personnalise a ensuite ete
activee et un push contenant une nouvelle valeur fictive a bien ete refuse.
Les deux tests sont valides. Le nettoyage du premier fichier et la cloture de
l'alerte ont ete verifies par API le 2026-10-30.

| Element | Valeur |
| --- | --- |
| Motif | `GHAS validation fictive` |
| Identifiant | `47519` |
| Slug | `ghas_validation_fictive` |
| Expression | `GHAS_VALIDATION_[A-Z0-9]{24}` |
| Etat initial | `unpublished` |
| Push protection initiale du motif | `false` |
| Push protection au test du 2026-10-30 | `true` |
| Branche dediee | `codex/ghas-secret-test` |
| Commit du fichier fictif | `8296605405c7298e19dd686de73a3ff92a9f899d` |
| Nombre de correspondances locales dans le fichier | Une |

Le [fichier fictif](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/blob/codex/ghas-secret-test/security-tests/secret-scanning-fixture.txt)
est un texte inerte qui n'authentifie aucun service. Aucun vrai jeton n'a ete
cree, utilise ou publie. La branche `dev` et le depot source ne sont pas modifies
par la preparation. Aucune PR n'est ouverte pour ce test.

## Publication et detection validees

Le motif est publie depuis `2026-10-30T17:45:03Z` et
l'[alerte Secret Scanning numero 1](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/security/secret-scanning/1)
a ete creee a `2026-10-30T17:45:07Z`. Son type est
`ghas_validation_fictive` et son emplacement confirme la ligne 2 du fichier
`security-tests/secret-scanning-fixture.txt`, dans le commit
`8296605405c7298e19dd686de73a3ff92a9f899d`.

La detection par le motif personnalise est donc validee. Elle ne valide pas
la couverture de tous les types de secrets fournisseurs. Les horodatages API
ci-dessus sont en UTC. Pour reproduire la publication :

1. Dans les reglages du fork, ouvrir `Advanced Security` puis `Secret Protection`
   et `Custom patterns`. Ouvrir le motif `GHAS validation fictive` deja cree.
2. Lancer `Save and dry run`, attendre les resultats et verifier une correspondance
   sur `security-tests/secret-scanning-fixture.txt` dans la branche de test.
   Le test a blanc ne cree pas d'alerte.
3. Publier avec `Publish pattern`, sans activer pour le moment la push protection
   de ce motif. La publication lance l'analyse de l'historique des branches.
4. Verifier l'alerte du motif dans `Security` > `Secret scanning` et conserver
   son URL, son numero et l'emplacement. Ne pas copier d'autres secrets eventuels
   dans la fiche de preuve.

L'API documentee permet de creer le brouillon, mais n'expose pas dans cette
version les operations de test a blanc, de publication ou d'activation de la
push protection du motif. Le navigateur de l'agent n'etant pas connecte au compte,
ces operations necessitent la session GitHub de l'administrateur du depot.

## Push protection validee

Le 2026-10-30, l'API confirme `push_protection_enabled: true` pour le motif
47519, mis a jour a `2026-10-30T19:22:39Z`. Une copie temporaire du fork a servi
a creer un commit local avec une nouvelle valeur fictive correspondant au motif,
differente de celle deja detectee dans l'historique.

- Branche tentee : `codex/ghas-push-protection-test`.
- Commit local : `a42f60604fc93b15196de5cbc4330f1a19a363ac`.
- Fichier : `security-tests/push-protection-fixture.txt`, ligne 2.
- Resultat : `git push` termine avec le code 1, erreur GitHub `GH013`,
  `GITHUB PUSH PROTECTION`, `Push cannot contain secrets`.
- Le diagnostic nomme explicitement `GHAS validation fictive` et cet emplacement.
- Verification `git ls-remote` : sortie vide, code 0 ; la branche distante
  n'a pas ete creee. Aucun bypass n'a ete utilise.

Le commit local de test n'est pas signe : la signature a ete desactivee pour
cette commande uniquement, sans modification de configuration Git. Le rejet
observe concerne bien le motif de secret, pas une exigence de signature.
La branche `dev`, le depot source et les protections existantes sont inchanges.

Le [diagnostic de refus](./secret-scanning-push-protection-refusal.txt) est conserve
sans le lien de contournement. Ce test valide notre motif personnalise, pas la
couverture de tous les secrets fournisseurs.

## Nettoyage verifie

Le fichier fictif n'est plus present sur `codex/ghas-secret-test` (API Contents :
404). L'alerte 1 est `resolved`, resolution `used_in_tests`, depuis
`2026-10-30T20:20:13Z`. Le fichier reste dans l'historique Git : son retrait
n'est pas une purge d'historique et ne suffirait pas pour traiter un vrai secret.

Le motif personnalise est conserve pour le moment, avec les preuves et les
protections actives. Une suppression de motif peut supprimer ses alertes selon
l'option choisie : ne pas utiliser une suppression definitive des preuves.

## Preuves

Les [metadonnees JSON](./secret-scanning-controlled-test.json) sont conservees
sans identifiant d'authentification. Les validations de detection et de Push
Protection sont a `true`. Les etats initiaux et l'instantane de publication
sont historiques ; l'etat au test de push figure dans `push_protection_test`.

## References

- [Definition et publication des motifs](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/customize-leak-detection/define-custom-patterns)
- [Activation de la protection d'un motif](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/customize-leak-detection/manage-custom-patterns)
- [API des motifs personnalises](https://docs.github.com/en/rest/secret-scanning/custom-patterns)
