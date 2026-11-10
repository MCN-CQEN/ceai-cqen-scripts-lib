# Validation Dependabot sur le fork pilote

Verification des PR et de leurs controles par API le 2026-11-03.
Depot : `MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`, branche par defaut `dev`.

## Configuration et activation

La [PR 2](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/pull/2)
ajoute uniquement `.github/dependabot.yml`. Elle est fusionnee dans `dev` depuis
2026-11-03T19:14:24Z. Le fichier configure des mises a jour hebdomadaires pour :

- GitHub Actions, repertoire `/` ;
- Terraform, repertoires `/aws/terraform/modules/*`.

Chaque entree limite les PR de mise a jour de versions ouvertes a 5.
L'utilisateur a confirme l'activation de Dependency graph, Dependabot alerts
et Dependabot security updates. L'activation des mises a jour de versions sur
le fork a ensuite ete effectuee dans l'interface Dependabot.

La capture fournie montre huit PR creees par `dependabot[bot]` : cinq pour
GitHub Actions (6 a 10), trois pour Terraform (3 a 5). Un job indique
`Dependabot cannot open any more pull requests` : cette limite n'invalide pas
la creation des propositions deja constatees. Ce n'est pas une preuve que
tous les jobs Terraform et Actions se terminent sans erreur.

## Adaptation GitFlow

Le validateur refusait initialement les branches `dependabot/...` vers `dev`.
La [PR 11](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/pull/11),
fusionnee le 2026-11-03 a 21:34:08 UTC, ajoute un parametre
`restrictions_branches` dans le workflow appelant du fork, sans modifier l'action
de la bibliotheque. Les branches de production restent limitees a
`release/` et `hotfix/`. Vers `dev`, la regle est :

```regex
^(release|feature|hotfix|dependabot)/.+$
```

Apres un commentaire `@dependabot rebase`, la PR de mise a jour est actualisee.
Les controles de securite ne sont pas contournes.

## PR de preuve

[PR 9 : actions/checkout 7.0.0 vers 7.0.1](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/pull/9).

- Source : `dependabot/github_actions/actions/checkout-7.0.1`.
- Destination : `dev` du fork.
- Commit verifie : `a3e4a4b20de75e4d026d04cb75e720c26d4cdc9a`.
- Etat lors de la verification : ouverte, non fusionnee.

| Controle | Resultat | Preuve |
| --- | --- | --- |
| GitFlow | success | [Job](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/41724038220/job/126224082577) |
| CodeQL Actions | success | [Job](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/41724038068/job/126224001487) |
| CodeQL Python | success | [Job](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/41724038068/job/126224001564) |
| Dependency Review | success | [Job](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/41724038068/job/126224001306) |

Les anciens controles autonomes `Dependency Review` et
`CodeQL (${{ matrix.language }})` sont ignores. Les controles reutilisables
ci-dessus sont effectivement executes, et non ignores.

## Conclusion et limites

La configuration, la creation de PR Actions/Terraform et l'execution des
controles sur une PR Dependabot sont validees sur le fork. La fusion de la PR 9
n'est pas necessaire pour cette preuve et n'a pas ete demandee.

Une PR de mise a jour de version n'est pas une alerte de vulnerabilite.
Cette preuve ne demontre ni une alerte Dependabot controlee sur la branche par
defaut, ni une correction automatique de cette alerte, ni la compatibilite de
toutes les mises a jour proposees. Les changements majeurs exigent une revue.
