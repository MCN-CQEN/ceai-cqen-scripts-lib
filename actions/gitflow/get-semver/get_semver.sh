# Extraire le nom de la branche de $GITHUB_REF, soit la partie après 'refs/heads/'
branch_name=${GITHUB_REF#refs/heads/}
echo "Branch name : $branch_name"

# Retourne le hash court du commit qui servira à tracer précisément la source
# de la préversion. GitVersion fournit normalement ShortSha; github.sha sert
# de repli si cette valeur n'est pas disponible dans le contexte d'exécution.
get_short_hash() {
    if [[ -n "$COMMIT_HASH" ]]; then
        echo "${COMMIT_HASH:0:7}"
    elif [[ -n "$GITHUB_SHA" ]]; then
        echo "${GITHUB_SHA:0:7}"
    else
        echo "unknown"
    fi
}

# Détermine la portion "prebuild" du suffixe à partir du contexte GitFlow.
# On privilégie PRE_RELEASE_LABEL, car il provient de GitVersion et respecte
# la configuration GitVersion.yml; les règles suivantes servent de repli pour
# conserver un comportement prévisible si le label GitVersion est vide.
get_prebuild_label() {
    if [[ -n "$PRE_RELEASE_LABEL" ]]; then
        echo "$PRE_RELEASE_LABEL"
    elif [[ $branch_name =~ ^feature[\/-](.+)$ ]]; then
        echo "feature-${BASH_REMATCH[1]}"
    elif [[ $branch_name =~ ^hotfix[\/-](.+)$ ]]; then
        echo "hotfix-${BASH_REMATCH[1]}"
    elif [[ $branch_name =~ ^dev$ ]]; then
        echo "dev"
    elif [[ $branch_name =~ $RELEASE_BRANCH_NAME_REGEX ]]; then
        echo "rc"
    else
        echo "prebuild"
    fi
}

# Génère la date de préversion en UTC au format YYYYMMDD pour rendre les
# versions ordonnables et comparables d'un environnement à l'autre. VERSION_DATE
# permet aux tests automatisés de figer la valeur sans dépendre de l'horloge.
get_version_date() {
    if [[ -n "$VERSION_DATE" ]]; then
        echo "$VERSION_DATE"
    else
        date -u +%Y%m%d
    fi
}

# Calcule le nombre de secondes écoulées depuis minuit UTC. Ce segment ajoute
# un séquentiel temporel standardisé dans la journée; le format sur 5 chiffres
# facilite le tri lexical des versions générées le même jour.
get_version_seconds() {
    if [[ -n "$VERSION_SECONDS" ]]; then
        printf "%05d" "$VERSION_SECONDS"
    else
        current_hour=$(date -u +%H)
        current_minute=$(date -u +%M)
        current_second=$(date -u +%S)
        printf "%05d" $((10#$current_hour * 3600 + 10#$current_minute * 60 + 10#$current_second))
    fi
}

if [[ $branch_name =~ $MAIN_BRANCH_NAME_REGEX ]]; then
    # La branche principale publie la version stable calculée par GitVersion,
    # sans suffixe de préversion, afin de produire un tag final comme 1.5.0.
    semVer=$MAJOR_MINOR_PATCH

else 
    # Toutes les branches non principales produisent une préversion unique et
    # traçable au format Major.Minor.Patch-prebuild.YYYYMMDD.SSSSS.hashcommit.
    prebuildLabel=$(get_prebuild_label)
    versionDate=$(get_version_date)
    versionSeconds=$(get_version_seconds)
    shortHash=$(get_short_hash)

    semVer=${VERSION_PREFIX}${MAJOR_MINOR_PATCH}-${prebuildLabel}.${versionDate}.${versionSeconds}.${shortHash}
fi  

echo "::debug::semVer=${semVer}"

if [[ -n "$semVer" ]]; then
    echo "semVer=${semVer}" >> $GITHUB_OUTPUT
else
    echo "::error::❌ semVer n'a pas pu être défini."
fi
