# Preparation de plusieurs forks

Le workflow central recoit toujours un `target_repository` explicite au format
`ORG/fork`. La cible doit etre un fork GitHub actif de la meme organisation que
la bibliotheque. L'application doit etre installee sur cette cible. Aucun acces
aux secrets AWS du projet, aucun checkout du fork et aucune execution de son
code ne sont necessaires pour l'inventaire.

## Options independantes

| Option | Defaut | Effet |
| --- | --- | --- |
| `target_repository` | Aucun | Fork a preparer |
| `enable_security` | `false` | Demande d'activation des produits, potentiellement facturable |
| `configure_variables` | `false` | Verification des prerequis et configuration des deux variables |
| `files_mode` | `none` | `none`, `preview` ou `install` |

Les options d'activation, de variables et de fichiers sont independantes.
L'installation des fichiers ne vaut pas activation des produits et ne prouve
pas la reussite des analyses. Un fichier appele peut exister avec une variable
`false`, auquel cas le controle est ignore.

## Inventaire et proposition

`preview` lit l'arbre Git de la branche par defaut du fork sans le modifier.
Il detecte les fichiers Python, Ruby et JavaScript/TypeScript, et ajoute Actions
car le kit installe lui-meme un workflow. Les langages compilables sont signales
comme necessitant un profil non encore automatise par ce kit ; cela ne signifie
pas qu'ils ne sont pas pris en charge par CodeQL.

Dependabot est propose pour les manifestes npm, pip, Bundler, Go modules, Maven,
Gradle, Cargo, Composer et NuGet reconnus par nom ou extension, ainsi que les
repertoires Terraform contenant des `.tf`. Les repertoires sont propres au fork,
sans chemins cluster predefinis. Les entrees sont dedupliquees et hebdomadaires.

Les repertoires `vendor`, `node_modules`, `.venv`, `venv`, `dist` et `build` sont
ignores pour l'inventaire. Cet inventaire est une heuristique, pas une analyse
du contenu des manifestes. Les variantes de gestionnaires (par exemple uv), les
registres prives, les sous-modules et les ecosystemes non listes necessitent
une revue. La presence d'un manifeste ne garantit pas des alertes de vulnerabilite.
Un arbre Git tronque ou plus de 100 couples ecosysteme/repertoire bloque la
generation plutot que d'omettre silencieusement une partie du projet.

## Installation dans une branche de proposition

`install` genere :

- `.github/workflows/ghas-security.yml`, avec les langages detectes, la vraie
  branche par defaut du fork et les appels de bibliotheque figes au SHA utilise ;
- `.github/dependabot.yml`, uniquement si aucun fichier `dependabot.yml` ou
  `dependabot.yaml` n'existe deja dans `.github`. Une configuration existante
  est preservee et sa couverture doit etre revue.

Les documents generes utilisent JSON, un sous-ensemble valide de YAML, pour
serialiser les donnees avec la bibliotheque standard et conserver les expressions
GitHub Actions telles quelles. Leurs extensions restent `.yml`.

Les modifications sont proposees dans une branche
`ghas/setup-<SHA-base-court>-<SHA-bibliotheque-court>`. Le workflow ne modifie pas
la branche par defaut, n'ouvre aucune PR, ne fusionne pas et ne lance pas les
analyses. Un seul commit contient les fichiers proposes. Il peut remplacer le
fichier appelant GHAS dans la proposition ; la version de la branche par defaut
reste intacte tant que la proposition n'est pas fusionnee.

Le resume fournit un lien de comparaison. Une proposition identique est reusee.
Une proposition existante avec des modifications differentes est refusee,
sans force-push. Aucune modification n'est necessaire si la branche par defaut
contient deja le workflow attendu ; Dependabot existant reste preserve.

Avant de fusionner dans le fork, verifier les doublons avec les anciens workflows
de securite et desactiver les workflows de deploiement herites. Un push vers la
branche par defaut peut sinon lancer des workflows d'infrastructure. Cette
version ne les desactive pas automatiquement et ne demande jamais leur execution.

Pour installer, l'application doit avoir `Contents: Read and write` et
`Workflows: Read and write`, approuves sur l'installation. Le jeton de preparation
est limite au fork et a ces permissions. Le mode preview ne demande que Contents
en lecture. Chaque jeton est revoque a la fin du job.

## Premiere verification sur branche

Dans `.github/workflows/ghas-pilot.yml`, choisir un fork autorise et conserver :

```yaml
enable_security: false
configure_variables: false
files_mode: preview
```

Publier la modification sur `feature/ghas-toolkit`, puis consulter `GHAS - Branch
pilot` dans la bibliotheque, resume `GHAS file preparation`. Apres revue,
passer `files_mode` a `install` et publier ce changement pour creer la proposition
dans le fork. Les essais sur d'autres forks changent uniquement `target_repository`.
Apres integration du workflow central sur la branche par defaut, ces options
seront accessibles via `Run workflow` sans modifier le pilote.

Le plan complet est conserve uniquement dans un fichier temporaire du runner,
sans publication automatique d'un artefact. Le resume publie les langages,
les nombres de repertoires par ecosysteme et le lien de proposition, sans contenu
source ni liste complete des chemins. La bibliotheque etant publique, ses resumes
et journaux le sont aussi : utiliser un orchestrateur prive si ces metadonnees
doivent rester confidentielles.

## Verification locale

```bash
python3 -m unittest discover -s tests/ghas -v
```

Les tests couvrent les projets differents du cluster, la generation des references
immuables, les restrictions de cible, la preservation de Dependabot, l'absence
d'ecriture en preview et la creation/reutilisation d'une proposition sans mise
a jour de la branche par defaut.

Validation du 2026-10-29 : 14 tests locaux reussis. Un preview reel sur le fork
pilote a confirme `actions` et `python`, une entree GitHub Actions et cinq
repertoires Terraform, avec toutes les mutations bloquees par le client de test.
L'installation distante par le nouveau job doit encore etre verifiee apres
publication de cette version. Aucun autre fork reel n'a encore servi a valider
la detection ; les projets alternatifs sont couverts par les tests locaux.

## References

- [Options Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
- [Modes CodeQL pour les langages compiles](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-for-compiled-languages)
