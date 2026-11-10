# Migration vers des actions composites

Etat du 2026-11-10 : migration publiee sur la branche de travail et tests GitHub
realises sur le fork cluster. Le nettoyage final (retrait du workflow temporaire,
references figees et preuves) est prepare localement, a publier puis faire revoir.
Voir les [resultats exportes](./preuves/composite-actions-validation.md).

## Architecture

- `actions/ghas-codeql/` : validation du langage, init et analyse CodeQL.
- `actions/ghas-dependency-review/` : contexte PR, seuil et controle des dependances.
- `actions/ghas-prepare-fork/` : inspection, activation, variables et fichiers via API.
- `exemples/ghas/security.yml` : orchestration possedee par le depot analyse.
- `exemples/ghas/prepare-fork.yml` : orchestration et credentials du depot d'administration.
- `.github/workflows/ghas-*.yml` : adaptateurs temporaires, sans logique metier dupliquee.
- `.github/workflows/ghas-toolkit-tests.yml` : CI propre a la bibliotheque, sans App.

Les anciens appels workflow_call continuent d'exister ; ils deleguent aux actions.
Les nouveaux consumers utilisent `jobs.<job>.steps[].uses`, pas
`jobs.<job>.uses`. Les regles de branche doivent etre revues si les noms de
controles changent. Aucun workflow de deploiement n'est ajoute.

## References de livraison

Les exemples, README et adaptateurs appellent les nouvelles actions au SHA
publie et teste `8c108cedf0faa03e3ff6cf153ef1b62484a6d8c7`, sans reference a la
branche de travail. Les anciens commits du pilote ne contiennent pas ces actions.
Un futur changement d'implementation exige un nouveau SHA valide ; les commits
de nettoyage de documentation ne modifient pas le code des actions teste ici.

Les fichiers generes utilisent deja les actions par SHA complet ; verifier que
le SHA fourni contient effectivement les trois dossiers d'action. Un pin de
l'action externe ne fige pas automatiquement les actions tierces qu'elle appelle ;
ces dependances restent a maintenir.

## Tests locaux

Installer `tests/ghas/requirements.txt` dans un environnement Python de test,
puis executer `python3 -m unittest discover -s tests/ghas -v`.
Les tests ne font aucun appel reseau ni aucune activation GitHub.

Ils couvrent le format composite, les shells et entrees, les exemples appelants,
le refus de pull_request_target pour Dependency Review, les permissions declarees,
l'absence de cle App dans le scan, les validations de cible, les activations
partielles/refusees, les variables et le generateur.

Ces tests ne remplacent pas une execution reelle : CodeQL et Dependency Review
sont des actions tierces executees uniquement sur GitHub pendant le pilote.

Verification locale du 2026-11-05 : 36 tests reussis dans un environnement
Python isole. `actionlint` 1.7.7 ne signale aucune erreur sur les trois
adaptateurs, la CI, les deux exemples et un workflow genere avec une matrice
Actions/Python. Les verifications ShellCheck et Pyflakes d'actionlint sont
desactivees ; les gardes Bash sont executees directement par les tests.
L'entree CLI historique a aussi ete lancee depuis un repertoire etranger avec
`--help`, sans checkout de la bibliotheque dans le workspace appelant.

Le nettoyage final ajoute des tests empechant une livraison avec un workflow
pilote temporaire ou des references mutables aux actions de bibliotheque.
Verification du 2026-11-10 : les 38 tests reussissent. Actionlint 1.7.7 valide
les trois adaptateurs, la CI et les deux exemples sans erreur, avec les memes
limites ShellCheck/Pyflakes decrites ci-dessus. Aucun commit ou push de ce
nettoyage final n'a ete effectue par l'agent.

## Parcours GitHub de reproduction

1. Conserver le fork cluster licencie et exporter les preuves existantes.
   Aucun vrai secret ni droit AWS n'est necessaire pour le scan.
2. Publier la migration sur la branche de travail de la bibliotheque, sans fusion.
   Attendre la CI puis relever son SHA complet.
3. Dans le fork, creer une branche depuis dev. Remplacer les appels workflow_call
   de `ghas-security.yml` par les jobs de l'exemple security, avec les deux actions
   figees au nouveau SHA. Adapter matrice/branches, conserver les variables existantes.
4. Ouvrir une PR vers dev du fork uniquement. Verifier CodeQL Actions et Python,
   l'envoi SARIF et Dependency Review. Conserver SHA, URL des jobs et conclusions.
5. Dans cette PR de test, ajouter temporairement le manifeste inerte
   `security-tests/dependency-review/requirements.txt` avec `requests==2.19.1`.
   Ne pas l'installer, ne pas le fusionner. Verifier le rejet pour vulnerabilites,
   retirer ce fichier, verifier le retour au vert.
6. Verifier une analyse CodeQL manuelle et les alertes sur la bonne branche.
   Pour une preuve controlee de detection, reprendre la fixture Actions inerte
   du test historique puis sa correction par SHA, sans executer l'action de test.
7. Dans un depot d'administration autorise, installer prepare-fork et ne donner
   la cle App qu'au job manuel de confiance. Verifier d'abord inspection/preview :
   les mutations doivent rester false. Verifier l'ID de la cible et aucun changement.
8. Tester install avec le nouveau SHA, revoir la proposition sur sa branche et
   constater que dev n'est pas modifiee. Sur le fork deja active, tester ensuite
   configure-variables explicitement et verifier les valeurs relues. Ne pas
   demander une activation facturable sur un autre fork sans autorisation.
9. Verifier aussi les adaptateurs historiques encore utilises. Documenter les
   differences de resumes et les nouveaux noms de jobs.
10. Apres reussite, figer les references de migration, relire la PR de bibliotheque
    et demander approbation. Ne supprimer les adaptateurs qu'apres migration des consumers.

Le test Secret Scanning/Push Protection reste une preuve historique du service
GitHub, pas une fonction locale de l'action CodeQL. Une nouvelle configuration
d'administration doit verifier les reglages reels sans supposer leur activation.

Les etapes 3 a 5 sont constatees dans la PR 12, puis le nettoyage de dev dans la
PR 13. Preview, install et variables ont ete executes via trois runs distincts
du workflow temporaire, avec la meme action figee au SHA teste. Ce workflow est
retire pour la livraison ; les prochains tests passent par le workflow manuel
d'administration. L'activation facturable, un nouveau test controle CodeQL et un
run planifie ne sont pas prouves par ces runs : ne pas les annoncer comme faits.

## Revue finale

1. Publier le nettoyage final et attendre les controles de la PR 38.
2. Faire revoir les actions, les permissions de l'App et les metadonnees de forks
   prives conservees dans la bibliotheque publique.
3. Confirmer le perimetre accepte : pilote sur fork, pas activation sur le depot source.
4. Apres approbation et fusion, verifier le lancement manuel en lecture seule.
   Ne pas relancer les anciens runs temporaires : ils conservent leurs options,
   y compris les permissions d'installation et de gestion des variables.

## Points non automatises

L'action ne cree ni ne supprime le fork, n'active pas les mises a jour de versions
Dependabot sur un nouveau fork, ne configure pas les protections de branche et
ne garantit pas le nombre de licences. Les registres prives et langages compiles
demandent des profils adaptes. Si un fork est supprime, conserver des exports
avant suppression ; un lien vers une alerte ou un job supprime ne suffit pas.
