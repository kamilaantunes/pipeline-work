import json
import os
from colorama import Fore, Style

def calcular_score(report_path):
    """Calculate a score based on the vulnerabilities found by the bandit."""
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}File {report_path} not found.{Style.RESET_ALL}")
        return None

    # Contar vulnerabilidades por severidade
    low, medium, high = 0, 0, 0
    
    for result in report.get("results", []):
        severity = result.get("issue_severity", "").lower()
        if severity == "low":
            low += 1
        elif severity == "medium":
            medium += 1
        elif severity == "high":
            high += 1
    
    # Fórmula do score
    score = max(0, 100 - (low * 1 + medium * 3 + high * 5))
    return score, low, medium, high

def criar_issue_github(token, repo, title, body):
    """Create an issue on GitHub if critical vulnerabilities are detected."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": title, "body": body}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"{Fore.GREEN}Issue succesfully created on  GitHub!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Error creating issue: {response.text}{Style.RESET_ALL}")

def gerar_relatorio_markdown(score_atual, score_anterior, low, medium, high):
    """Generate a report in Markdown format."""
    with open("security_report.md", "w") as f:
        f.write("# Security report\n\n")
        f.write(f"*Current score:* {score_atual}\n")
        if score_anterior is not None:
            f.write(f"*Previous score:* {score_anterior}\n")
            f.write(f"*Score variation:* {'+' if score_atual - score_anterior >= 0 else ''}{score_atual - score_anterior}\n\n")
        f.write("## Vulnerability Details\n")
        f.write(f"- *Low:* {low}\n")
        f.write(f"- *Medium:* {medium}\n")
        f.write(f"- *High:* {high}\n")
    print(f"{Fore.GREEN}Report saved in  security_report.md{Style.RESET_ALL}")

def comparar_scores(atual_path, anterior_path):
    """Compares the current score with the score from the last report and alerts you in case of worsening."""
    score_atual, low_a, medium_a, high_a = calcular_score(atual_path)
    score_anterior, low_b, medium_b, high_b = calcular_score(anterior_path) if os.path.exists(anterior_path) else (None, 0, 0, 0)
    
    print("=== Security Comparison  ===")
    print(f"{Fore.CYAN}Current score: {score_atual}{Style.RESET_ALL}")
    if score_anterior is not None:
        print(f"{Fore.CYAN}Previous score: {score_anterior}{Style.RESET_ALL}")
        diff = score_atual - score_anterior
        print(f"Score variation: {'+' if diff >= 0 else ''}{diff}")
        if high_a > high_b:
            print(f"{Fore.RED}ALERT: Increased high vulnerabilities!{Style.RESET_ALL}")
    else:
        print("No previous reports found.")
    
    print("\n=== Vulnerability Details ===")
    print(f"{Fore.YELLOW}Low: {low_a} ({low_a - low_b:+}){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Medium: {medium_a} ({medium_a - medium_b:+}){Style.RESET_ALL}")
    print(f"{Fore.RED}High: {high_a} ({high_a - high_b:+}){Style.RESET_ALL}")
    
    gerar_relatorio_markdown(score_atual, score_anterior, low_a, medium_a, high_a)
    
    # Salvar o relatório atual como referência para a próxima execução
    with open(anterior_path, 'w') as f:
        json.dump(json.load(open(atual_path)), f, indent=4)
    
    return score_atual

# Caminhos dos relatórios
atual_report_path = "bandit_report_with_cwe.json"
anterior_report_path = "previous_bandit_report.json"

# Configuração do GitHub (adicionar token e repositório ao pipeline)
github_token = os.getenv("GITHUB_TOKEN")  # Definir como variável de ambiente
repo = "kamilaantunes/bandit-cwe-pipeline"

# Comparar scores e criar issue se necessário
comparar_scores(atual_report_path, anterior_report_path, github_token, repo)
