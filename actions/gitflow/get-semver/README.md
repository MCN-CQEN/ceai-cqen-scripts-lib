# Description

Utilise la libraire [GitVersion](https://gitversion.net/) pour déterminer le prochain numéro de version pour la branche en cours.

Respecte les règles de versionnage définies pour le CQEN :

| Branche   | Exemple                            |
|-----------|------------------------------------|
| `feature` | 1.2.0-feature.nouvel-ecran+ca1f980 |
| `dev`     | 1.2.0-dev+865860e                  |
| `release` | 2.0.0-rc.1                         |
| `prod`    | 2.0.0                              |
| `hotfix`  | 2.0.1-hotfix.CVE-1234+f03cd2a      |
| `support` | 2.0.1-support+ec13609              |


# Paramètres

| Variable               | Type     | Description    |
|------------------------|----------|----------------|
| buildNumberField       | `string` | Nom de la variable retournée par GitVersion qui contient le numéro de build. |
| preReleaseNumberField  | `string` | Nom de la variable retournée par GitVersion qui contient le numéro de build du release. |
| mainBranchNameRegex    | `regex` | Regex de la branche main |
| releaseBranchNameRegex | `regex` | Regex de la branche release |
| versionPrefix          | `string` | Préfixe de la version (ex : 'v') qui sera systématiquement ajouté au début du tag de version"  |


# Valeurs retournées

| Variable    | Type     | Description    |
|-------------|----------|----------------|
| semVer      | `string` | Le prochain numéro de version pour la branche en cours. Voir la grille plus haut pour des exemples | 

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
      - develop
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