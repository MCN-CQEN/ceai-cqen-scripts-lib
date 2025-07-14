# Vérifier si le commit actuel a déjà une tag de version.
# Si oui, définir variable d'environnement COMMIT_HAS_TAG
# Un tag de version débute par un série de 3 nombres, séparées par des points : 9.9.9. Aprèes les trois nombre, il peut, ou pas, y avoir des caractères.
echo "Github token : $GH_TOKEN"
echo "Github ref_name: $GH_REF_NAME"
echo "Commit SHA : $COMMIT_SHA"

TAG_INFO=$(git tag --points-at $COMMIT_SHA)

echo "TAG_INFO : $TAG_INFO"

# Vérifier le format du tag
if [[ $TAG_INFO =~ ^[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
    echo "Ce commit a déjà une tag de version : $TAG_INFO"
    echo "COMMIT_HAS_TAG=true" >> $GITHUB_ENV
else
    echo "COMMIT_HAS_TAG=false" >> $GITHUB_ENV
fi
