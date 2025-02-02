#!/bin/bash

# Diretório onde os relatórios serão armazenados
mkdir -p security_tests
cd security_tests || exit 1

# Repositórios a serem testados
REPOS=(
    "https://github.com/digininja/DVWA"
    "https://github.com/juice-shop/juice-shop"
    "https://github.com/OWASP/SecurityShepherd"
)

# Clonar e analisar cada repositório
for repo in "${REPOS[@]}"; do
    repo_name=$(basename $repo .git)
    if [ -d "$repo_name" ]; then
        echo "Repositório $repo_name já existe, pulando clone..."
    else
        git clone $repo
    fi
    cd $repo_name || continue
    bandit -r . -f json -o ../bandit_report_${repo_name}.json || echo "Erro ao rodar Bandit em $repo_name"
    cd ..
done

echo "Análises concluídas! Relatórios disponíveis em security_tests/"
