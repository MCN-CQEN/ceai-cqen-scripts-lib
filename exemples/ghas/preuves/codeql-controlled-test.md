# Preuve du test CodeQL controle

Date du test : 2026-10-28 (America/Toronto). Les horodatages exportes de l'API
dans le fichier JSON associe sont en UTC.

## Perimetre

- Depot : `MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`.
- Branche : `codex/ghas-controlled-test`, creee depuis `dev`.
- Base : `c386d01ad2387af159ed343880559c39deeec7cf`.
- Fichier : `.github/workflows/ghas-controlled-test.yml`, ligne 16.
- Regle attendue : `actions/unpinned-tag`.

Le workflow de test n'a qu'un declencheur manuel et son job porte la condition
`if: ${{ false }}`. Il est analyse statiquement par CodeQL ; l'action referencee
n'est pas executee. Aucun secret, acces AWS ou code exploitable n'est necessaire.
Les analyses sont lancees manuellement via `ghas-security.yml` sur cette branche.
Aucune PR n'est ouverte et aucune fusion n'est faite dans `dev` ou dans le depot
source, pour ne pas declencher les workflows d'infrastructure.

## Introduction controlee

Le test ajoute volontairement la reference mutable suivante :

```yaml
uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/gitflow/validate-pr@feature/ghas-toolkit
```

- [Commit d'introduction](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/commit/5b3f5d275b05546b94734c450f30d041ef6f815b)
- [Analyse avant correction](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/40778673766)
- [Alerte controlee numero 52](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/security/code-scanning/52)

Resultat constate : les analyses Actions et Python reussissent, et une nouvelle
alerte `actions/unpinned-tag` est ouverte sur le fichier de test a la ligne 16,
pour le commit d'introduction. Cette alerte est distincte des alertes preexistantes
48 et 51 du depot.

## Correction

La meme reference est remplacee par le SHA complet d'un commit de la bibliotheque
contenant l'action cible, dont l'existence a ete verifiee :

```yaml
uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/gitflow/validate-pr@b095b20e7d751a755c2cb947b8c577eefe84b412
```

- [Commit de correction](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/commit/9d2dbdf579fa0a9e6ac937a09c3e9af9075b820f)
- [Analyse apres correction](https://github.com/MCN-CQEN/ceai-cqen-labinfra-cluster-ghas/actions/runs/40778919910)

Resultat constate : l'instance de l'alerte 52 sur
`refs/heads/codex/ghas-controlled-test` est passee de `open` a `fixed` apres la
nouvelle analyse. Les deux executions sont terminees avec la conclusion
`success`, avec les jobs CodeQL Actions et Python reussis.

| Mesure | Introduction | Correction |
| --- | --- | --- |
| Run GitHub Actions | `40778673766` | `40778919910` |
| Resultats CodeQL Actions | 52 | 51 |
| Resultats CodeQL Python | 0 | 0 |
| Instance de l'alerte controlee 52 | `open` | `fixed` |

Les 51 autres resultats Actions sont preexistants et ne sont pas corriges par
ce test. La reussite du job CodeQL signifie que l'analyse et l'envoi des resultats
ont reussi ; elle ne signifie pas que le depot est exempt de risques.

L'API de detail de l'alerte renvoie `state: null` et `fixed_at: null` au niveau
global. La preuve de correction est donc explicitement
`most_recent_instance.state: fixed` pour la reference de la branche de test,
et non une affirmation sur l'etat de la branche par defaut `dev`.

Les [preuves JSON](./codeql-controlled-test.json) conservent les commits, les
liens des runs et jobs, leurs conclusions, les metadonnees des analyses et les
etats de l'alerte avant/apres. Ce fichier est un export filtre de l'API GitHub,
sans identifiants d'authentification, et non un export SARIF complet.

## Reproduction

1. Dans un fork autorise, creer une branche de test depuis la branche analysee.
2. Ajouter le fichier de test avec `workflow_dispatch`, `permissions: contents: read`,
   un job `if: ${{ false }}` et une etape utilisant la reference mutable ci-dessus.
3. Lancer manuellement `GHAS - Security checks` sur cette branche et conserver
   le commit, le lien du run et l'alerte correspondant exactement au fichier.
4. Remplacer uniquement la reference mutable par le SHA complet verifie.
5. Relancer l'analyse sur la meme branche, verifier l'etat `fixed` de l'instance
   et conserver les nouveaux identifiants dans une fiche de preuve distincte.

Conclusion : le test controle de detection et de correction CodeQL Actions est
valide sur le fork pilote.

## Limites

Ce test porte sur une faiblesse de securite des workflows GitHub Actions. Il ne
valide pas Secret scanning, Push protection ou Dependency Review. Le job
Dependency Review est ignore lors de ces executions manuelles. Le succes de
l'analyse Python confirme son execution, pas la detection d'une vulnerabilite
Python controlee. Les autres alertes du depot ne sont pas corrigees par ce test.

La branche de test est conservee pour l'audit, avec le fichier corrige et le job
toujours desactive. Ne pas fusionner cette fixture dans le depot source.

## Reference

- [Regle CodeQL et correction par SHA](https://codeql.github.com/codeql-query-help/actions/actions-unpinned-tag/)
