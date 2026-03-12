# GitHub Action – Associer un WAF à tous les ALBs

## Introduction

Cette GitHub Action composite permet d'**associer automatiquement un Web ACL AWS WAF à tous les Application Load Balancers (ALB) d'une région AWS**.

Elle :

* Récupère la liste de tous les ALBs dans la région AWS cible
* Associe le Web ACL WAF à chacun d'eux

Technologies utilisées :

* AWS WAFv2
* AWS Elastic Load Balancing
* GitHub Actions

---

## Table des matières

* [Vue d'ensemble](#vue-densemble)
* [Fonctionnement](#fonctionnement)
* [Inputs](#inputs)
* [Permissions IAM requises](#permissions-iam-requises)
* [Exemple d'utilisation](#exemple-dutilisation)
* [Bonnes pratiques sécurité](#bonnes-pratiques-sécurité)
* [Dépannage](#dépannage)

---

## Vue d'ensemble

Cette action est de type **composite** et exécute une série d'étapes Bash pour automatiser l'association WAF/ALB via l'AWS CLI.

Elle est **idempotente** : si le WAF est déjà associé à un ALB, l'appel AWS CLI le confirmera sans erreur.

---

## Fonctionnement

L'action suit la logique suivante :

1. Lister tous les ALBs disponibles dans la région AWS spécifiée
2. Pour chaque ALB, associer le Web ACL WAF via `aws wafv2 associate-web-acl`

Si aucun ALB n'est trouvé dans la région, l'action se termine sans erreur.

---

## Inputs

| Input         | Requis | Défaut         | Description                              |
| ------------- | ------ | -------------- | ---------------------------------------- |
| `web_acl_arn` | ✅     | —              | ARN du Web ACL WAF à associer aux ALBs  |
| `aws_region`  | ❌     | `ca-central-1` | Région AWS où se trouvent les ressources |

---

## Permissions IAM requises

Le rôle AWS utilisé dans le workflow doit avoir les permissions suivantes :

```json
{
  "Effect": "Allow",
  "Action": [
    "wafv2:AssociateWebACL",
    "elasticloadbalancing:DescribeLoadBalancers"
  ],
  "Resource": "*"
}
```

---

## Exemple d'utilisation

```yaml
jobs:
  associate-waf:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Configurer les credentials AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ca-central-1

      - name: Associer le WAF à tous les ALBs
        uses: MCN-CQEN/ceai-cqen-scripts-lib/actions/associate-waf@main
        with:
          web_acl_arn: ${{ secrets.WAF_ARN }}
          aws_region: "ca-central-1"
```

### Secrets GitHub à configurer

| Nom            | Type   | Description                       |
| -------------- | ------ | --------------------------------- |
| `AWS_ROLE_ARN` | Secret | ARN du rôle IAM à assumer (OIDC) |
| `WAF_ARN`      | Secret | ARN du Web ACL WAF                |

---

## Bonnes pratiques sécurité

* Utiliser **OIDC** (`id-token: write`) pour l'authentification AWS plutôt que des clés d'accès statiques
* Stocker l'ARN du WAF dans les **GitHub Secrets**
* Restreindre le rôle IAM au strict nécessaire (principe du moindre privilège)
* Vérifier que le Web ACL est bien en scope `REGIONAL` (obligatoire pour les ALBs)

---

## Dépannage

### ❌ Aucun ALB trouvé

* Vérifier que la région `aws_region` est correcte
* Vérifier que le rôle IAM a la permission `elasticloadbalancing:DescribeLoadBalancers`

### ❌ Erreur lors de l'association WAF

* Vérifier que le Web ACL est en scope `REGIONAL` (et non `CLOUDFRONT`)
* Vérifier que l'ARN du WAF est correct
* Vérifier les permissions IAM : `wafv2:AssociateWebACL`
