# Validation de la preparation sur un deuxieme fork

Date : 2026-10-29 (America/Toronto).

- Cible : `MCN-CQEN/ceai-cqen-labinfra-projects-ghas`.
- Branche par defaut : `main`.
- Bibliotheque : `16443af5ee94789bcfe429f21dc9ba668841d1bc`.
- [Execution centrale](https://github.com/MCN-CQEN/ceai-cqen-scripts-lib/actions/runs/40929433172).
- [Comparaison de la proposition](https://github.com/MCN-CQEN/ceai-cqen-labinfra-projects-ghas/compare/main...ghas/setup-8ab7398fa47d-16443af5ee94).
- Commit propose : `e9023260c3e1bb0628e2c0ffaae752f67c4bc095`.

## Resultats verifies par API

| Controle | Resultat |
| --- | --- |
| Inspection et acces au fork | Reussis |
| Preparation des fichiers | Reussie |
| Branche de proposition | `ghas/setup-8ab7398fa47d-16443af5ee94` |
| Ecart avec main | Un commit, deux fichiers ajoutes |
| Fichiers | `.github/workflows/ghas-security.yml`, `.github/dependabot.yml` |
| Langages CodeQL proposes | `actions` |
| Dependabot propose | Une entree `github-actions` a la racine |
| Branche cible des pushes analyses | `main`, detectee dans ce fork |
| Appels a la bibliotheque | SHA complet, aucun chemin Terraform du cluster |
| Activation Code Security | Echec HTTP 422, verrou sur l'usage facture |
| Activation Secret scanning | Echec HTTP 422, verrou sur l'usage facture |
| Etat Push protection observe | Desactive |
| Configuration automatique des variables | Job ignore suite a l'echec de l'activation |

Le message exact retourne pour Code Security est :
`Code Security cannot be enabled due to a lock on metered usage.`
Le meme verrou est retourne pour Secret scanning.

Lors de la verification, les deux variables de controle sont absentes et le
workflow GHAS n'est pas present sur `main` : les fichiers restent dans la branche
de proposition. Aucune fusion ou execution d'analyse n'a ete demandee pendant
cette verification.

## Conclusion et suite

La generation et l'installation sur une branche fonctionnent sur un autre depot
que le cluster. Ce test ne valide pas toutes les technologies de l'organisation.
Il montre que la selection de la branche et de la configuration n'est plus fixe
au projet cluster.

La validation des analyses sur ce fork reste bloquee par la facturation.
Faire lever le verrou par le responsable autorise, puis relancer la preparation
pour verifier l'activation et les variables. Examiner les workflows de deploiement
herites avant toute fusion de la proposition dans le fork. Ne pas presenter
cette execution globale en echec comme une installation GHAS entierement validee.
