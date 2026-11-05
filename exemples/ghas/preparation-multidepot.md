# Preparation de plusieurs forks

L'action `actions/ghas-prepare-fork` recoit une cible explicite
`target-repository: ORG/fork` et un jeton fourni par le workflow appelant.
Ce jeton doit etre limite au seul fork. La cible doit etre un fork actif de la
meme organisation que `library-repository`, pas un depot source ni la bibliotheque.

Le code du fork n'est jamais checkout ou execute. Les scripts distribues avec
l'action sont appeles par `github.action_path`. Il n'est pas necessaire de
checkout la bibliotheque dans le depot appelant.

## Responsabilites du caller

Le [workflow d'exemple](./prepare-fork.yml) est installe dans un depot
d'administration de confiance, pas dans les analyses de PR. Il definit le
declenchement manuel, le runner, les permissions, les secrets, la creation du
jeton et la concurrence par cible. Ne pas lancer deux cycles de recreation du
meme fork en parallele.

La cle PEM reste un secret du depot d'administration. L'action recoit seulement
le jeton temporaire. Voir les [permissions detaillees](../../actions/ghas-prepare-fork/README.md).

## Options de l'action

| Option | Defaut | Effet |
| --- | --- | --- |
| `target-repository` | Aucun | Fork a preparer |
| `library-repository` | Aucun | Bibliotheque de la meme organisation |
| `library-sha` | Vide | SHA complet publie contenant les actions, obligatoire en preview/install |
| `enable-security` | `false` | Demande d'activation potentiellement facturable |
| `configure-variables` | `false` | Configure les variables apres verification |
| `files-mode` | `none` | `none`, `preview` ou `install` |

Les chaines booleennes doivent etre exactement `true` ou `false`. L'action
inspecte d'abord puis traite activation, variables et fichiers dans cet ordre.
Une activation incomplete fait echouer l'action et empeche les operations
suivantes. Les mutations deja acceptees ne sont pas annulees.
L'installation ne vaut pas activation ni reussite d'analyse.

## Inventaire

Le preview lit l'arbre de la branche par defaut du fork sans le modifier.
Il detecte Python, Ruby et JavaScript/TypeScript, et ajoute Actions pour le
workflow installe. Les langages compiles sont signales comme profils non
automatises, pas comme langages incompatibles avec CodeQL.

Dependabot est propose pour npm, pip, Bundler, Go modules, Maven, Gradle, Cargo,
Composer et NuGet reconnus par nom/extension, ainsi que les repertoires Terraform.
Les chemins sont derives du projet, sans chemins cluster imposes.
`vendor`, `node_modules`, `.venv`, `venv`, `dist` et `build` sont ignores.
Un arbre tronque ou plus de 100 couples ecosysteme/repertoire bloque la generation.

Cet inventaire reste une heuristique : uv, registres prives, sous-modules et
autres variantes demandent une revue. La presence d'un manifeste ne garantit
pas la couverture de ses vulnerabilites.

## Fichiers et proposition

Le generateur produit :

- `.github/workflows/ghas-security.yml` avec des jobs locaux : evenements,
  runners, permissions, matrice, checkout puis appels aux actions composites
  au `library-sha` fourni. Aucun appel de job a un workflow reutilisable.
- `.github/dependabot.yml`, sauf si `dependabot.yml` ou `dependabot.yaml`
  existe deja dans `.github`. Une configuration existante est preservee.

La serialisation JSON est un sous-ensemble valide de YAML ; les extensions
restent `.yml`. Les expressions GitHub Actions sont preservees.

Le mode install cree un commit dans
`feature/ghas-setup-<SHA-base-court>-<SHA-bibliotheque-court>`.
Le prefixe `feature/` convient au GitFlow du pilote cluster vers dev, pas
necessairement aux regles de tous les depots.
Une proposition identique est reusee ; une proposition modifiee est refusee
sans force-push. La branche par defaut n'est jamais mise a jour ou fusionnee.
Le generateur peut remplacer le workflow GHAS dans la proposition : examiner
le diff avant fusion. Il n'ouvre pas de PR et ne lance pas d'analyse distante.

Le mode preview ne cree ni commit, ni branche, ni blob ; il ne fait que des GET
si activation et variables restent desactivees. Les sorties `proposal-branch`
et `compare-url` sont vides dans ce cas.

## Installation et verifications

1. Publier un commit contenant les nouvelles actions. L'ancien SHA du pilote
   ne suffit pas. Pour les tests de migration, conserver la branche de travail ;
   avant livraison, figer aussi les appels des exemples/adaptateurs.
2. Installer l'exemple d'administration dans un depot autorise. Renseigner le
   fork cible et le SHA de bibliotheque, puis lancer preview avec les mutations
   desactivees.
3. Revoir le resume, les licences et la couverture. Lancer une nouvelle execution
   en install uniquement apres approbation.
4. Examiner la proposition, les anciens workflows de securite et les workflows
   d'infrastructure. Ces derniers ne sont pas desactives automatiquement.
5. Configurer explicitement les produits et variables si necessaire, sans
   demander d'activation sur le depot source. Dependabot version updates reste
   a activer sur chaque nouveau fork.
6. Tester les controles sur une PR et conserver les preuves par ID de depot,
   commit et date. Exporter avant suppression/recreation sous le meme nom.

Le resume publie des metadonnees : cible, ID, langages et nombres de repertoires.
Les journaux sont publics si le workflow appelant l'est. Utiliser un depot
d'administration prive pour les informations confidentielles. Aucun plan complet
de fichiers n'est televerse comme artefact par l'action.

## Validation

```bash
python3 -m pip install -r tests/ghas/requirements.txt
python3 -m unittest discover -s tests/ghas -v
```

Les tests verifient inventaire, SHA, garde de cible, mode lecture seule,
variables, erreurs d'activation, idempotence et contrats des actions.
Le [plan de migration](./migration-actions.md) couvre les essais GitHub restants.

Les [preuves du deuxieme fork](./preuves/preparation-projects.md) restent
historiques : elles portent sur l'ancien generateur et conservent leur prefixe
`ghas/setup-`. Elles ne prouvent pas l'installation des actions composites.
