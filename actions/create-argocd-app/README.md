# GitHub Action — Créer une application dans ArgoCD

Cette GitHub Action permet d’automatiser la création d’une application Argo CD si elle n’existe pas déjà.

Elle gère l’authentification AWS (assume-role), la récupération du mot de passe ArgoCD depuis Secrets Manager, l’installation de l’CLI ArgoCD, la vérification de l’existence du projet et de l’application, puis la création automatique avec des paramètres Helm optionnels.

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

- se connecte à AWS via un rôle IAM ;
- récupère le mot de passe admin ArgoCD depuis AWS Secrets Manager ;
- installe et configure le CLI ArgoCD si nécessaire ;
- se connecte au serveur ArgoCD ;
- vérifie l’existence du projet ArgoCD ;
- crée l’application ArgoCD si elle n'existe pas ;
- applique automatiquement les paramètres Helm fournis ;
- attend que l’application soit en Healthy state.

## Fonctionnalités

- 🔐 Assume-role AWS et récupération de secrets
- 🚀 Installation automatique de l’ArgoCD CLI
- 🔑 Login automatique au serveur ArgoCD
- 📁 Vérification de l’existence du projet ArgoCD
- 🏗️ Création conditionnelle d’une application ArgoCD
- ⚙️ Support des paramètres Helm (key=val)
- ⏳ Validation de la santé de l’application (argocd app wait)
- 🛑 Sort proprement si le projet ArgoCD n’existe pas

## Entrées (inputs)

| Nom | Description | Obligatoire | Valeur par défaut |
|------|--------|---------|---------|
|role_to_assume|Nom du rôle AWS à assumer|✅|—|
|aws_region|Région AWS|❗|ca-central-1|
|argocd_server|URL du serveur ArgoCD|✅|—|
|argocd_version|Version du CLI ArgoCD à installer (même version que ArgoCD de travail)|❗|v2.10.20|
|argocd_username|Nom d’utilisateur ArgoCD|❗|admin|
|sm_argocd_admin_creds_secret_name|Nom du secret AWS contenant les creds|✅|—|
|sm_argocd_admin_creds_secret_key|Clé à extraire à l’intérieur du secret|✅|—|
|app_project_name|Projet ArgoCD où créer l’application. Le projet devrait déjà exister, si non, le workflow ne continue pas.|✅|—|
|app_name|Nom de l’application ArgoCD|✅|—|
|app_dest_namespace|Namespace cible sur Kubernetes|❗|argocd|
|app_manifest_repo|Repo Git contenant les manifests Helm/Kustomize|✅|—|
|app_manifest_repo_branch|CBranche du repo|❗|main|
|app_manifest_path|Chemin dans le repo vers les manifests|✅|—|
|helm_params|Paramètres Helm au format "key1=val1,key2=val2"|❗|vide|

## Comportement général

1. Configure AWS via aws-actions/configure-aws-credentials.
2. Récupère le secret ArgoCD admin depuis AWS Secrets Manager.
3. Vérifie que la clé existe dans le secret.
4. Installe le CLI ArgoCD si absent.
5. Login au serveur ArgoCD.
6. Vérifie si le projet ArgoCD existe — sinon arrête le workflow.
7. Vérifie si l’application existe ; si non :
8. construit la commande argocd app create
9. applique les paramètres helm si fournis
10. crée l’application
11. Attend que l’application devienne Healthy.

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
        uses: ./.github/actions/create-argocd-app
        with:
          role_to_assume: arn:aws:iam::111111111111:role/MyRole
          argocd_server: argocd.example.com
          sm_argocd_admin_creds_secret_name: argocd/admin
          sm_argocd_admin_creds_secret_key: password
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

- AWS Actions
    - aws-actions/configure-aws-credentials@v4
    - aws-actions/aws-secretsmanager-get-secrets@v1
- ArgoCD CLI
    - installé automatiquement si absent
- Accès au :
    - rôle IAM fourni
    - secret dans AWS Secrets Manager
    - serveur ArgoCD

## Troubleshooting

❌ "Error: secret not found"
    
    Le secret ou la clé n’existe pas dans AWS Secrets Manager.

❌ "project does not exist, exit workflow" 
    
    Le projet ArgoCD n’a pas été créé par l’administrateur.

❌ Login échoue

    Vérifie :
        l’URL du serveur (souvent --grpc-web doit être activé)
        le mot de passe extrait

❌ L’application ne devient jamais Healthy

    Augmente le timeout ou vérifie les resources Kubernetes.