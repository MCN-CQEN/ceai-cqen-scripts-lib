# Publier une image au registre des conteneurs d'images

## Table des matières

- [Introduction](./README.md#introduction)
- [Fonctionnalités](./README.md#fonctionnalités)
- [Entrées (Inputs)](./README.md#entrées-inputs)
- [Exemple d’utilisation](./README.md#exemple-dutilisation)
- [Détails du fonctionnement](./README.md#détails-du-fonctionnement)
- [Prérequis](./README.md#prérequis)
- [Limitations](./README.md#limitations)

## Introduction

Cette action GitHub permet de construire et publier automatiquement une image Docker dans un registre de conteneurs — en particulier GitHub Container Registry (GHCR) ou tout autre registre compatible.

Elle inclut plusieurs étapes :
- vérification du dépôt,
- connexion au registre,
- extraction automatique de métadonnées (tags, labels),
- build & push de l’image,
- génération d’un certificat d’attestation de build (pour les dépôts publics).

## Fonctionnalités

- 🔐 Connexion sécurisée au registre
- 🏷️ Génération automatique des tags et labels Docker
- 🏗️ Build et mise en ligne de l’image Docker
- 📄 Attestation de build (provenance) pour les dépôts publics
- ⚙️ Personnalisation du nom de l'image et du registre

## Entrées (Inputs)

| Nom de l’input | Description | Obligatoire |Valeur par défaut|
|------|--------|---------|---------|
|registry|Le registre dans lequel publier l'image Docker|✅|ghcr.io|
|image-name|Le nom de l'image à produire|✅|${{ github.repository }}|
|github-token|Le token permettant l'authentification au registre|❗|-|

## Exemple d’utilisation

name: Build & Publish Docker image

```yaml
on:
  push:
    branches: [ "main" ]

jobs:
  publish-docker-image:
    runs-on: ubuntu-latest
    steps:
      - name: Build & publish
        uses: MCN-CQEN/ceai-cqen-commons/actions/publish-image-to-registry@main
        with:
          registry: ghcr.io
          image-name: ${{ github.repository }}-${{ github.run_number }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Détails du fonctionnement

1. Checkout du dépôt

    Utilisation de actions/checkout@v7.0.0 pour récupérer le contenu du repository.

2. Connexion au registre de conteneurs

    Connexion via docker/login-action@v3 avec le token GitHub fourni.

3. Extraction des métadonnées

    docker/metadata-action@v5 génère automatiquement :
    - les tags (par ex. latest, SHA, tags Git…)
    - les labels OCI

4. Build et push de l’image Docker

    docker/build-push-action@v6 :
    - construit l’image à partir du contexte .
    - applique les tags et labels générés
    - pousse l’image vers le registre

5. Attestation de build (provenance)

    Uniquement si le dépôt est public.
    Utilise actions/attest-build-provenance@v2 pour produire un certificat attaché à l’image.

## Prérequis

- Le repository doit activer GitHub Actions.
- Pour ghcr.io, il faut disposer d’un token incluant :
    - write:packages
    - read:packages
    - delete:packages (optionnel)
- Docker doit être supporté par le runner (par défaut sur ubuntu-latest).

## Limitations

- L’attestation de build ne fonctionne pas dans les dépôts privés (restriction GitHub).
- L’action suppose que votre Dockerfile se trouve à la racine du projet (ou que le contexte soit modifiable dans une future version).
