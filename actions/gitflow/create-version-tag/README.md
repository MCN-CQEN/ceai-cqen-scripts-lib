# Description

Cette action créé une étiquette (tag) pour le commit actuel, basée sur le semVer fourni en paramètre.

Elle est normalement utilisée après `get-semver`. 

L'action roule les étapes suivantes : 
1. Vérifie en premier si le commit actuel a déjà un tag de version
2. Sinon, elle crée le tag en utilisant le semVer fourni en paramètre.

# Paramètres

| Paramètre | Type   | Description | 
|-----------|--------|-------------| 
| semVer    | string | SemVer à utiliser pour créer la tag. |


# Valeurs retournées

Aucune valeur retournée.

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
      # Permission requise pour la validation de l'existance du tag de version :
      pull-requests: read 
      # Permission requise pour la création du tag : 
      contents: write 
    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Obtenir version
      id: obtenir_version
      uses: ./actions/get-semver
      with:
        mainBranchName: main
    
    # Utilisation de l'action 'create-version-tag' ici :
    - name: Créer le tag
      id: creer_tag
      uses: ./actions/create-version-tag
      with:
        semVer: ${{ steps.obtenir_version.outputs.semVer }}
```

