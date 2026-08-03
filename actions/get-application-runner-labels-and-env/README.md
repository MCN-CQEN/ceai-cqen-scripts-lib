# Obtenir les étiquettes du runner pour les applications

Cette action composite GitHub permet de déterminer dynamiquement les étiquettes d’un runner self-hosted ainsi que l’environnement applicatif à utiliser selon :

* la branche de travail de l’application;
* le système ciblé, soit `cqen` ou `mcn`.

L’action retourne les étiquettes du runner sous forme de tableau JSON afin qu’elles puissent être utilisées avec `fromJSON()` dans la propriété `runs-on` d’un job GitHub Actions.

## Fonctionnement

L’action utilise deux informations :

* la branche de travail de l’application;
* le système auquel appartient le runner.

Selon la branche reçue, elle sélectionne l’environnement du runner correspondant.

| Branche de l’application | Environnement du runner | Environnement applicatif      |
| ------------------------ | ----------------------- | ----------------------------- |
| `main`                   | `main`                  | `main`                        |
| `release/v1`             | `release-v1`            | `release-v1`                  |
| `dev`                    | `release-v1`            | `dev`                         |
| `feature/*`              | `release-v1`            | valeur complète de la branche |

Par exemple, pour les valeurs suivantes :

```text
app_branch_ref=feature/test-backup
runner_system=cqen
```

l’action retourne :

```json
["self-hosted","release-v1","cqen"]
```

et :

```text
feature/test-backup
```

## Systèmes pris en charge

Les systèmes autorisés sont :

```text
cqen
mcn
```

L’action échoue si une autre valeur est fournie.

## Branches prises en charge

Les branches autorisées sont :

```text
main
release/v1
dev
feature/*
```

Quelques exemples valides :

```text
main
release/v1
dev
feature/test
feature/configuration-rds
```

La valeur exacte `feature` n’est pas couverte par le motif `feature/*`.

Pour accepter également cette valeur, le bloc `case` doit être modifié ainsi :

```bash
dev|feature|feature/*)
```

## Entrées

### `app_branch_ref`

Branche de travail de l’application.

* Obligatoire : oui
* Type : chaîne de caractères
* Exemples :

```text
main
release/v1
dev
feature/test-rds
```

### `runner_system`

Système associé au runner self-hosted.

* Obligatoire : oui
* Type : chaîne de caractères
* Valeurs permises :

```text
cqen
mcn
```

## Sorties

### `runner_labels`

Liste JSON contenant les étiquettes du runner.

Exemple :

```json
["self-hosted","release-v1","cqen"]
```

Cette sortie est une chaîne JSON. Elle doit être convertie avec `fromJSON()` lorsqu’elle est utilisée dans `runs-on`.

### `app_env`

Nom de l’environnement applicatif déterminé à partir de la branche.

Exemples :

```text
main
release-v1
dev
feature/test-rds
```

## Utilisation dans un workflow

L’action doit être exécutée dans un premier job utilisant un runner déjà disponible, par exemple `ubuntu-24.04`.

```yaml
jobs:
  runner-labels-and-env:
    name: Déterminer le runner et l'environnement
    runs-on: ubuntu-24.04

    outputs:
      runner_labels: ${{ steps.get_runner.outputs.runner_labels }}
      app_env: ${{ steps.get_runner.outputs.app_env }}

    steps:
      - name: Obtenir les étiquettes du runner
        id: get_runner
        uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/get-application-runner-labels-and-env@main
        with:
          app_branch_ref: ${{ github.head_ref || github.ref_name }}
          runner_system: ${{ vars.SYSTEM }}
```

Les sorties du job peuvent ensuite être utilisées dans un autre job :

```yaml
  deploy:
    name: Déployer l'application
    needs: runner-labels-and-env
    runs-on: ${{ fromJSON(needs.runner-labels-and-env.outputs.runner_labels) }}
    environment:
      name: ${{ needs.runner-labels-and-env.outputs.app_env }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Afficher l'environnement
        run: |
          echo "Environnement : ${{ needs.runner-labels-and-env.outputs.app_env }}"
```

## Utilisation dans un workflow réutilisable

Dans le workflow appelant, la sortie JSON doit être transmise comme une chaîne, sans utiliser `fromJSON()` :

```yaml
jobs:
  call-workflow:
    needs: runner-labels-and-env
    uses: ./.github/workflows/deploy.yml
    with:
      runner_labels: ${{ needs.runner-labels-and-env.outputs.runner_labels }}
      environment_name: ${{ needs.runner-labels-and-env.outputs.app_env }}
    secrets: inherit
```

Dans le workflow réutilisable :

```yaml
on:
  workflow_call:
    inputs:
      runner_labels:
        description: Étiquettes du runner au format JSON
        required: true
        type: string

      environment_name:
        description: Nom de l'environnement applicatif
        required: true
        type: string

jobs:
  deploy:
    runs-on: ${{ fromJSON(inputs.runner_labels) }}
    environment:
      name: ${{ inputs.environment_name }}

    steps:
      - uses: actions/checkout@v4
```

La conversion `fromJSON()` doit être effectuée uniquement dans le workflow qui utilise la valeur dans `runs-on`.

## Structure des étiquettes générées

Les étiquettes suivent cette structure :

```json
[
  "self-hosted",
  "<environnement-runner>",
  "<système>"
]
```

Exemple pour la branche `main` et le système `mcn` :

```json
["self-hosted","main","mcn"]
```

Exemple pour la branche `dev` et le système `cqen` :

```json
["self-hosted","release-v1","cqen"]
```

Le runner sélectionné doit posséder simultanément toutes les étiquettes demandées.

Pour la valeur suivante :

```json
["self-hosted","release-v1","cqen"]
```

le runner doit avoir les trois étiquettes :

```text
self-hosted
release-v1
cqen
```

## Validation

L’action valide le système avant de déterminer les étiquettes :

```bash
case "${RUNNER_SYSTEM}" in
  cqen|mcn)
    ;;
  *)
    echo "Unsupported runner system: ${RUNNER_SYSTEM}" >&2
    exit 1
    ;;
esac
```

Elle valide également la branche :

```bash
case "${BRANCH_REF}" in
  main)
    ;;

  release/v1)
    ;;

  dev|feature/*)
    ;;

  *)
    echo "Unsupported application branch: ${BRANCH_REF}" >&2
    exit 1
    ;;
esac
```

Une branche ou un système non pris en charge provoque l’arrêt de l’action avec un code d’erreur.

## Diagnostic

Pour vérifier les sorties de l’action dans le workflow appelant :

```yaml
- name: Vérifier les sorties
  shell: bash
  env:
    RUNNER_LABELS: ${{ steps.get_runner.outputs.runner_labels }}
    APP_ENV: ${{ steps.get_runner.outputs.app_env }}
  run: |
    set -euo pipefail

    echo "Runner labels: >${RUNNER_LABELS}<"
    echo "Application environment: >${APP_ENV}<"

    if [[ -z "${RUNNER_LABELS}" ]]; then
      echo "La sortie runner_labels est vide." >&2
      exit 1
    fi

    echo "${RUNNER_LABELS}" |
      jq -e 'type == "array" and length > 0' >/dev/null
```

La sortie attendue est semblable à :

```text
Runner labels: >["self-hosted","release-v1","cqen"]<
Application environment: >dev<
```

## Erreurs courantes

### `Error from function 'fromJSON': empty input`

Cette erreur indique que la valeur transmise à `fromJSON()` est vide.

Vérifier :

* que le step appelant possède un `id`;
* que l’output de l’action est bien nommé `runner_labels`;
* que le job expose l’output du bon step;
* que le job consommateur contient `needs`;
* que le nom utilisé dans `needs.<job>.outputs.<output>` correspond exactement au nom déclaré.

Exemple correct :

```yaml
outputs:
  runner_labels: ${{ steps.get_runner.outputs.runner_labels }}
```

Puis :

```yaml
runs-on: ${{ fromJSON(needs.runner-labels-and-env.outputs.runner_labels) }}
```

### Les labels sont interprétés comme un seul label

Ne pas transmettre les labels sous cette forme :

```text
release-v1, cqen
```

Cette valeur peut être interprétée comme une seule chaîne.

L’action retourne volontairement un tableau JSON :

```json
["self-hosted","release-v1","cqen"]
```

Il doit être utilisé ainsi :

```yaml
runs-on: ${{ fromJSON(needs.runner-labels-and-env.outputs.runner_labels) }}
```

### `Unsupported application branch: feature`

Le motif suivant :

```bash
feature/*
```

accepte :

```text
feature/test
```

mais pas :

```text
feature
```

Pour accepter les deux formats :

```bash
dev|feature|feature/*)
```

## Limitation

Une action composite ne peut pas déterminer le `runs-on` du job dans lequel elle est exécutée, puisque GitHub doit sélectionner le runner avant de commencer les steps du job.

La séquence requise est donc :

```text
Job de préparation
    ↓
Exécution de l'action composite
    ↓
Exposition des labels comme output du job
    ↓
Job suivant utilisant fromJSON() dans runs-on
```
