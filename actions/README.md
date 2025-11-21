# Scripts communs pour GitHub Actions

## Introduction
L'objectif de ce repo est la réutilisation des scripts génériques et nécessaires pour l’automatisation dans GitHub Actions.

Il existe deux manières de réutiliser des scripts:
- workflows réutilisables
- composite actions

### Composite actions
Une composite action dans GitHub Actions est une manière de regrouper plusieurs étapes d'un workflow en une seule action réutilisable. Cela permet de simplifier et de centraliser des tâches communes, tout en évitant la duplication de code dans différents workflows.

#### Fonctionnement des composite actions

1. **Structure d'une composite action** :
   - Une composite action est définie dans un fichier `action.yml` ou `action.yaml`.
   - Elle contient une liste d'étapes (`steps`) qui seront exécutées dans l'ordre.

2. **Fichier `action.yml`** :
   - Ce fichier décrit l'action, ses entrées (`inputs`), ses sorties (`outputs`), et les étapes nécessaires pour accomplir la tâche.

3. **Exemple de fichier `action.yml`** :
   Voici un exemple simple d'une composite action qui exécute deux commandes shell :

   ```yaml
   # filepath: actions/exemple/action.yml
   name: "My Composite Action"
   description: "Une action composite pour démonstration"
   inputs:
     example-input:
       description: "Une entrée d'exemple"
       required: true
   outputs:
     example-output:
       description: "Une sortie d'exemple"
       value: ${{ steps.step2.outputs.result }}
   runs:
     using: "composite"
     steps:
       - name: Étape 1
         run: echo "Entrée reçue: ${{ inputs.example-input }}"
       - name: Étape 2
         id: step2
         run: echo "Résultat de l'action" && echo "result=success" >> $GITHUB_OUTPUT
   ```

4. **Utilisation dans un workflow** :
   Une fois la composite action créée, elle peut être utilisée dans un workflow comme suit :

   ```yaml
   # filepath: <app-repo>/.github/workflows/exemple.yml
   name: "Exemple de Workflow"
   on:
     push:
       branches:
         - main
   jobs:
     example-job:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout du code
           uses: actions/checkout@v3
         - name: Utiliser l'action composite
           uses: MCN-CQEN/ceai-cqen-commons/actions/exemple@feature/actions
           with:
             example-input: "Bonjour"
   ```

#### Avantages des composite actions :
- **Réutilisabilité** : Centralise les scripts communs pour les utiliser dans plusieurs workflows.
- **Maintenance simplifiée** : Les modifications dans l'action composite se propagent automatiquement à tous les workflows qui l'utilisent.
- **Lisibilité** : Réduit la complexité des workflows en déléguant des tâches à des actions composites.

Pour plus de détails, consultez la [documentation officielle de GitHub sur les composite actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action).


#### Création d'un script
Pour la création d'un script:
- Dans ce repertoire, ajoutez un dossier qui décribe le propos de l'action (i.e.: build-image)
- Dans le dossier créé, ajoutez un fichier action.yml et ajoutez les étapes à suivre comme indiqué dans l'exemple (section 3).

## Liste de scripts Créés

| Nom | Description | Documentation | Fichier |
|------|--------|---------|---------|
|Create ArgoCD Application | Permet d’automatiser la création d’une application Argo CD si elle n’existe pas déjà. | [Readme](./create-argocd-app/README.md) | [action](./create-argocd-app/action.yml) |
|Gitflow | Workflows réutilisables facilitant la mise en oeuvre du GitFlow dans les dépôts de code du CQEN | [Readme](./gitflow/README.md) | [plusieurs fichiers, voir répértoire](./gitflow/README.md) |
|Pulish image to registry| Publie une image au registre des conteneurs d'images | [Readme](./publish-image-to-registry/README.md) | [action](./publish-image-to-registry/action.yml)|


## Références
- [GitHub Docs - Composite Actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action)