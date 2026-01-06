# EVA-Cybersec - Reusable Security Workflows

Repositório público com templates de workflows reutilizáveis para pipelines de DevSecOps.

## Workflows Disponíveis

### `security-scan.yml` - Pipeline de Segurança Completo

Workflow reutilizável que executa múltiplos scanners de segurança e envia os resultados para o DefectDojo.

#### Scanners Incluídos

| Scanner | Tipo | Descrição |
|---------|------|-----------|
| **Trivy** | SCA + IaC | Análise de dependências e configurações de infraestrutura |
| **Gitleaks** | Secrets | Detecção de credenciais e secrets vazados no código |
| **Semgrep** | SAST | Análise estática de código para vulnerabilidades |

---

## Como Usar

### 1. Configurar Secrets no Repositório do Cliente

No repositório onde o workflow será executado, adicione os seguintes secrets em **Settings > Secrets and variables > Actions**:

| Secret | Descrição | Exemplo |
|--------|-----------|---------|
| `DEFECTDOJO_URL` | URL do DefectDojo | `https://defectdojo.exemplo.com` |
| `DEFECTDOJO_TOKEN` | API Token do DefectDojo | `abc123...` |

### 2. Criar Workflow no Repositório do Cliente

Crie o arquivo `.github/workflows/security.yml` no repositório do cliente:

```yaml
name: Security Scan

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master]
  workflow_dispatch:  # Permite execução manual

jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/security-scan.yml@main
    with:
      product_name: "Nome-Do-Produto"
    secrets:
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
```

---

## Parâmetros de Configuração

### Inputs (Configurações)

| Input | Tipo | Obrigatório | Default | Descrição |
|-------|------|-------------|---------|-----------|
| `product_name` | string | ✅ Sim | - | Nome do produto no DefectDojo |
| `engagement_name` | string | Não | `CI/CD Security Scan` | Nome do engagement no DefectDojo |
| `trivy_enabled` | boolean | Não | `true` | Habilitar scan Trivy |
| `gitleaks_enabled` | boolean | Não | `true` | Habilitar scan Gitleaks |
| `semgrep_enabled` | boolean | Não | `true` | Habilitar scan Semgrep |
| `upload_to_defectdojo` | boolean | Não | `true` | Fazer upload para DefectDojo |
| `trivy_severity` | string | Não | `CRITICAL,HIGH,MEDIUM` | Severidades do Trivy |
| `semgrep_config` | string | Não | `p/default` | Configuração do Semgrep |

### Secrets (Credenciais)

| Secret | Obrigatório | Descrição |
|--------|-------------|-----------|
| `DEFECTDOJO_URL` | Condicional* | URL do DefectDojo |
| `DEFECTDOJO_TOKEN` | Condicional* | API Token do DefectDojo |

*Obrigatório apenas se `upload_to_defectdojo` for `true`

---

## Exemplos de Uso

### Exemplo Básico
```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/security-scan.yml@main
    with:
      product_name: "Meu-Projeto"
    secrets:
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
```

### Exemplo com Configurações Customizadas
```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/security-scan.yml@main
    with:
      product_name: "API-Backend"
      engagement_name: "Sprint 42 - Security Review"
      trivy_severity: "CRITICAL,HIGH"
      semgrep_config: "p/owasp-top-ten"
    secrets:
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
```

### Exemplo: Apenas Trivy e Gitleaks (sem Semgrep)
```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/security-scan.yml@main
    with:
      product_name: "Infra-Terraform"
      semgrep_enabled: false
    secrets:
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
```

### Exemplo: Scan sem Upload para DefectDojo
```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/security-scan.yml@main
    with:
      product_name: "Projeto-Teste"
      upload_to_defectdojo: false
```

---

## Configurações do Semgrep

O parâmetro `semgrep_config` aceita diversas configurações:

| Configuração | Descrição |
|--------------|-----------|
| `p/default` | Regras padrão do Semgrep |
| `p/owasp-top-ten` | Focado nas OWASP Top 10 |
| `p/security-audit` | Auditoria de segurança completa |
| `p/python` | Regras específicas para Python |
| `p/javascript` | Regras específicas para JavaScript |
| `p/golang` | Regras específicas para Go |

Múltiplas configurações podem ser combinadas: `p/owasp-top-ten p/security-audit`

---

## Artefatos Gerados

Cada scan gera artefatos que ficam disponíveis por 30 dias:

- `trivy-results` - Resultados do Trivy (FS + IaC)
- `gitleaks-results` - Resultados do Gitleaks
- `semgrep-results` - Resultados do Semgrep

---

## Requisitos no DefectDojo

Para que o upload funcione corretamente:

1. **Produto**: Será criado automaticamente se não existir (`auto_create_context=true`)
2. **Engagement**: Será criado automaticamente se não existir
3. **Permissões**: O token precisa ter permissão para criar produtos/engagements e importar scans

---

## Suporte

Em caso de dúvidas ou problemas, entre em contato com a equipe EVA-Cybersec.
