import json

# Carregar o mapeamento Bandit para CWE
with open('bandit_to_cwe.json') as f:
    bandit_to_cwe = json.load(f)

# Carregar o relatório do Bandit
with open('bandit_report.json') as f:
    report = json.load(f)

# Adicionar os códigos CWE ao relatório
for result in report.get('results', []):
    bandit_code = result.get('test_id', 'N/A')
    result['cwe'] = bandit_to_cwe.get(bandit_code, 'N/A')

# Salvar o relatório atualizado
with open('bandit_report_with_cwe.json', 'w') as f:
    json.dump(report, f, indent=4)

print("Relatório atualizado com códigos CWE salvo como 'bandit_report_with_cwe.json'")
