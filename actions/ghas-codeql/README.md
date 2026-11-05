# GHAS CodeQL

Action composite reutilisable dans les `steps` d'un job du depot appelant.
Elle initialise CodeQL et analyse le code deja checkout, sans checkout de la
bibliotheque, sans acces AWS et sans secret d'administration.

## Entrees

| Entree | Defaut | Description |
| --- | --- | --- |
| `language` | Obligatoire | Un langage : `actions`, `python`, `ruby`, `javascript-typescript` |
| `queries` | `security-extended,security-and-quality` | Suites CodeQL |
| `category` | `/language:<language>` | Categorie SARIF, a personnaliser pour des analyses distinctes |

## Appel

Voir [security.yml](../../exemples/ghas/security.yml) pour un workflow complet.
Le job appelant declare les evenements, le runner, le timeout, le checkout et
les permissions `actions: read`, `contents: read`, `security-events: write`.
La matrice appartient au workflow appelant : un langage par job.

```yaml
steps:
  - uses: actions/checkout@v7.0.0
    with:
      persist-credentials: false
  # Branche pour les tests de migration ; figer au SHA publie avant livraison.
  - uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/ghas-codeql@feature/ghas-toolkit
    with:
      language: python
```

## Prerequis et limites

Runner Linux avec Bash, Code Security disponible sur le depot et Actions
autorisees. Ne pas donner de credentials privilegies au job d'analyse.
Cette version refuse les langages compiles : un profil de build et une separation
init/build/analyze devront etre ajoutes avant leur prise en charge. Elle ne
configure ni GHAS ni les protections de branche. Le succes du job ne garantit
pas l'absence d'alertes ; consulter Code scanning sur le depot appelant.
