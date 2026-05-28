# Collection

Collection Ansible pour le provisionnement et la gestion de l'infrastructure AWS Aurora PostgreSQL, incluant la création de bases de données, la gestion des utilisateurs et le stockage des secrets dans AWS Secrets Manager.

## Fonctionnalités

- Créer des bases de données et utilisateurs Aurora PostgreSQL
- Générer et stocker les identifiants dans AWS Secrets Manager
- Configurer le contrôle d'accès basé sur les rôles (RBAC) pour les utilisateurs de base de données
- Support des conventions de nommage spécifiques à l'environnement
- Opérations idempotentes (gère gracieusement les ressources existantes)
- Opérations de destruction/nettoyage pour les environnements de développement

## Prérequis

- Ansible >= 2.10
- Python >= 3.8
- Identifiants AWS configurés (permissions IAM pour Aurora, Secrets Manager, RDS)
- Bibliothèques cliente PostgreSQL (python-psycopg2)

## Installation

```bash
ansible-galaxy collection install mcn_cqen.infrastructure
```

Ou depuis un fichier requirements.yml :

```yaml
collections:
  - name: mcn_cqen.infrastructure
    version: ">=1.0.0"
```

## Utilisation

### Playbook : Provisionner les utilisateurs Aurora

Créer et configurer les bases de données et utilisateurs Aurora PostgreSQL :

```bash
ansible-playbook ~/.ansible/collections/ansible_collections/mcn_cqen/infrastructure/playbooks/provision_aurora_users.yml \\
  -e identifier=my-app \\
  -e engine=aurora-postgresql \\
  -e aws_region=ca-central-1 \\
  -e env_suffix=dev \\
  -e db_host=my-rds.amazonaws.com \\
  -e db_port=5432 \\
  -e db_master_user=postgres \\
  -e db_master_password=masterpass \\
  -e PYTHON_BIN=/usr/bin/python3
```

### Variables requises

- `identifier`: Identifiant application/infrastructure (utilisé pour le nommage)
- `engine`: Moteur de base de données (ex: aurora-postgresql)
- `aws_region`: Région AWS pour Secrets Manager
- `env_suffix`: Suffixe d'environnement (ex: dev, staging, prod)
- `db_host`: Hôte de la base de données Aurora
- `db_port`: Port de la base de données Aurora
- `db_master_user`: Utilisateur maître de la base de données
- `db_master_password`: Mot de passe maître de la base de données

### Variables optionnelles

- `apps`: Liste des applications à provisionner (défaut: défini dans group_vars/apps.yml)
- `db_roles`: Définitions des rôles de base de données (défaut: défini dans group_vars/roles.yml)

## Structure des variables

### Configuration des applications

```yaml
apps:
  - name: keycloak
  - name: icp
  - name: signserver
```

### Rôles de base de données

```yaml
db_roles:
  admin:
    flags:
      - LOGIN
      - CREATEDB
      - CREATEROLE
    schema_privileges:
      - CREATE
      - USAGE
  app:
    flags:
      - LOGIN
    table_privileges:
      - SELECT
      - INSERT
      - UPDATE
      - DELETE
      - TRUNCATE
      - REFERENCES
      - TRIGGER
```

## Secrets créés

Pour chaque application, un secret est créé dans AWS Secrets Manager selon le modèle de nommage :
`{identifier}-{engine}-{app_name}_{env_suffix}-rds-users-secret`

Exemple : `cqen-aurora-postgresql-keycloak_dev-rds-users-secret`

Le secret contient :

```json
{
  "DB_NAME": "keycloak_dev_db",
  "DB_HOST": "my-rds.amazonaws.com",
  "DB_ADMIN": "keycloak_dev_admin",
  "DB_ADMIN_PASS": "generated_password",
  "DB_USER": "keycloak_dev_user",
  "DB_PASS": "generated_password"
}
```
