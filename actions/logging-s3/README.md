# Journalisation des logs des tests et des déploiements

Ce workflow GitHub Actions permet d’enregistrer les logs des tests et des déploiements dans un bucket Amazon S3.

Il est conçu pour être déclenché par d'autres workflows via l’événement workflow_call.
Les logs générés, au format JSON, facilitent le suivi historique des exécutions à travers divers environnements (production, staging, etc.).

## 🧭 Table des matières

- [Fonctionnalités](./README.md#-fonctionnalités)
- [Schéma du fonctionnement](./README.md#-schéma-du-fonctionnement)
- [Inputs](./README.md#-inputs)
- [Installation](./README.md#-installation)
- [Utilisation](./README.md#️-utilisation)
- [Exemple de fichier JSON généré](./README.md#-exemple-de-fichier-json-généré)
- [Dépendances](./README.md#-dépendances)
- [Notes de sécurité](./README.md#-notes-de-sécurité)
- [Troubleshooting](./README.md#-troubleshooting)

## ✨ Fonctionnalités

- Enregistrement de logs détaillés (workflow, statut, message, environnement…)
- Génération automatique d’un fichier JSON propre via jq
- Upload sécurisé vers un bucket S3 via un rôle IAM assumé
- Nettoyage automatique des fichiers temporaires
- Utilisation simple via workflow_call depuis n’importe quel autre workflow

## 🔧 Schéma du fonctionnement

1. Le workflow est déclenché par un autre workflow.
2. Il configure des identifiants AWS via un rôle IAM fourni.
3. Il génère un fichier log.json contenant les métadonnées de l’exécution.
4. Il envoie ce fichier dans :
    ```bash
    s3://<bucket>/logs/<workflow>/run-<run_id>.json
    ```
5. Il nettoie les fichiers temporaires.

## 📝 Inputs

| Nom de l’input | Description | Obligatoire |
|------|--------|---------|
|bucket	| Nom du bucket S3 où stocker les logs |✅|
|region|Région AWS du bucket|✅|
|role_to_assume|ARN du rôle IAM à assumer|✅|
|status|Statut de l’exécution (success, failure, etc.)|✅|
|message|Message descriptif (Tests réussis, Déploiement échoué, etc.)|✅|
|workflow|Nom du workflow appelant|✅|
|environment|Environnement (production, staging, etc.)|✅|

## 📦 Installation

Placez le fichier du workflow dans :
```bash
.github/workflows/logs-to-s3.yml
```
Le workflow pourra ensuite être appelé par d’autres workflows.

## ▶️ Utilisation

Exemple de workflow appelant ce module :

```yaml
name: Tests CI

on:
  push:
    branches: ["main"]

jobs:
  run-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: echo "Tests réussis"

      - name: Log tests
        uses: ./.github/workflows/logs-to-s3.yml
        with:
          bucket: my-logs-bucket
          region: ca-central-1
          role_to_assume: arn:aws:iam::123456789012:role/github-logs-writer
          status: success
          message: "Tests réussis"
          workflow: "Tests CI"
          environment: "staging"

```

## 📄 Exemple de fichier JSON généré

```json
{
  "workflow": "Tests CI",
  "status": "success",
  "message": "Tests réussis",
  "environment": "staging",
  "timestamp": "2025-01-01T12:00:00Z",
  "run_id": "1234567890",
  "actor": "octocat",
  "event_name": "push",
  "repository_owner": "my-org",
  "repository_name": "my-repo",
  "repository_full_name": "my-org/my-repo"
}
```

## 🧩 Dépendances

- GitHub Actions aws-actions/configure-aws-credentials@v6.2.2
- AWS CLI installé dans le runner
- jq pour générer le fichier JSON
- Rôle IAM avec permissions sts:AssumeRole et s3:PutObject

## 🔐 Notes de sécurité

- Le rôle IAM fourni doit être limité uniquement à l’écriture dans le répertoire S3 concerné.
- Évitez de stocker des informations sensibles dans les messages de logs.
- Privilégiez l’utilisation de l’authentification OIDC GitHub → AWS au lieu de clés statiques.

## ❗ Troubleshooting

| Problème | Cause probable | Solution |
|------|--------|---------|
|Erreur `AccessDenied` AWS|Le rôle IAM n’a pas les permissions nécessaires|Vérifier `s3:PutObject` et le trust policy|
|jq: `command not found`|Runner sans `jq`|Utiliser une image contenant `jq` ou installer manuellement|
|Le fichier ne se trouve pas dans S3|Mauvaise clé ou chemin configuré|Vérifier le bucket, le préfixe et les inputs|
