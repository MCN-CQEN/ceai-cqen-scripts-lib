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
  # La branche principale doit rester une version stable pure: aucun suffixe
  # prebuild/date/secondes/hash ne doit être ajouté sur main.
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
  # Les variables temporelles et le hash sont figés pour rendre le test
  # déterministe tout en validant le format réel produit par le workflow.
  export GITHUB_REF="refs/heads/release/1.0.0"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX=""
  export MAJOR_MINOR_PATCH="1.0.0"
  export PRE_RELEASE_LABEL="rc"
  export VERSION_DATE="20260707"
  export VERSION_SECONDS="45296"
  export COMMIT_HASH="a1b2c3d"

  # Act
  run get_semver.sh

  # Assert
  assert_output --partial "Branch name : release/1.0.0"
  assert_output --partial "semVer=1.0.0-rc.20260707.45296.a1b2c3d"
  __after
}

@test "Tester branche develop" {
  # Arrange
  __before
  # develop doit produire une préversion "dev" ordonnable et traçable, car
  # elle représente l'environnement d'intégration continue du GitFlow.
  export GITHUB_REF="refs/heads/develop"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX=""
  export MAJOR_MINOR_PATCH="1.4.2"
  export PRE_RELEASE_LABEL="dev"
  export VERSION_DATE="20260707"
  export VERSION_SECONDS="45296"
  export COMMIT_HASH="a1b2c3d"

  # Act
  run get_semver.sh

  # Assert
  assert_output --partial "Branch name : develop"
  assert_output --partial "semVer=1.4.2-dev.20260707.45296.a1b2c3d"
  __after
}

@test "Tester branche de feature avec préfix 'v'" {
  # Arrange
  __before
  # Le préfixe optionnel "v" doit s'appliquer au début de la version sans
  # modifier la structure du suffixe de préversion standardisé.
  export GITHUB_REF="refs/heads/feature/auth"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX="v"
  export MAJOR_MINOR_PATCH="1.4.2"
  export PRE_RELEASE_LABEL="feature-auth"
  export VERSION_DATE="20260707"
  export VERSION_SECONDS="45296"
  export COMMIT_HASH="a1b2c3d"

  # Act
  run get_semver.sh

  # Prepare for assert
  gh_output=($(echo "$(cat $GITHUB_OUTPUT)"))
  
  # Assert
  [ "${gh_output[0]}" = "semVer=v1.4.2-feature-auth.20260707.45296.a1b2c3d" ]
  assert_output --partial "Branch name : feature/auth"
  assert_output --partial "semVer=v1.4.2-feature-auth.20260707.45296.a1b2c3d"
  __after
}

@test "Tester branche hotfix" {
  # Arrange
  __before
  # Une branche hotfix doit conserver son contexte dans le segment prebuild afin
  # de distinguer un correctif de préproduction d'une release ou d'une feature.
  export GITHUB_REF="refs/heads/hotfix/correction"
  export MAIN_BRANCH_NAME_REGEX="^master$|^main$|^prod$"
  export RELEASE_BRANCH_NAME_REGEX="^release[\/-]"
  export VERSION_PREFIX=""
  export MAJOR_MINOR_PATCH="1.4.3"
  export PRE_RELEASE_LABEL="hotfix-correction"
  export VERSION_DATE="20260707"
  export VERSION_SECONDS="45296"
  export COMMIT_HASH="a1b2c3d"

  # Act
  run get_semver.sh

  # Assert
  assert_output --partial "Branch name : hotfix/correction"
  assert_output --partial "semVer=1.4.3-hotfix-correction.20260707.45296.a1b2c3d"
  __after
}
