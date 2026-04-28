# 📦 Vérifier la santé d'un Load Balancer AWS

## 📖 Introduction

Cette GitHub Action permet de vérifier la santé d'un **Load Balancer (ALB/NLB)** déployé sur AWS.
Elle identifie les **Target Groups** associés et s'assure que toutes les cibles sont en état `healthy`.

L'action peut être utilisée en fournissant :

* soit l'ARN du Load Balancer
* soit son nom DNS

Elle échoue automatiquement si des cibles non saines sont détectées.

---

## 📚 Table des matières

* [Introduction](#-introduction)
* [Fonctionnalités](#-fonctionnalités)
* [Pré-requis](#-pré-requis)
* [Installation](#-installation)
* [Utilisation](#-utilisation)
* [Inputs](#-inputs)
* [Exemple](#-exemple)
* [Fonctionnement](#-fonctionnement)
* [Dépendances](#-dépendances)
* [Dépannage](#-dépannage)
* [Contributeurs](#-contributeurs)

---

## ✨ Fonctionnalités

* 🔍 Récupération automatique du Load Balancer via DNS ou ARN
* 🔗 Identification des Target Groups associés
* ❤️ Vérification de l'état de santé des cibles
* ❌ Échec du workflow si une cible est unhealthy
* 🔐 Support de l'authentification AWS via OIDC

---

## ⚙️ Pré-requis

* Un compte AWS avec permissions :

  * `elasticloadbalancing:DescribeLoadBalancers`
  * `elasticloadbalancing:DescribeTargetGroups`
  * `elasticloadbalancing:DescribeTargetHealth`
* Une relation de confiance configurée pour GitHub OIDC
* GitHub Actions activé dans votre repository

---

## 📥 Installation

Ajoutez cette action dans votre repository ou référencez-la depuis un dépôt distant.

---

## 🚀 Utilisation

```yaml
jobs:
  check-lb-health:
    runs-on: ubuntu-latest
    steps:
      - name: Vérifier la santé du Load Balancer
        uses: votre-repo/check-lb-health-action@v1
        with:
          role_to_assume: arn:aws:iam::123456789012:role/github-actions-role
          aws_region: ca-central-1
          lb-dns: my-load-balancer.amazonaws.com
```

---

## 🔧 Inputs

| Nom              | Description                 | Obligatoire | Défaut         |
| ---------------- | --------------------------- | ----------- | -------------- |
| `lb-dns`         | DNS du Load Balancer        | ❌           | -              |
| `lb-arn`         | ARN du Load Balancer        | ❌           | -              |
| `role_to_assume` | Rôle IAM à assumer via OIDC | ✅           | -              |
| `aws_region`     | Région AWS                  | ✅           | `ca-central-1` |

⚠️ Vous devez fournir **au moins un** des paramètres suivants :

* `lb-dns`
* `lb-arn`

---

## 📌 Exemple complet

```yaml
name: Check Load Balancer Health

on:
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Vérifier la santé via ARN
        uses: votre-repo/check-lb-health-action@v1
        with:
          role_to_assume: arn:aws:iam::123456789012:role/github-actions-role
          aws_region: ca-central-1
          lb-arn: arn:aws:elasticloadbalancing:ca-central-1:123456789012:loadbalancer/app/my-lb/123abc
```

---

## ⚙️ Fonctionnement

1. Validation des paramètres d'entrée
2. Récupération de l'ARN (si DNS fourni)
3. Extraction des Target Groups associés
4. Vérification de l'état de chaque cible
5. Échec si une cible est détectée comme non saine

---

## 📦 Dépendances

* AWS CLI
* GitHub Actions
* Action officielle :

  * `aws-actions/configure-aws-credentials@v4`
  * `actions/checkout@v3`

---

## 🛠️ Dépannage

### ❌ Erreur : Load Balancer not found

* Vérifiez le DNS fourni
* Assurez-vous que la région AWS est correcte

### ❌ Targets unhealthy

* Vérifiez :

  * les health checks configurés
  * l'état des instances EC2 / containers
  * les security groups

### ❌ Permissions insuffisantes

* Vérifiez que le rôle IAM contient les permissions nécessaires

---

## 👥 Contributeurs

* Votre équipe DevOps 🚀

