# Installer BATS pour tester :
# https://bats-core.readthedocs.io/en/stable/tutorial.html#quick-installation
# 
# Pour exécuter : 
# ./test/bats/bin/bats test/test.bats

setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'
    DIR="$( cd "$( dirname "$BATS_TEST_FILENAME" )" >/dev/null 2>&1 && pwd )"
    PATH="$DIR/..:$PATH"
}

__before() {
  # La variable GITHUB_OUTPUT est fournie par Github dans le contexte d'un runner.
  # Elle pointe sur un fichier dans lequel les variables de sortie doivent être écrites.
  # Pour les tests en local, on utilise un fichier temporaire.
  export GITHUB_OUTPUT=$(mktemp)
}

__after() {
  rm -f "$GITHUB_OUTPUT"
}

@test "Le script roule" {
  __before
  run ./get_semver.sh
  __after
}

@test "Tester branch main" {
  # Arrange
  __before
  export GITHUB_REF="refs/heads/main"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export VERSION_PREFIX=""
  export MAJOR_MINOR_PATCH="1.0.0"

  # Act
  run get_semver.sh
  
  # Prepare for assert
  gh_output=($(echo "$(cat $GITHUB_OUTPUT)"))
  
  # Assert
  [ "${gh_output[0]}" = "semVer=1.0.0" ]
  assert_output --partial "semVer=1.0.0"
  assert_output --partial "Branch name : main"

  # Cleanup
  __after
}

@test "Tester branche de release" {
  # Arrange
  __before
  export GITHUB_REF="refs/heads/release/1.0.0"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX=""
  export MAJOR_MINOR_PATCH="1.0.0"
  export PRE_RELEASE_LABEL="rc"
  export PRE_RELEASE_NUMBER="2"

  # Act
  run get_semver.sh

  # Assert
  assert_output --partial "Branch name : release/1.0.0"
  assert_output --partial "semVer=1.0.0-rc.2"
  __after
}

@test "Tester branche de release avec pre_release_number number null" {
  # Arrange
  __before
  export GITHUB_REF="refs/heads/release/1.0.0"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX=""
  export MAJOR_MINOR_PATCH="1.0.0"
  export PRE_RELEASE_LABEL="rc"
  export PRE_RELEASE_NUMBER=""

  # Act
  run get_semver.sh

  # Assert
  assert_output --partial "Branch name : release/1.0.0"
  assert_output --partial "semVer=1.0.0-rc.0"
  __after
}

@test "Tester branche de feature avec build_number null et préfix 'v'" {
  # Arrange
  __before
  export GITHUB_REF="refs/heads/feature/test"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX="v"
  export MAJOR_MINOR_PATCH="1.1.0"
  export PRE_RELEASE_LABEL="feature-test"
  export BUILD_NUMBER=""

  # Act
  run get_semver.sh

  # Prepare for assert
  gh_output=($(echo "$(cat $GITHUB_OUTPUT)"))
  
  # Assert
  [ "${gh_output[0]}" = "semVer=v1.1.0-feature-test.0" ]
  assert_output --partial "Branch name : feature/test"
  assert_output --partial "semVer=v1.1.0-feature-test.0"
  __after
}