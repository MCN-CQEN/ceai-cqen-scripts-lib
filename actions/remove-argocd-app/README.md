# GitHub Action — Supprimer une application ArgoCD

Cette GitHub Action permet d'automatiser la suppression d'une application Argo CD.

Elle installe le CLI ArgoCD si nécessaire, se connecte au serveur, vérifie l'existence du projet, puis supprime l'application si elle existe.

## Table des matières

- [Introduction](./README.md#introduction)
- [Fonctionnalités](./README.md#fonctionnalités)
- [Entrées (inputs)](./README.md#entrées-inputs)
- [Comportement général](./README.md#comportement-général)
- [Utilisation](./README.md#utilisation)
- [Exemple de workflow](./README.md#exemple-de-workflow)
- [Dépendances](./README.md#dépendances)
- [Troubleshooting](./README.md#troubleshooting)

## Introduction

Cette action GitHub automatise la suppression d'applications ArgoCD dans un contexte CI/CD.
Elle :

- installe et configure le CLI ArgoCD si nécessaire ;
- se connecte à Argo CD via utilisateur/mot de passe ;
- vérifie que le projet existe (sinon interrompt proprement) ;
- supprime l'application ArgoCD si elle existe ;
- utilise la cascade de suppression pour nettoyer proprement les ressources.

## Fonctionnalités

- 🚀 Installation automatique de l'ArgoCD CLI
- 🔑 Authentification simple via username / password
- 📁 Vérification de l'existence du projet ArgoCD
- 🗑️ Suppression sécurisée d'une application ArgoCD
- ⚙️ Support du namespace d'application
- 🛑 Sort proprement si le projet ArgoCD n'existe pas
- Compatible ArgoCD >= v2.x

## Entrées (inputs)

| Nom | Description | Obligatoire | Valeur par défaut |
|------|--------|---------|---------|
|argocd_server|URL du serveur ArgoCD|✅|—|
|argocd_version|Version du CLI ArgoCD à installer|❗|v2.10.20|
|argocd_username|Nom d'utilisateur ArgoCD|❗|admin|
|argocd_password|Mot de passe ArgoCD|✅|—|
|app_project_name|Projet ArgoCD contenant l'application. Le projet devrait déjà exister.|✅|—|
|app_name|Nom de l'application ArgoCD à supprimer|✅|—|
|app_dest_namespace|Namespace de l'application ArgoCD|❗|defaultApp|

## Comportement général

1. Installe le CLI ArgoCD si absent.
2. Se connecte au serveur Argo CD via username/password.
3. Vérifie si le projet ArgoCD existe.
4. Si le projet n'existe pas, le workflow s'arrête proprement.
5. Vérifie si l'application existe.
6. Si elle existe :
    - exécute `argocd app delete` avec cascade
    - supprime proprement toutes les ressources associées
7. Si elle n'existe pas, signale qu'il n'y a rien à supprimer.

## Utilisation

Voici un exemple minimal :
```yaml
jobs:
  remove:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Remove ArgoCD App
        uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/remove-argocd-app@main
        with:
          argocd_server: argocd.example.com
          argocd_username: ${{ secrets.ARGOCD_USERNAME }}
          argocd_password: ${{ secrets.ARGOCD_ADMIN_PASSWORD }}          
          app_project_name: demo-project
          app_name: demo-app
          app_dest_namespace: default
```

## Exemple de workflow

```yaml
name: Remove ArgoCD Application
on:
  workflow_dispatch:
    inputs:
      app_name:
        description: 'Name of the application to remove'
        required: true

jobs:
  remove-app:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Remove Application
        uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/remove-argocd-app@main
        with:
          argocd_server: ${{ secrets.ARGOCD_SERVER }}
          argocd_password: ${{ secrets.ARGOCD_PASSWORD }}
          app_project_name: my-project
          app_name: ${{ github.event.inputs.app_name }}
          app_dest_namespace: production
```

## Dépendances

- ArgoCD CLI
    - installé automatiquement si absent
- Accès réseau au serveur Argo CD
- Identifiants ArgoCD fonctionnels
- Permissions suffisantes pour supprimer des applications dans le projet

## Troubleshooting

❌ Login échoue

    Vérifier l'URL (HTTPS requis)
    Vérifier --grpc-web et --insecure selon la configuration de votre API server
    Vérifier le mot de passe fourni
   
❌ "project does not exist, exit workflow" 
    
    Le projet ArgoCD n'a pas été créé par l'administrateur ou le nom est incorrect.

❌ Erreur lors de la suppression

    Vérifier que l'utilisateur ArgoCD a les permissions de suppression
    Vérifier que l'application existe effectivement
