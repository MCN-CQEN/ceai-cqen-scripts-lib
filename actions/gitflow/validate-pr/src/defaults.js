/**
 * Restriction de branche par défaut pour les branches principales et développement. 
 * Les expressions régulières sont utilisées pour vérifier si la branche est une version 
 * de développement ou une version de production. Par exemple, "^(release)|(hotfix)\/.*$" 
 * correspond à toutes les branches qui commencent par "release" ou "hotfix"."
 *
 */
const defaultRestrictions = [
    {
        "dest": "^master$|^main$|^prod$",
        "restriction_branche": "^(release)|(hotfix)\/.*$"
    },
    {
        "dest": "^dev(elop)?(ment)?$",
        "restriction_branche": "^(release)|(feature)|(hotfix)\/.*$"
    }
];

exports.DEFAULT_RESTRICTIONS = defaultRestrictions; 


