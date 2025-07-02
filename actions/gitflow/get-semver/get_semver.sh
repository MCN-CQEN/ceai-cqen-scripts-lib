# Extraire le nom de la branche de $GITHUB_REF, soit la partie après 'refs/heads/'
branch_name=${GITHUB_REF#refs/heads/}
echo "Branch name : $branch_name"

if [[ $branch_name =~ $MAIN_BRANCH_NAME_REGEX ]]; then
    # Nous créons un tag pour la branche principale (prod, main, master)
    semVer=$MAJOR_MINOR_PATCH

elif [[ $branch_name =~ $RELEASE_BRANCH_NAME_REGEX ]]; then
    # Nous créons une étiquette de version pour une branche de release
    preReleaseNumber=$PRE_RELEASE_NUMBER

    # Si preReleaseNumber est vide, on le rem
    if [[ -z "$preReleaseNumber" ]]; then
        preReleaseNumber=0
    fi

    semVer=${VERSION_PREFIX}${MAJOR_MINOR_PATCH}-${PRE_RELEASE_LABEL}.${preReleaseNumber}

else 
    buildNumber=$BUILD_NUMBER

    # Si buildNumber est vide, on le remplace par 0
    if [[ -z "$buildNumber" ]]; then
        buildNumber=0
    fi

    semVer=${VERSION_PREFIX}${MAJOR_MINOR_PATCH}-${PRE_RELEASE_LABEL}.${buildNumber}
fi  

echo "::debug::semVer=${semVer}"

if [[ -n "$semVer" ]]; then
    echo "semVer=${semVer}" >> $GITHUB_OUTPUT
else
    echo "::error::❌ semVer n'a pas pu être défini."
fi