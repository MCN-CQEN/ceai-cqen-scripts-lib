# Usage Examples

## Example 1: Using in GitHub Actions Workflow

Your workflow now installs and uses the Collection:

```yaml
- name: Install Ansible and collection
  shell: bash
  run: |
    pip install ansible boto3 botocore psycopg2-binary
    ansible-galaxy collection install git+https://github.com/MCN-CQEN/ceai-cqen-scripts-lib@main
```

## Example 2: Using in Another Project

1. Add to your requirements.yml:

```yaml
collections:
  - name: mcn_cqen.infrastructure
    version: ">=1.0.0"
    source: https://github.com/MCN-CQEN/ceai-cqen-scripts-lib.git
```

2. Install with: ansible-galaxy collection install -r requirements.yml

3. Use in your playbook with the role aurora_users

## Example 3: Local Development

Create group_vars/all.yml, group_vars/apps.yml, group_vars/roles.yml
Then run the playbook from playbooks/provision_aurora_users.yml

## Secrets Created

Pattern: {identifier}-{engine}-{app_name}_{env_suffix}-rds-users-secret

Example: cqen-aurora-postgresql-keycloak_dev-rds-users-secret

Contains: DB_NAME, DB_HOST, DB_ADMIN, DB_ADMIN_PASS, DB_USER, DB_PASS
