const core = require('@actions/core');
const {run, parseRestrictionBranches } = require('../src/index');
const defaults = require('../src/defaults');

jest.mock('@actions/core');

describe('Main action function', () => {
    afterEach(() => {
        jest.resetAllMocks()
    })

    it("Rouler l'action sans paramètres", async () => {
        // Act
        await run()

        // Assert
        expect(core.setOutput).toHaveBeenCalledWith('accepted', true);
    })

    it("Rouler l'action avec des paramètres valides", async () => {
        // Arrange
        core.getInput.mockImplementation((name) => {
            switch (name) {
                case 'nom_branche_dest':
                    return 'main';
                case 'nom_branche_source':
                    return 'release/test';
                case 'restrictions_branches':
                    return '[{"dest": "main", "restriction_branche": "^release\/.*$"}]';
                default:
                    return '';
            } 
        });
        
        // Act
        await run();

        // Assert
        expect(core.setOutput).toHaveBeenCalledWith('accepted', true);
    })
    
    it("Rouler l'action avec des paramètres valides, sans fournir la restriction de branche (devrait utiliser les valeurs par défaut)", async () => {
        // Arrange
        core. getInput.mockImplementation((name) => {
            switch (name) {
                case 'nom_branche_dest':
                    return 'main';
                case 'nom_branche_source':
                    return 'release/test';
                default:
                    return null;
            } 
        });
        
        // Act
        await run();

        // Assert
        expect(core.setOutput).toHaveBeenCalledWith('accepted', true);
    })

    it("Casse si la branche à fusionner n'est pas permise", async () => {
        // Arrange
        core. getInput.mockImplementation((name) => {
            switch (name) {
                    case 'nom_branche_dest':
                        return 'main';
                    case 'nom_branche_source':
                        return 'feature/test';
                    case 'restrictions_branches':
                        return '[{"dest": "main", "restriction_branche": "^release\/.*$"}]';
                    default:
                        return '';
                } 
            });

        // Act
        await run();

        // Assert
        expect(core.setFailed).toHaveBeenCalled();
    })


    it("Casse si la branche à fusionner n'est pas permise, sans fournir la restriction de branche (devrait utiliser les valeurs par défaut)", async () => {

        // Arrange
        core. getInput.mockImplementation((name) => {
            switch (name) {
                case 'nom_branche_dest':
                    return 'main';
                case 'nom_branche_source':
                    return 'feature/test';
                case 'restrictions_branches':
                    return '';
                default:
                    return '';
            } 
        });
        
        // Act
        await run();

        // Assert
        expect(core.setFailed).toHaveBeenCalled();
    })

    it("Accepte plus d'une configuration de restriction de branche", async () => {
    	// Arrange
        core.getInput.mockImplementation((name) => {
            switch (name) {
                case 'nom_branche_dest':
                    return 'main';
                case 'nom_branche_source':
                    return 'release/test';
                case 'restrictions_branches':
                    return '[{"dest": "main", "restriction_branche": "^release\/.*$"}, {"dest": "main", "restriction_branche": "^feature\/.*$"}]';
                default:
                    return '';
            } 
        });

        // Act
        await run();

        // Assert
        expect(core.setOutput).toHaveBeenCalledWith('accepted', true);
    })

    it("Tombe dans le carch (du try) en cas d'erreur innattendue", async () => {
    	// Arrange
        core.getInput.mockImplementation((name) => {
            switch (name) {
                case 'nom_branche_dest':
                    return 'main';
                case 'nom_branche_source':
                    return 'release/test';
                case 'restrictions_branches':
                    return '[{"dest": "main", "restriction_branche": "^release\/.*$"}, {"dest": "main"}]';
                default:
                    return '';
            } 
        });

        // Act
        await run();

        // Assert
        expect(core.setFailed).toHaveBeenCalledWith(expect.stringContaining("Erreur inattendue"));
    })
});

describe("parseRestrictionBranches", () => {
    afterEach(() => {
        jest.resetAllMocks()
    })
    
    it("La fonction parseRestrictionBranches() retourne un objet conforme", async () => {
        // Arrange
        const input = '[{"dest": "main", "restriction_branche": "^release\/.*$"}, {"dest": "main", "restriction_branche": "^feature\/.*$"}]';
        const expectedOutput = [
            { dest: 'main', restriction_branche: '^release\/.*$' },
            { dest: 'main', restriction_branche: '^feature\/.*$' }
        ];
        
        // Act
        const ret = parseRestrictionBranches(input)

        // Assert
        expect(ret).toEqual(expectedOutput);
    })

    it("La fonction parseRestrictionBranches() retourne une erreur si l'input est invalide", async () => {
        // Arrange
        const input = '[{"dest": "main", "restriction_branche": "^release\/.*$"}, {"dest": "main"}]';
        
        // Act & Assert
        expect(() => parseRestrictionBranches(input)).toThrow();
    })

    it("should return empty array if restrictionsBranches is falsy", () => {
        // Act & Assert
        expect(parseRestrictionBranches()).toEqual([]);
        expect(parseRestrictionBranches(null)).toEqual([]);
        expect(parseRestrictionBranches('')).toEqual([]);
    });

    it("devrait lever une erreur si une propriété inconnue est présente dans la restriction", () => {
        // Arrange
        const invalidRestrictions = '[{"branch":"master","type":"invalidType","value":"release-\\d+\\.\\d+"}]';

        // Act & Assert
        expect(() => parseRestrictionBranches(invalidRestrictions)).toThrow();
    });

    it("devrait lever une erreur si le JSON est mal formé", () => {
        // Arrange
        const malformedJson = '[Invalid JSON]';

        // Act & Assert
        expect(() => parseRestrictionBranches(malformedJson)).toThrow(/Erreur lors de l'analyse des restrictions de branches/);
    });
})