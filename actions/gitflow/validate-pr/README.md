# But

Cette action permet d'accepter ou de refuser un merge vers les branches "main" et "develop".

L'idée est de pouvoir renforcer, dans le contexte du GitFlow, quels branches peuvent être fusionnées vers les branches permanentes.

# Paramètres en entrée

### nom_branche_dest
Nom de la branche de destination.

**Exemples** : 
- `"main"` : Valeur explicite. Cet usage n'est pas recommandé, puisque le nom de la branche peut être variable selon les condition de déclenchement de l'action.
- `"{{ github.base_ref }}"` : Valeur dynamique. Cet usage est recommandé, puisque il s'adapte à la situation.


### nom_branche_source
Nom de la branche source. 

**Exemple** : 
- `"{{ github.head_ref }}"` : Cette variable **github** est la branche source de la pull request.

### restrictions_branches **(optionnel)**

> Cette valeur est optionnelle. Si omise, les valeurs sous `./src/defaults.js` seront automatiquement appliquées.

Objet définissant les contraintes de fusion de branche par branche de destination.

**Format** : 
```json
[
  {
    "dest": String (regex), 
    "restriction_branche": String (regex)
  }
]
```

**Exemple** : 
```json
[
  {
    "dest": "^master$|^main$", 
    "restriction_branche": "^feature/"
  }, 
  {
    "dest": "develop", v
    "restriction_branche": "^hotfix/"
  }
]
```

> À noter que cette valeur devra être sérialisée sous forme de chaîne de caractères, comme présentée dans l'exemple d'utilisation de la section suivante.

# Exemple d'utilisation

```yaml
name: Validation du PR sur main ou develop
on:
  pull_request:
    types: [opened, synchronize, reopened, edited]
jobs:
  gitflow_on_pr_main_or_develop:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        id: checkout
        uses: actions/checkout@v4
        
      - name: Validation du PR sur main ou develop
        id: gitflow_on_pr
        uses: ./actions/validate-pr
        with:
          nom_branche_dest: ${{ github.base_ref }}
          nom_branche_source: ${{ github.head_ref }}  
```

       
 

