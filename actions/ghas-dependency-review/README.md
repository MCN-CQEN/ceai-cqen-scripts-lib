# GHAS Dependency Review

Action composite reutilisable dans les `steps` d'un job de Pull Request.
Elle appelle `actions/dependency-review-action` et propage son echec lorsqu'une
dependance introduite atteint le seuil choisi.

## Entrees

| Entree | Defaut | Description |
| --- | --- | --- |
| `fail-on-severity` | `low` | `low`, `moderate`, `high` ou `critical` |
| `repo-token` | `github.token` | Jeton du depot appelant, normalement son `GITHUB_TOKEN` |

## Appel

Le workflow appelant definit `on: pull_request`, `runs-on`, le checkout et
`permissions: contents: read`. Si plusieurs evenements sont presents, le job
doit porter `if: github.event_name == 'pull_request'`.

```yaml
steps:
  - uses: actions/checkout@v7.0.0
    with:
      persist-credentials: false
  # Commit de migration publie et teste dans le fork pilote.
  - uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/ghas-dependency-review@8c108cedf0faa03e3ff6cf153ef1b62484a6d8c7
    with:
      fail-on-severity: low
```

Voir [l'exemple complet](../../exemples/ghas/security.yml). L'action refuse
les appels hors `pull_request`, y compris `pull_request_target` : ne pas
executer du code de PR avec des secrets d'administration.

## Prerequis et limites

Dependency graph et eligibility Dependency Review doivent etre verifies sur le
depot. L'action ne les active pas, ne gere pas Dependabot et ne cree pas de regle
de fusion obligatoire. Un controle vert ne prouve pas l'absence de vulnerabilites
deja presentes hors des changements de la PR. Aucun token de la GitHub App ni
cle privee n'est necessaire ici.
