# Actions GHAS reutilisables

Le kit suit la structure des autres bibliotheques du depot : chaque composant
reutilisable possede un `action.yml` composite et un README sous `actions/`.
Les workflows des depots consommateurs appellent ces actions dans leurs steps.

## Composants

| Action | Responsabilite | Documentation |
| --- | --- | --- |
| `actions/ghas-codeql` | Init et analyse du code checkout, un langage par job | [README](../../actions/ghas-codeql/README.md) |
| `actions/ghas-dependency-review` | Controle des dependances introduites par une PR | [README](../../actions/ghas-dependency-review/README.md) |
| `actions/ghas-prepare-fork` | Inspection et preparation explicite d'un fork via API | [README](../../actions/ghas-prepare-fork/README.md) |

Les actions ne declarent ni evenements, ni runner, ni permissions de job.
Ces choix appartiennent au workflow appelant, de meme que le checkout,
la matrice, les conditions et les secrets. Aucune action de scan n'a besoin
de la cle GitHub App, d'un environnement AWS ou de `secrets: inherit`.

## Exemples appelants

- [security.yml](./security.yml) : workflow a installer dans le fork analyse.
  CodeQL tourne sur PR, push vers les branches choisies, calendrier et lancement
  manuel ; Dependency Review est limite aux PR.
- [prepare-fork.yml](./prepare-fork.yml) : workflow manuel a installer dans un
  depot d'administration de confiance. Il fournit le jeton cible a l'action
  de preparation. La cle PEM reste dans ce depot d'administration, pas dans les forks.

Les exemples et adaptateurs appellent les actions au commit teste
`8c108cedf0faa03e3ff6cf153ef1b62484a6d8c7`. Le generateur utilise aussi un SHA
complet. Fournir un commit contenant les trois actions dans `library-sha` ;
un ancien commit ne contenant que les workflows ne convient pas. Une evolution
des actions exige une nouvelle validation et une mise a jour deliberee des SHA.

## Preparation d'un nouveau fork

1. Creer manuellement le fork dans la meme organisation que la bibliotheque.
2. Autoriser la GitHub App sur cette nouvelle cible. Une recreation sous le meme
   nom cree un nouveau depot : reverifier l'installation et conserver son ID.
3. Dans le depot d'administration, configurer `GHAS_APP_ID` (variable) et
   `GHAS_APP_PRIVATE_KEY` (secret PEM), puis limiter le jeton au fork cible.
4. Lancer une inspection/preview : `enable-security: false`,
   `configure-variables: false`, `files-mode: preview`.
   Fournir dans `library-sha` un commit publie contenant les nouvelles actions.
5. Examiner le resume, les langages et manifestes proposes. Les fichiers sont
   seulement proposes, pas installes. Revoir licences, politiques et permissions.
6. Apres autorisation, demander separement ou ensemble l'activation, les variables
   et `files-mode: install`. Une activation incomplete arrete les operations
   suivantes dans la nouvelle action ; les mutations deja acceptees restent.
7. Examiner la branche `feature/ghas-setup-...`. Desactiver les workflows de
   deploiement herites et verifier les regles GitFlow avant toute fusion.
8. Installer les fichiers dans le fork selon votre procedure de PR ; activer les
   mises a jour de versions Dependabot sur le fork. L'action ne les active pas.
9. Verifier les analyses et les alertes dans le depot analyse. Un job vert prouve
   l'execution, pas l'absence de risques ni un blocage obligatoire de fusion.
10. Exporter les preuves dans un emplacement approuve avant toute suppression
    du fork. Les liens seuls ne permettent plus de les consulter apres suppression.

Voir [preparation multi-depot](./preparation-multidepot.md) pour l'inventaire,
les propositions et les limites. Les licences ne sont pas garanties par le nom
ou la creation manuelle d'un fork ; aucune politique d'entreprise n'est contournee.

## Compatibilite temporaire

Les workflows `.github/workflows/ghas-codeql.yml`,
`ghas-dependency-review.yml` et `ghas-prepare-fork.yml` restent presents comme
adaptateurs pour les appels existants. Leur logique est deleguee aux actions ;
ils ne sont plus l'interface conseillee pour les nouveaux depots.
Le workflow de preparation historique conserve le bouton manuel apres
integration, mais reste limite a la bibliotheque pour la gestion de ses credentials.
Un autre depot d'administration utilise directement l'action composite.

Le script `scripts/ghas/prepare_files.py` reste une entree CLI de compatibilite.
L'implementation est maintenant dans `actions/ghas-prepare-fork/`.
Aucun workflow pilote automatique specifique a un fork n'est ajoute.

## Validation et exploitation

Le [plan de migration et de tests](./migration-actions.md) et la
[preuve des actions composites](./preuves/composite-actions-validation.md)
decrivent les tests locaux et distants realises ainsi que les limites restantes.
Les anciennes preuves restent des observations historiques distinctes.

- [Bilan historique du pilote](./bilan-validation.md)
- [Validation des actions composites et donnees exportees](./preuves/composite-actions-validation.md)
- [Traitement des alertes](./traitement-alertes.md)
- [CodeQL : detection et correction](./preuves/codeql-controlled-test.md)
- [Secret Scanning et Push Protection](./preuves/secret-scanning-controlled-test.md)
- [Dependency Review : detection et retour au vert](./preuves/dependency-review-controlled-test.md)
- [Dependabot et controles sur PR](./preuves/dependabot-validation.md)
- [Deuxieme fork et blocage de facturation](./preuves/preparation-projects.md)

Les metadonnees de forks prives ne doivent etre publiees dans cette bibliotheque
publique qu'apres autorisation. Les langages compiles, registres prives et
manifestes non reconnus demandent une adaptation. Le prototype ne garantit pas
l'analyse de tous les projets sans revue.

## References

- [Actions composites](https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action)
- [Options Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
- [API Dependency Review](https://docs.github.com/en/rest/dependency-graph/dependency-review)
