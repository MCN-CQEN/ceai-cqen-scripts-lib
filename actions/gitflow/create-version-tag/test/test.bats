# Installer BATS pour tester :
# https://bats-core.readthedocs.io/en/stable/tutorial.html#quick-installation
# 
# Pour exécuter : 
# ./test/bats/bin/bats test/test.bats


setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'
    load 'test_helper/bats-mock/stub'

    _GIT_ARGS_COMMIT_AVEC_TAG='tag --points-at sha-commit-avec-tag'
    _GIT_ARGS_COMMIT_SANS_TAG='tag --points-at sha-commit-sans-tag'

    stub git \
        "${_GIT_ARGS_COMMIT_AVEC_TAG} : echo '1.0.0'" \
        "${_GIT_ARGS_COMMIT_SANS_TAG} : echo ''"
}

cleanup_stubs() {
    # Issue : https://github.com/jasonkarns/bats-mock/issues/3
    if stat ${BATS_TMPDIR}/*-stub-plan >/dev/null 2>&1; then
        for file in ${BATS_TMPDIR}/*-stub-plan; do
            program=$(basename $(echo "$file" | rev | cut -c 11- | rev))
            unstub $program || true
        done
    fi
}

teardown() {
    cleanup_stubs
}

__before() {
    # La variable GITHUB_OUTPUT est fournie par Github dans le contexte d'un runner.
    # Elle pointe sur un fichier dans lequel les variables de sortie doivent être écrites.
    # Pour les tests en local, on utilise un fichier temporaire.
    export GITHUB_ENV=$(mktemp)
}

__after() {
    rm -f "$GITHUB_ENV"
}


@test "Tester sur commit avec tag de version" {
    # Arrange
    __before
    export COMMIT_SHA="sha-commit-avec-tag"

    # Act
    run ./check_version_tag.sh
    echo "$output"

    # Prepare for assert
    gh_env=($(echo "$(cat $GITHUB_ENV)"))
    
    # Assert
    [ "${gh_env[0]}" == 'COMMIT_HAS_TAG=true' ]

    __after
}

@test "Tester sur commit sans tag de version" {
    # Arrange
    __before
    export COMMIT_SHA="sha-commit-sans-tag"

    # Act
    run ./check_version_tag.sh
    echo "$output"

    # Prepare for assert
    gh_env=($(echo "$(cat $GITHUB_ENV)"))

    # Assert
    [ "${gh_env[0]}" == 'COMMIT_HAS_TAG=false' ]

    __after
}


