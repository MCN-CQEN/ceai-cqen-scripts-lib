# Kit GHAS - premiere etape

Cette version centralise CodeQL et Dependency Review. Elle fournit une inspection
du fork et un mode explicite d'activation des fonctions de securite. Elle ne cree
pas de fork ni de variable.

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
2. La bibliotheque est publique : aucun partage de workflows prives n'est requis.
   Verifier que les politiques Actions du fork autorisent ces workflows.
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

## Verification centrale de la GitHub App

Le workflow `.github/workflows/ghas-prepare-fork.yml` fournit par defaut une
inspection en lecture seule. Le mode d'activation exige `enable_security: true`.
Il ne cree ni variable ni fichier. Il exige un veritable fork GitHub appartenant a la meme organisation
que la bibliotheque ; une copie independante du code sera refusee.

Configurer une fois dans les reglages Actions de la bibliotheque :

- Variable de depot `GHAS_APP_ID` : identifiant numerique de l'application.
- Secret de depot `GHAS_APP_PRIVATE_KEY` : contenu complet de la cle PEM.
- Installation de l'application autorisee sur le fork cible, avec au minimum
  les permissions Administration et Contents en lecture pour cette inspection.

Le jeton temporaire est limite au seul depot saisi et aux permissions de lecture
demandees, puis revoque par l'action de creation du jeton en fin de job.

### Test avant fusion

Un push sur `feature/ghas-toolkit` modifiant
`.github/workflows/ghas-prepare-fork.yml` lance automatiquement l'inspection du
fork pilote `MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`. Ce declencheur permet de
tester l'authentification sans fusionner la PR. Aucun parametre manuel n'est
disponible sur cet evenement ; la cible du pilote est utilisee explicitement.
Un push modifiant uniquement la documentation ne declenche pas cette inspection.
Consulter l'execution sur cette branche dans Actions et son resume. Cette
inspection ne lance pas CodeQL ou Dependency Review et ne modifie pas le fork.

### Activation explicite avant fusion

Le workflow `.github/workflows/ghas-pilot.yml` appelle le workflow de preparation
depuis le meme commit. Il s'execute uniquement lorsqu'un push sur
`feature/ghas-toolkit` modifie ce fichier pilote. Par defaut, `enable_security`
vaut `false` et seule l'inspection est executee.

Pour demander l'activation sans fusionner la PR, verifier la cible dans ce fichier,
passer explicitement `enable_security` a `true`, puis committer et pousser ce
changement. Cette operation peut consommer des licences. Elle exige la permission
Administration en ecriture de l'application et l'approbation des permissions
sur son installation. Le token d'activation est limite au fork et a cette permission.

Le job d'activation tente d'activer Code Security, Secret scanning, puis Push
protection, et relit les reglages. Il ne contourne pas les politiques de
l'entreprise ou la facturation. Le resume `GHAS activation` presente les etats
avant/apres et les requetes acceptees ou refusees. Un refus HTTP peut avoir
plusieurs causes ; le code ne presume pas laquelle. En cas de propagation differee,
verifier les reglages et relancer apres confirmation. Les fonctions deja actives
ne sont pas desactivees et une activation partielle n'est pas annulee.

Apres le test, remettre `enable_security: false` dans le pilote et pousser cette
modification pour revenir aux inspections. Cela ne desactive pas les produits
deja actives sur le fork. Une reexecution d'un ancien run conserve son ancien
parametre : ne pas relancer un run d'activation pour effectuer une inspection.
Ce pilote devra etre retire avant l'integration finale de la bibliotheque.

### Lancement manuel apres integration

Pour rendre le bouton `Run workflow` disponible, le fichier de preparation doit
exister sur la branche par defaut de la bibliotheque. Apres publication de la
branche de travail, integrer ce fichier par la procedure de revue habituelle.
Depuis Actions, lancer `GHAS - Prepare existing fork` avec
`MCN-CQEN/ceai-cqen-labinfra-cluster-ghas` comme cible. Consulter le resume de
l'execution pour les etats renvoyes par GitHub.

Laisser `enable_security` decoche pour une inspection, ou le cocher pour demander
l'activation apres verification des licences et de la cible.

Un succes confirme l'authentification, l'acces et le lien de fork, pas l'activation
GHAS ou les permissions d'ecriture. `not reported` signifie que GitHub n'a pas
fourni l'etat, et non que la fonction est desactivee. Les politiques et licences
restent a verifier avant toute activation. Aucun jeton ni cle ne doit etre copie
dans les journaux ou le depot.

## Etapes suivantes

- Installation des fichiers, adaptation de Dependabot et creation des variables.
- Activation des fonctions autorisees et rapport des blocages.
- Tests de detection controles et collecte des preuves.

Secret scanning et Dependabot restent des services propres au fork ; ces deux
workflows reutilisables ne les activent pas. Le nombre de licences n'est pas
garanti par la creation manuelle du fork.

## References

- [Workflows reutilisables](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
- [Partage dans l'organisation](https://docs.github.com/en/actions/how-tos/reuse-automations/share-with-your-organization)
