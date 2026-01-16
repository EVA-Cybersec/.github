# EVA-Cybersec - DevSecOps Pipeline Template

Template público de segurança DevSecOps mantido pela EVA-Cybersec. Fornece scans de segurança reutilizáveis para qualquer organização/repositório.

---

## Scanners Incluídos

| Scanner | Tipo | Descrição |
|---------|------|-----------|
| **Semgrep** | SAST | Análise estática de código para vulnerabilidades, bugs e más práticas |
| **Gitleaks** | Secrets | Detecção de credenciais e secrets vazados no código e histórico git |
| **Trivy FS** | SCA + IaC | Análise de dependências (CVEs) e misconfigurations em IaC |
| **Trivy Image** | Container | Scan de imagens Docker para vulnerabilidades |

---

## Como Usar

### 1. Configurar Secrets no Repositório do Cliente

No repositório onde o workflow será executado, adicione os seguintes secrets em **Settings > Secrets and variables > Actions**:

| Secret | Obrigatório | Descrição |
|--------|-------------|-----------|
| `GITLEAKS_LICENSE` | Não* | Licença do Gitleaks |
| `DEFECTDOJO_URL` | Não** | URL do DefectDojo (ex: `https://defectdojo.empresa.com`) |
| `DEFECTDOJO_API_KEY` | Não** | Token de API do DefectDojo |

\* Obrigatório para organizações com mais de 10 colaboradores
\*\* Obrigatório apenas se `defectdojo_import` for `true`

### 2. Criar Workflow no Repositório do Cliente

Crie o arquivo `.github/workflows/security.yml` no repositório do cliente:

```yaml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    with:
      defectdojo_import: true
      defectdojo_product_name: "MeuProduto"
      defectdojo_engagement_name: "CI/CD Pipeline"
    secrets:
      GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_API_KEY: ${{ secrets.DEFECTDOJO_API_KEY }}
```

---

## Parâmetros de Configuração

### Inputs - Controle de Scans

| Input | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `run_semgrep` | boolean | `true` | Executar Semgrep SAST scan |
| `run_gitleaks` | boolean | `true` | Executar Gitleaks secrets scan |
| `run_trivy_fs` | boolean | `true` | Executar Trivy filesystem scan (SCA + IaC) |
| `gitleaks_full_scan` | boolean | `false` | Se `true`, escaneia TODO o histórico git. Se `false`, apenas commits novos |
| `upload_sarif` | boolean | `true` | Fazer upload dos artefatos SARIF gerados |

### Inputs - Docker Image Scan

| Input | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `image_built` | boolean | `false` | Se `true`, executa scan de imagem Docker |
| `image_name` | string | `""` | Nome da imagem Docker para scan (ex: `myapp:latest`) |

### Inputs - Exclusões

| Input | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `extra_excludes` | string | `""` | Exclusões adicionais separadas por espaço (ex: `.nuxt/ .output/ vendor/`) |

### Inputs - DefectDojo

| Input | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `defectdojo_import` | boolean | `false` | Se `true`, envia resultados para o DefectDojo |
| `defectdojo_product_name` | string | `""` | Nome do Product no DefectDojo |
| `defectdojo_engagement_name` | string | `""` | Nome do Engagement no DefectDojo |

### Secrets

| Secret | Obrigatório | Descrição |
|--------|-------------|-----------|
| `GITLEAKS_LICENSE` | Não* | Licença do Gitleaks |
| `DEFECTDOJO_URL` | Condicional** | URL do servidor DefectDojo |
| `DEFECTDOJO_API_KEY` | Condicional** | Token de API do DefectDojo |

\* Obrigatório para organizações com mais de 10 colaboradores
\*\* Obrigatório apenas se `defectdojo_import` for `true`

---

## Exemplos de Uso

### Exemplo Básico (todos os scans, sem DefectDojo)

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    secrets:
      GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

### Exemplo Completo (com DefectDojo)

```yaml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    with:
      defectdojo_import: true
      defectdojo_product_name: "API-Backend"
      defectdojo_engagement_name: "CI/CD Pipeline - GitHub Actions"
    secrets:
      GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_API_KEY: ${{ secrets.DEFECTDOJO_API_KEY }}
```

### Exemplo: Scan de Imagem Docker

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_name: ${{ steps.build.outputs.image }}
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        id: build
        run: |
          docker build -t myapp:${{ github.sha }} .
          echo "image=myapp:${{ github.sha }}" >> $GITHUB_OUTPUT

  security:
    needs: build
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    with:
      image_built: true
      image_name: ${{ needs.build.outputs.image_name }}
      defectdojo_import: true
      defectdojo_product_name: "MyApp"
      defectdojo_engagement_name: "CI/CD Pipeline"
    secrets:
      GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_API_KEY: ${{ secrets.DEFECTDOJO_API_KEY }}
```

### Exemplo: Gitleaks Full Scan (histórico completo)

```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    with:
      gitleaks_full_scan: true
      defectdojo_import: true
      defectdojo_product_name: "Legacy-Project"
      defectdojo_engagement_name: "Initial Security Audit"
    secrets:
      GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_API_KEY: ${{ secrets.DEFECTDOJO_API_KEY }}
```

### Exemplo: Apenas Trivy (SCA/IaC)

```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    with:
      run_semgrep: false
      run_gitleaks: false
      run_trivy_fs: true
```

### Exemplo: Com Exclusões Customizadas

```yaml
jobs:
  security:
    uses: EVA-Cybersec/.github/.github/workflows/devsecops-template.yml@main
    with:
      extra_excludes: ".nuxt/ .output/ generated/ third_party/"
      defectdojo_import: true
      defectdojo_product_name: "Nuxt-App"
      defectdojo_engagement_name: "CI/CD Pipeline"
    secrets:
      GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
      DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
      DEFECTDOJO_API_KEY: ${{ secrets.DEFECTDOJO_API_KEY }}
```

---

## Exclusões Padrão

O Semgrep já exclui automaticamente os seguintes diretórios/arquivos:

- `node_modules/`, `dist/`, `build/`, `coverage/`
- `.git/`, `vendor/`, `__pycache__/`
- `.venv/`, `venv/`, `target/`, `bin/`, `obj/`
- `*.min.js`, `*.min.css`, `*.map`, `*.lock`

Use o input `extra_excludes` para adicionar exclusões específicas do seu projeto.

---

## Artefatos Gerados

Cada scan gera artefatos SARIF que ficam disponíveis por 30 dias:

| Artefato | Descrição |
|----------|-----------|
| `semgrep-sarif` | Resultados do Semgrep SAST |
| `gitleaks-sarif` | Resultados do Gitleaks Secrets |
| `trivy-fs-sarif` | Resultados do Trivy (dependências + IaC) |
| `trivy-image-sarif` | Resultados do Trivy Image (se habilitado) |

---

## Integração DefectDojo

### Hierarquia

```
Product Type > Product > Engagement > Test > Finding
```

### Comportamento

- **auto_create_context**: Cria automaticamente Product e Engagement se não existirem
- **close_old_findings**: Fecha findings antigos que não aparecem mais nos scans
- **deduplication_on_engagement**: Evita duplicação de findings no mesmo engagement

### Obter API Token

1. Acesse seu DefectDojo
2. Vá em **Configurações** (ícone de engrenagem)
3. Clique em **API v2 Key**
4. Copie o token e adicione como secret no repositório

---

## Deduplicação Automática de Findings

### O Problema

Quando Semgrep e Gitleaks estão habilitados, ambos podem detectar secrets no código (API keys, tokens, senhas, etc.), gerando findings duplicados no DefectDojo.

### A Solução

O template inclui um job de deduplicação automática (`deduplicate-sarif`) que:

1. **Executa automaticamente** entre os scans e o import para o DefectDojo
2. **Compara os resultados** do Semgrep e Gitleaks por arquivo e linha
3. **Remove duplicatas** do Semgrep quando Gitleaks já detectou o mesmo secret
4. **Preserva Gitleaks** como fonte autoritativa para detecção de secrets

### Como Funciona

```
┌─────────────┐     ┌─────────────┐
│   Semgrep   │     │  Gitleaks   │
│   (SAST)    │     │  (Secrets)  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └───────┬───────────┘
               ▼
    ┌─────────────────────┐
    │ Deduplicate SARIF   │
    │ (Remove duplicatas) │
    └──────────┬──────────┘
               ▼
    ┌─────────────────────┐
    │  DefectDojo Import  │
    │  (Findings únicos)  │
    └─────────────────────┘
```

### Regras de Deduplicação

| Cenário | Ação |
|---------|------|
| Secret detectado por ambos | Mantém Gitleaks, remove Semgrep |
| Secret detectado apenas por Gitleaks | Mantém Gitleaks |
| Secret detectado apenas por Semgrep | Mantém Semgrep |
| Finding não relacionado a secrets | Mantém (sem alteração) |

### Padrões Reconhecidos como Secrets

O deduplicador identifica secrets no Semgrep através de padrões no `ruleId`:

- `*secret*`, `*password*`, `*credential*`
- `*api-key*`, `*api_key*`, `*apikey*`
- `*token*`, `*auth*`, `*private*`
- `*jwt*`, `*bearer*`

### Comportamento

- **Ativação automática**: Executado apenas quando `run_semgrep` e `run_gitleaks` são `true` (padrão)
- **Sem configuração**: Não requer nenhum input adicional
- **Tolerante a falhas**: Usa `continue-on-error` para não bloquear o pipeline
- **Transparente**: Log detalhado mostra quantos findings foram removidos

### Exemplo de Log

```
Processing SARIF deduplication...
  Semgrep findings loaded: 15
  Gitleaks findings loaded: 4
  Gitleaks locations (file:line): 4
  Semgrep secrets findings matching Gitleaks: 3
  Semgrep findings after deduplication: 12
  Duplicates removed: 3
```

---

## Requisitos

### DefectDojo (se habilitado)

- DefectDojo v2.x ou superior
- Token de API com permissões para criar Products, Engagements e importar scans

### Gitleaks License

- Gratuito para repositórios pessoais e organizações com até 10 colaboradores
- Requer licença para organizações maiores: [gitleaks.io](https://gitleaks.io)

---

## Suporte

- **Repositório**: https://github.com/EVA-Cybersec/.github
- **Contato**: contato@eva-cybersec.com
