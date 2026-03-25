import requests
import csv
import base64
import os
import sys

# =========================
# CONFIGURAÇÃO
# =========================
org = "SUA_ORG_AQUI"

# =========================
# TOKEN (via variável de ambiente)
# =========================
pat = os.getenv("AZURE_DEVOPS_PAT")

if not pat:
    print("❌ Erro: variável de ambiente AZURE_DEVOPS_PAT não definida")
    print("Use: export AZURE_DEVOPS_PAT=seu_token")
    sys.exit(1)

# =========================
# AUTH HEADER
# =========================
token = base64.b64encode(f":{pat}".encode()).decode()

headers = {
    "Authorization": f"Basic {token}"
}

# =========================
# BUSCAR PROJETOS
# =========================
projects_url = f"https://dev.azure.com/{org}/_apis/projects?api-version=7.0"

response = requests.get(projects_url, headers=headers)

if response.status_code != 200:
    print(f"❌ Erro ao buscar projetos: {response.status_code}")
    print(response.text)
    sys.exit(1)

projects = response.json()

rows = []

# =========================
# LOOP PROJETOS / REPOS
# =========================
for p in projects.get('value', []):
    project_name = p['name']
    print(f"🔍 Processando projeto: {project_name}")

    repos_url = f"https://dev.azure.com/{org}/{project_name}/_apis/git/repositories?api-version=7.0"
    repos_response = requests.get(repos_url, headers=headers)

    if repos_response.status_code != 200:
        print(f"⚠️ Erro ao buscar repos do projeto {project_name}")
        continue

    repos = repos_response.json()

    for r in repos.get('value', []):
        rows.append([
            org,
            project_name,
            r.get('name'),
            r.get('webUrl')
        ])

# =========================
# EXPORTAR CSV
# =========================
output_file = "azure_devops_repos.csv"

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Organizacao', 'Projeto', 'Repositorio', 'Url'])
    writer.writerows(rows)

print(f"✅ CSV gerado com sucesso: {output_file}")
