# Description

Utilise la libraire [GitVersion](https://gitversion.net/) pour déterminer le prochain numéro de version pour la branche en cours.

Respecte les règles de versionnage définies pour le CQEN :

| Branche   | Exemple                            |
|-----------|------------------------------------|
| `feature` | 1.4.2-feature-auth.20260707.45296.a1b2c3d |
| `dev` | 1.4.2-dev.20260707.45296.a1b2c3d |
| `release` | 1.5.0-rc.20260707.45296.a1b2c3d |
| `main`    | 2.0.0                              |
| `hotfix`  | 1.4.3-hotfix-correction.20260707.45296.a1b2c3d |

Pour les branches de préversion, GitVersion demeure la source de référence pour la portion `Major.Minor.Patch`.
L'action ajoute ensuite un suffixe standardisé :

```text
Major.Minor.Patch-prebuild.YYYYMMDD.SSSSS.hashcommit
```

- `prebuild` représente le contexte GitFlow (`feature-*`, `dev`, `rc`, `hotfix-*`).
- `YYYYMMDD` correspond à la date UTC d'exécution du workflow.
- `SSSSS` correspond au nombre de secondes écoulées depuis le début de la journée UTC.
- `hashcommit` correspond au hash court du commit.

# Paramètres

| Variable               | Type     | Description    |
|------------------------|----------|----------------|
| mainBranchNameRegex    | `regex`  | Regex de la branche main |
| releaseBranchNameRegex | `regex`  | Regex de la branche release |
| versionPrefix          | `string` | Préfixe de la version (ex : 'v') qui sera systématiquement ajouté au début du tag de version"  |


# Valeurs retournées

| Variable    | Type     | Description    |
|-------------|----------|----------------|
| semVer      | `string` | Le prochain numéro de version pour la branche en cours. Voir la grille plus haut pour des exemples. |

# Exemple d'utilisation

```yaml
name: "Créer un tag de version"
on:
  push:
    branches:
      - feature/*
      - release/*
      - hotfix/*
      - main
      - dev
jobs:
  get_semver_version:
    name: Calculer la version et appliquer le tag
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read 
      contents: write 
    steps:
    - name: Checkout
      uses: actions/checkout@v4

    # Utilisation de l'action 'get-semver' ici :
    - name: Obtenir version
      id: obtenir_version
      uses: ./actions/get-semver
      with:
        mainBranchName: main
    
    - name: Créer le tag
      id: creer_tag
      uses: ./actions/create-version-tag
      with:
        # Le semVer créé est utilisé ici :
        semVer: ${{ steps.obtenir_version.outputs.semVer }}
```
