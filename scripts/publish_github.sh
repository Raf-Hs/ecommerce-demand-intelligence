#!/usr/bin/env bash
# Run this after `gh auth login` to publish the project to GitHub.
set -euo pipefail

REPO="ecommerce-demand-intelligence"
USER=$(gh api user --jq .login)

if gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  echo "Repository already exists: $USER/$REPO"
else
  gh repo create "$REPO" \
    --public \
    --description "A multi-source E-commerce Data Engineering platform for retail demand intelligence and inventory management, featuring Python, SQL, Apache Spark, DuckDB, Parquet, dbt, Airflow, and production-oriented data pipelines."
  echo "Repository created."
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$USER/$REPO.git"
git push -u origin main
echo "Published to https://github.com/$USER/$REPO"
