# GHAS Prepare Fork

Action composite de preparation d'un fork, appelee dans les `steps` d'un workflow
d'administration de confiance. Elle n'est pas reservee au depot de bibliotheque.
Le caller fournit les permissions et le jeton ; aucun secret n'est lu implicitement
dans les reglages de la bibliotheque. Les scripts sont charges depuis
`github.action_path`, jamais depuis le code du fork ou le repertoire courant.

## Entrees

| Entree | Defaut | Description |
| --- | --- | --- |
| `target-repository` | Obligatoire | Fork GitHub actif, `OWNER/REPO` |
| `library-repository` | Obligatoire | Bibliotheque `OWNER/REPO` de la meme organisation |
| `library-sha` | Vide | SHA complet publie contenant les actions, obligatoire en preview/install |
| `github-token` | Obligatoire | Jeton court, limite au fork par le caller |
| `enable-security` | `false` | Demande explicite d'activation des produits, peut consommer des licences |
| `configure-variables` | `false` | Configure et relit `CODEQL_ENABLED` et `DEPENDENCY_REVIEW_ENABLED` |
| `files-mode` | `none` | `none`, `preview`, `install` |

Les booleens d'une action composite sont des chaines `true` ou `false`, pas des
types `workflow_call`. Toute autre valeur est refusee avant les appels API.

## Sorties

- `repository-id` : identifiant GitHub, utile pour distinguer les forks recrees
  sous le meme nom. Ce n'est pas un export automatique des preuves d'analyse.
- `proposal-branch` et `compare-url` : proposition creee/reutilisee en install,
  vides pour une inspection ou un preview sans proposition.

## Utilisation et permissions

Voir [prepare-fork.yml](../../exemples/ghas/prepare-fork.yml), a installer dans
un depot d'administration autorise. Il cree un jeton GitHub App pour la cible,
appelle l'action puis laisse `create-github-app-token` revoquer le jeton en fin
de job. Ne jamais placer ce workflow sur un declencheur de PR non fiable.

```yaml
- name: Prepare fork
  # Commit de migration publie et teste dans le fork pilote.
  uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/ghas-prepare-fork@8c108cedf0faa03e3ff6cf153ef1b62484a6d8c7
  with:
    target-repository: ORG/fork-de-test
    library-repository: ORG/bibliotheque
    github-token: ${{ steps.app-token.outputs.token }}
```

Le runner doit fournir Python 3.10+ et Bash (Ubuntu 24.04 convient).
L'action n'effectue aucun checkout. Une inspection/preview ne fait que des GET,
si les deux options de mutation restent `false`.

| Operation | Permissions du jeton |
| --- | --- |
| Inspection, preview | Administration read, Contents read |
| Activation | Administration write |
| Variables et verification | Variables write, Administration read, Contents read |
| Proposition de fichiers | Contents write, Workflows write |

Combiner les permissions requises si plusieurs options sont demandees.
L'action ne reduit pas elle-meme les droits du jeton fourni. L'exemple avec
`create-github-app-token@v2` herite des permissions d'installation pour les
variables, car cette version n'expose pas `permission-variables`. Limiter les
permissions de l'installation et toujours renseigner `owner` et `repositories`.
La cle PEM et l'ID de l'App restent dans le depot d'administration uniquement.

## Gardes et effets

L'action refuse une cible hors organisation, la bibliotheque elle-meme, un depot
non fork, archive, desactive ou resolu par GitHub sous un autre nom. Les requetes
de mutation sont precedees d'une nouvelle verification du fork.

Ordre : inspection, activation explicite, variables explicites, fichiers.
Une activation incomplete arrete les operations suivantes. Les mutations deja
acceptees ne sont pas annulees ; verifier le resume avant toute relance.
`not reported` ne signifie pas desactive. Les politiques et licences restent
imposees par GitHub. Le probe Dependency Review compare un commit a lui-meme :
il prouve l'acces, pas une detection ; une variable `false` peut etre un resultat
normal et garde le controle correspondant desactive.

`install` cree un seul commit dans `feature/ghas-setup-...`, sans fusion ni mise
a jour de la branche par defaut. Les fichiers generes appellent les actions
composites au `library-sha` fourni. Fournir un commit contenant effectivement les
actions, pas un ancien commit de workflows seulement. Dependabot existant est
preserve. Aucun deploiement, suppression de fork ou analyse distante n'est lance.

## Migration et limites

Les anciens workflows `.github/workflows/ghas-*.yml` sont des adaptateurs
temporaires. Les nouveaux depots doivent appeler les actions depuis leurs jobs.
Les anciens workflows possedent des preuves historiques distinctes. Le preview,
l'installation sur une branche et la verification des variables de cette action
ont ete testes sur le fork cluster : voir les
[preuves composites](../../exemples/ghas/preuves/composite-actions-validation.md)
et le [plan de test](../../exemples/ghas/migration-actions.md).
Les registres prives et langages compiles exigent des adaptations. Avant de
fusionner une proposition dans un fork, verifier les regles GitFlow, desactiver
les workflows de deploiement herites et activer les mises a jour de versions
Dependabot. Exporter les preuves dans un emplacement approuve avant suppression
du fork ; leurs liens GitHub seuls ne seront plus suffisants.
