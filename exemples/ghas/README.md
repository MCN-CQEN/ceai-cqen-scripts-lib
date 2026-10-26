# Kit GHAS - premiere etape

Cette premiere version centralise CodeQL et Dependency Review. Elle ne cree pas
de fork, ne modifie pas les reglages GitHub et ne cree aucune variable.

## Bibliotheque

Les workflows `.github/workflows/ghas-codeql.yml` et
`.github/workflows/ghas-dependency-review.yml` utilisent `workflow_call` uniquement.
Ils ne se declenchent pas automatiquement dans la bibliotheque. Le checkout
recupere le depot appelant et les resultats sont associes a ce depot.

Le pilote CodeQL couvre `actions` et `python`. Le parametre `languages` est un
tableau JSON. Les langages necessitant une compilation devront faire l'objet
d'un profil de construction adapte avant utilisation ; cette version ne fournit
pas d'etape de compilation. Les suites de requetes sont centralisees directement
dans le workflow, sans fichier de configuration externe prive a telecharger.

Dependency Review ne s'execute que sur une pull request. Son seuil par defaut
est `low`, donc toute vulnerabilite connue introduite peut faire echouer le job.
Un controle obligatoire doit etre configure separement dans les regles de branche.

## Essai dans le fork

1. Publier la branche `feature/ghas-toolkit` de la bibliotheque.
2. Dans les reglages de la bibliotheque privee, autoriser son utilisation depuis
   les depots de l'organisation : `Settings > Actions > General > Access`.
   Verifier aussi que les politiques Actions du fork autorisent ces workflows.
3. Verifier que Code Security et le dependency graph sont effectivement actifs
   dans le fork. Une politique d'entreprise ou une licence manquante reste bloquante.
4. Installer `security.yml` sous `.github/workflows/ghas-security.yml` dans le fork.
   Remplacer les anciens workflows GHAS equivalents pour eviter les analyses
   dupliquees. Ne pas installer ce fichier dans le depot source.
5. Pour cet essai initial, definir les variables de depot `CODEQL_ENABLED` et
   `DEPENDENCY_REVIEW_ENABLED` a `true` uniquement lorsque leurs prerequis sont
   satisfaits. Leur creation automatique sera ajoutee au workflow de preparation.
   L'ancienne variable `GHAS_ENABLED` n'est pas utilisee par ce nouvel exemple.
6. Ouvrir une PR dans le fork pour tester les deux controles. Une execution
   manuelle teste CodeQL uniquement. Le workflow doit exister sur la branche par
   defaut pour etre lance depuis l'interface et pour les executions planifiees.
7. Consulter les jobs de la PR et `Security > Code scanning` dans le fork.
   Un job reussi sans alerte ne prouve pas la detection d'un probleme controle.

Les references a `feature/ghas-toolkit` servent au pilote. Apres validation,
les remplacer par un SHA de commit valide ou une version publiee de la bibliotheque.
Aucun secret AWS, environnement de deploiement ou `secrets: inherit` n'est requis.
Les workflows d'infrastructure herites doivent rester desactives dans le fork
de test ; cette premiere etape ne les desactive pas automatiquement.

## Etapes suivantes

- Workflow central recevant le nom d'un fork deja cree manuellement.
- Authentification centrale et verification des depots cibles autorises.
- Installation des fichiers, adaptation de Dependabot et creation des variables.
- Activation des fonctions autorisees et rapport des blocages.
- Tests de detection controles et collecte des preuves.

Secret scanning et Dependabot restent des services propres au fork ; ces deux
workflows reutilisables ne les activent pas. Le nombre de licences n'est pas
garanti par la creation manuelle du fork.

## References

- [Workflows reutilisables](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
- [Partage dans l'organisation](https://docs.github.com/en/actions/how-tos/reuse-automations/share-with-your-organization)
