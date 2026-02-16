# GitHub Action – Créer une application dans ArgoCD

## Introduction

Cette GitHub Action composite permet de **créer automatiquement une application dans Argo CD si elle n’existe pas déjà**.

Elle :

* Installe la CLI si nécessaire
* Se connecte au serveur Argo CD
* Ajoute un dépôt Git privé (via GitHub App) si requis
* Vérifie l’existence du projet Argo CD
* Crée l’application si absente
* Attend que l’application soit en état *Healthy*

Technologies utilisées :

* Argo CD
* GitHub Actions
* Kubernetes

---

## Table des matières

* [Vue d’ensemble](#vue-densemble)
* [Fonctionnement](#fonctionnement)
* [Inputs](#inputs)
* [Workflow interne](#workflow-interne)
* [Exemple d’utilisation](#exemple-dutilisation)
* [Gestion des dépôts privés](#gestion-des-dépôts-privés)
* [Bonnes pratiques sécurité](#bonnes-pratiques-sécurité)
* [Dépannage](#dépannage)

---

## Vue d’ensemble

Nom de l’action :

```
créer une application dans ArgoCD
```

Description :

```
créer une application dans ArgoCD si elle n'existe pas
```

Cette action est de type **composite** et exécute une série d’étapes Bash pour automatiser la gestion d’applications Argo CD.

---

## Fonctionnement

L’action suit la logique suivante :

1. Vérifier si la CLI Argo CD est installée
2. Installer la CLI si nécessaire
3. Se connecter au serveur Argo CD
4. Ajouter le dépôt Git (si privé)
5. Vérifier que le projet Argo CD existe
6. Créer l’application si elle n’existe pas
7. Attendre que l’application soit *Healthy*

---

## Inputs

| Input                        | Requis | Description                             |
| ---------------------------- | ------ | --------------------------------------- |
| `argocd_server`              | ✅      | URL du serveur Argo CD                  |
| `argocd_version`             | ❌      | Version CLI Argo CD (défaut: v2.10.20)  |
| `argocd_username`            | ❌      | Username (défaut: admin)                |
| `argocd_password`            | ✅      | Mot de passe Argo CD                    |
| `app_project_name`           | ✅      | Nom du projet Argo CD                   |
| `app_name`                   | ✅      | Nom de l’application                    |
| `app_dest_namespace`         | ❌      | Namespace cible (défaut: defaultApp)    |
| `app_manifest_repo`          | ✅      | URL du repo Git                         |
| `app_manifest_repo_branch`   | ❌      | Branche (défaut: main)                  |
| `app_manifest_path`          | ✅      | Chemin du manifeste                     |
| `helm_params`                | ❌      | Paramètres Helm (`key1=val1,key2=val2`) |
| `private_repo`               | ❌      | Indique si le repo est privé            |
| `github_app_id`              | ❌      | GitHub App ID                           |
| `github_app_installation_id` | ❌      | GitHub App Installation ID              |
| `github_app_private_key`     | ❌      | Clé privée GitHub App                   |

---

## Workflow interne

### 1️⃣ Installation CLI

Vérifie la présence de `argocd`.
Si absente → téléchargement depuis GitHub Releases.

---

### 2️⃣ Login Argo CD

```bash
argocd login <server> --username <user> --password <pass> --grpc-web --insecure
```

---

### 3️⃣ Gestion repo privé (GitHub App)

Si `private_repo=true` :

* Vérifie la présence des credentials GitHub App
* Ajoute le repo si absent
* Ignore si déjà enregistré

---

### 4️⃣ Vérification du projet

```bash
argocd proj get <project>
```

Si le projet n’existe pas → arrêt du workflow.

---

### 5️⃣ Création conditionnelle de l’application

Si l’application n’existe pas :

```bash
argocd app create ...
```

Options appliquées :

* `--sync-policy automated`
* `--sync-option CreateNamespace=true`
* `--dest-server https://kubernetes.default.svc`

---

### 6️⃣ Attente du statut Healthy

```bash
argocd app wait <app> --health --timeout 300
```

---

## Exemple d’utilisation

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Créer application ArgoCD
        uses: ./github-actions/create-argocd-app
        with:
          argocd_server: https://argocd.example.com
          argocd_password: ${{ secrets.ARGOCD_PASSWORD }}
          app_project_name: base
          app_name: my-app
          app_manifest_repo: https://github.com/org/repo.git
          app_manifest_path: charts/my-app
```

---

## Gestion des dépôts privés

Si le repo est privé :

```yaml
private_repo: "true"
github_app_id: ${{ secrets.GH_APP_ID }}
github_app_installation_id: ${{ secrets.GH_APP_INSTALLATION_ID }}
github_app_private_key: ${{ secrets.GH_APP_PRIVATE_KEY }}
```

L’action :

* Vérifie si le repo est déjà enregistré
* Ajoute le repo via GitHub App
* Stocke temporairement la clé privée

---

## Bonnes pratiques sécurité

* Utiliser des **GitHub Secrets**
* Éviter `--insecure` en production si possible
* Restreindre les permissions Argo CD
* Ne jamais exposer la clé privée GitHub App en clair
* Limiter l’accès admin Argo CD

---

## Dépannage

### ❌ Erreur login Argo CD

* Vérifier l’URL
* Vérifier les credentials
* Vérifier l’accessibilité réseau

### ❌ Projet inexistant

Le workflow s’arrête volontairement.
Créer le projet via :

```bash
argocd proj create <project>
```

### ❌ Application stuck en Progressing

Vérifier :

```bash
argocd app get <app>
kubectl get pods -n <namespace>
```

---

## Fonctionnalités principales

* Idempotent (ne recrée pas si existe)
* Support repo privé via GitHub App
* Sync automatique
* Attente du statut Healthy
* Paramétrage Helm dynamique

