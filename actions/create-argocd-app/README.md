# GitHub Action — Créer une application dans ArgoCD

Cette GitHub Action permet d’automatiser la création d’une application Argo CD si elle n’existe pas déjà.

Elle installe l’CLI ArgoCD si nécessaire, se connecte au serveur, vérifie l’existence du projet, crée l’application, ajoute les paramètres Helm éventuels, puis attend que l’application soit Healthy.

## Table des matières

- [Introduction](./README.md#introduction)
- [Fonctionnalités](./README.md#fonctionnalités)
- [Entrées (inputs)](./README.md#entrées-inputs)
- [Comportement général](./README.md#comportement-général)
- [Utilisation](./README.md#utilisation)
- [Exemple de workflow](./README.md#exemple-avec-paramètres-helm)
- [Dépendances](./README.md#dépendances)
- [Troubleshooting](./README.md#troubleshooting)

## Introduction

Cette action GitHub automatise la gestion d’applications ArgoCD dans un contexte CI/CD.
Elle :

- installe et configure le CLI ArgoCD si nécessaire ;
- se connecte à Argo CD via utilisateur/mot de passe ;
- vérifie que le projet existe (sinon interrompt proprement) ;
- crée l’application ArgoCD si elle n'existe pas ;
- applique les paramètres Helm fournis sous forme key=value ;
- attend que l’application soit Healthy avant de terminer le job.

## Fonctionnalités

- 🚀 Installation automatique de l’ArgoCD CLI
- 🔑 Authentification simple via username / password
- 📁 Vérification de l’existence du projet ArgoCD
- 🏗️ Création conditionnelle d’une application ArgoCD
- ⚙️ Support des paramètres Helm (key=val)
- ⏳ Validation de la santé de l’application (argocd app wait)
- 🛑 Sort proprement si le projet ArgoCD n’existe pas
- Compatible ArgoCD >= v2.x

## Entrées (inputs)

| Nom | Description | Obligatoire | Valeur par défaut |
|------|--------|---------|---------|
|argocd_server|URL du serveur ArgoCD|✅|—|
|argocd_version|Version du CLI ArgoCD à installer (même version que ArgoCD de travail)|❗|v2.10.20|
|argocd_username|Nom d’utilisateur ArgoCD|❗|admin|
|argocd_password|Mot de passe ArgoCD|✅|-|
|app_project_name|Projet ArgoCD où créer l’application. Le projet devrait déjà exister, si non, le workflow ne continue pas.|✅|—|
|app_name|Nom de l’application ArgoCD|✅|—|
|app_dest_namespace|Namespace cible sur Kubernetes|❗|argocd|
|app_manifest_repo|Repo Git contenant les manifests Helm/Kustomize|✅|—|
|app_manifest_repo_branch|CBranche du repo|❗|main|
|app_manifest_path|Chemin dans le repo vers les manifests|✅|—|
|helm_params|Paramètres Helm au format "key1=val1,key2=val2"|❗|vide|

## Comportement général

1. Installe le CLI ArgoCD si absent.
2. Se connecte au serveur Argo CD via username/password.
3. Vérifie si le projet ArgoCD existe.
4. Si le projet n'existe pas, le workflow s'arrête proprement.
5. Vérifie si l’application existe.
6. Si elle n'existe pas:
    - construit la commande `argocd app create`
    - applique les paramètres helm si fournis
    - crée l’application
7. Attend que l’application devienne Healthy.

## Utilisation

Voici un exemple minimal :
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create ArgoCD App
        #uses: ./.github/actions/create-argocd-app
        uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/create-argocd-app@main
        with:
          argocd_server: argocd.example.com
          argocd_username: ${{ secrets.ARGOCD_USERNAME }}
          argocd_password: ${{ secrets.ARGOCD_ADMIN_PASSWORD }}          
          app_project_name: demo-project
          app_name: demo-app
          app_manifest_repo: https://github.com/myorg/myrepo.git
          app_manifest_path: charts/demo
```

## Exemple avec paramètres Helm

```yaml
helm_params: "image.tag=1.2.3,replicaCount=2"
````

## Dépendances

- ArgoCD CLI
    - installé automatiquement si absent
- Accès réseau au serveur Argo CD
- Identifiants ArgoCD fonctionnels
- Éventuellement : GitOps repo public ou privé

## Troubleshooting

❌ Login échoue

    Vérifier l’URL (HTTPS requis)
    Vérifier --grpc-web et --insecure selon la configuration de votre API server
    Vérifier le mot de passe fourni
   
❌ "project does not exist, exit workflow" 
    
    Le projet ArgoCD n’a pas été créé par l’administrateur.

❌ L’application ne devient jamais Healthy

    Augmente le timeout ou vérifie les resources Kubernetes.