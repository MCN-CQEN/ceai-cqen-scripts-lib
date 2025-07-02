const core = require('@actions/core');
const defaults = require('./defaults.js');

const ajv = require('ajv');

const schemaRestrictionsBranches = {
    type: "array",
    items: {
        type: "object",
        properties: {
            dest: { type: "string" },
            restriction_branche: { type: "string" }
        },
        required: ["dest", "restriction_branche"], 
        additionalProperties: false
    }
};


const parseRestrictionBranches = (restrictionsBranches) => {
    if (!restrictionsBranches) {
        return [];
    }
    try {
        const parsedRestrictions = JSON.parse(restrictionsBranches);
        const validator = new ajv();
        const isValid = validator.validate(schemaRestrictionsBranches, parsedRestrictions);
        
        if (!isValid) {
            throw new Error(`Format des restrictions de branches invalide: ${validator.errors.map(err => err.message).join(', ')}`);
        }
        
        return parsedRestrictions;
    } catch (error) {
        throw new Error(`Erreur lors de l'analyse des restrictions de branches: ${error.message}`);
    }
}

const run = () => {
    try {
        const nomBrancheDest = core.getInput('nom_branche_dest');
        const nomBrancheSource = core.getInput('nom_branche_source');
        let restrictionsBranches = core.getInput('restrictions_branches');

        restrictionsBranches = !restrictionsBranches ? defaults.DEFAULT_RESTRICTIONS : parseRestrictionBranches(restrictionsBranches);
        
        const restrictionBranche = restrictionsBranches
            .find(r => new RegExp(r.dest).test(nomBrancheDest))
            ?.restriction_branche;

        core.info(`Branche de destination: ${nomBrancheDest}`);
        core.info(`Branche source: ${nomBrancheSource}`);
        core.info(`Restriction de branche: ${restrictionBranche}`);

        if (!restrictionBranche) {
            core.setOutput("accepted", true);
            core.info(`Aucune restriction trouvée pour la branche de destination: ${nomBrancheDest}`);
            return
        }
        
        const regex = new RegExp(restrictionBranche, 'i');
        const accepted = regex.test(nomBrancheSource);
        
        if (!accepted) {
            core.setFailed(`Vous ne pouvez pas fusionner la branche ${nomBrancheSource} vers ${nomBrancheDest}, car elle ne respecte pas la rêgle ${restrictionBranche}`);
            return
        }
        
        const time = (new Date()).toTimeString();
        core.setOutput("accepted", accepted);
        core.setOutput("time", time);

    
    } catch (error) {
        core.setFailed(`Erreur inattendue : ${error.message}`);
    }
}

exports.run = run
exports.parseRestrictionBranches = parseRestrictionBranches

run()
