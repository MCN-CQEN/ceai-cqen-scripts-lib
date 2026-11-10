# Bilan de validation GHAS

Etat au 2026-11-10. Cible pilote :
`MCN-CQEN/ceai-cqen-labinfra-cluster-ghas`, ID `1435756700`, branche par defaut
`dev`. Bibliotheque : PR 38, integration finale soumise a revue et approbation.

La solution utilise des actions composites sous `actions/`, conformement a
la structure de la bibliotheque. Les anciens workflows restent des adaptateurs
temporaires pour les consumers existants, pas l'interface conseillee.
Voir les [preuves de migration](./preuves/composite-actions-validation.md).

## Criteres d'acceptation

| Critere | Resultat sur le fork pilote | Preuve ou reserve |
| --- | --- | --- |
| GHAS active et configure | Valide pour le service sur ce fork | Produits constates actifs ; activation composite sur un depot desactive non rejouee |
| Analyse CodeQL reussie | Valide via composite : Actions et Python | [PR 12 et runs](./preuves/composite-actions-validation.md) |
| Secret scanning fonctionnel | Valide avec motif fictif | [Alerte 1 et refus GH013](./preuves/secret-scanning-controlled-test.md) ; test historique, independant de la migration des scans |
| Controles de dependances | Valides sur PR et propositions de versions | Composite : rejet de requests 2.19.1 puis retour au vert ; [Dependabot](./preuves/dependabot-validation.md) |
| Execution automatique | Validee sur PR | Jobs du fork appelant les actions ; calendrier configure mais sans preuve de run planifie |
| Problemes accessibles | CodeQL et Secret scanning valides ; dependances visibles dans les Checks | [CodeQL controle](./preuves/codeql-controlled-test.md), alertes historiques ; pas de preuve controlee d'alerte Dependabot |
| Probleme controle detecte | Valide | Nouvelle action Dependency Review : 5 vulnerabilites detectees ; CodeQL Actions et motif fictif historiquement testes |
| Configuration et traitement documentes | Rediges et references | [README](./README.md), [preparation](./preparation-multidepot.md), [procedure](./traitement-alertes.md) ; nettoyage final a publier |

## Validation de la bibliotheque reutilisable

- `ghas-codeql` : analyse du checkout du caller ; matrice et permissions dans son workflow.
- `ghas-dependency-review` : rejet d'une dependance vulnerable puis retour au vert.
- `ghas-prepare-fork` : preview sans modification, installation d'un seul commit
  sur une branche de proposition, configuration et relecture des deux variables.
- Dev restee intacte pendant le test d'installation ; le manifeste vulnerable
  present sur dev a ete retire par une PR de nettoyage distincte (13).
- Exemples et adaptateurs figes sur `8c108cedf0faa03e3ff6cf153ef1b62484a6d8c7`.
- Workflow temporaire de tests retire dans le nettoyage de livraison ; aucune
  cible de test declenchee automatiquement n'est livree.
- Code du fork jamais execute par la preparation ; la cle App reste dans le
  depot d'administration, pas dans les jobs de scan.

Les PR de configuration historiques Dependabot (2) et GitFlow (11) sont fusionnees
dans le fork. La PR composite 12 reste ouverte et non fusionnee lors de la
verification. La branche d'installation est conservee comme preuve, sans fusion.
La bibliotheque ne fusionne aucune proposition ni ne supprime les forks.

## Restes pour la cloture administrative

1. Publier le nettoyage final, verifier la CI, puis faire approuver la PR 38.
2. Confirmer avec le responsable que le pilote sur fork satisfait le perimetre
   retenu. Il ne constitue pas une activation GHAS sur le depot source.
3. Apres fusion de la bibliotheque, verifier le lancement manuel en lecture seule
   depuis la branche par defaut du depot d'administration.
4. Exporter les preuves selon les regles internes avant suppression des forks ;
   les liens vers leurs alertes/PR/jobs ne sont pas un archivage autonome complet.

## Limites et extensions distinctes

- Les profils compiles, registres prives et manifestes non reconnus exigent des
  adaptations. Le kit n'est pas valide universellement sur tous les projets.
- La preparation sur un [deuxieme fork](./preuves/preparation-projects.md) est
  historique ; son activation et ses analyses restent non validees apres le
  verrou de facturation constate. Faire verifier cet etat par un administrateur.
- Les protections de branche et le blocage obligatoire de fusion ne sont pas
  configures/testes par ce pilote. Un job CodeQL reussi n'implique pas zero alerte.
- Les anciens workflows ignores et les workflows d'infrastructure herites restent
  a revoir par depot. Le kit ne desactive pas ces derniers automatiquement.
- Les alertes preexistantes ne sont pas toutes corrigees. Les actions tierces
  appelees a l'interieur des composites gardent leurs versions a maintenir,
  notamment les avertissements de runtime Node.js.
- Une nouvelle vulnerabilite Python controlee, le cycle d'une alerte Dependabot
  sur la branche par defaut et une nouvelle detection/correction CodeQL via
  composite ne sont pas prouves par les runs de migration seuls.
- Une recreation de fork sous le meme nom doit conserver son ID dans les preuves,
  reverifier l'installation de l'App, les produits et Dependabot version updates.
  Elle ne garantit pas une seule licence et ne contourne pas la facturation.

Conclusion : pilote technique valide dans le perimetre documente ; integration
et acceptation finale en attente de publication/revue, sans deploiement generalise.
