# Sistema Triador de Ordens de Serviço de Manutenção Industrial

**Arquitetura Híbrida Neurossimbólica para Classificação, Enriquecimento e Roteamento de Chamados Técnicos de Automação**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)

---

## 📋 Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Características Principais](#características-principais)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Avaliação](#avaliação)
- [API REST](#api-rest)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto

Este projeto implementa um **sistema de triagem automatizada de ordens de serviço** de manutenção industrial utilizando uma **arquitetura híbrida neurossimbólica**. O sistema combina o poder de processamento de linguagem natural de modelos de linguagem (LLM) com a confiabilidade e explicabilidade de sistemas especialistas baseados em regras.

### Contexto Acadêmico

Desenvolvido como protótipo para **monografia de pós-graduação em Controle e Automação no IFSP** (Instituto Federal de São Paulo).

### Problema Abordado

Ordens de serviço em ambientes industriais frequentemente:
- São descritas em linguagem natural não estruturada
- Contêm termos técnicos específicos e abreviações
- Requerem classificação rápida e precisa
- Necessitam roteamento para especialidades corretas
- Precisam priorização baseada em criticidade

---

## 🏗️ Arquitetura

O sistema implementa uma **arquitetura neurossimbólica em duas camadas**:

```
┌─────────────────────────────────────────────────────────────┐
│                   ORDEM DE SERVIÇO                          │
│              (Texto em Linguagem Natural)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│            CAMADA CONEXIONISTA (LLM/SLM)                    │
│  • Extração de informações                                   │
│  • Identificação de entidades                                │
│  • Normalização de termos                                    │
│  • NÃO toma decisões finais                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               VALIDAÇÃO (Pydantic)                          │
│  • Validação de schema JSON                                  │
│  • Garantia de tipos                                         │
│  • Tratamento de erros                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│          TRANSFORMAÇÃO EM FATOS                             │
│  • Conversão para representação simbólica                    │
│  • Derivação de fatos adicionais                             │
│  • Preparação para inferência                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│        CAMADA SIMBÓLICA (Sistema Especialista)              │
│  • Aplicação de regras determinísticas                       │
│  • Forward chaining inference                                │
│  • Decisão final explicável                                  │
│  • Rastreamento de regras aplicadas                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  RESULTADO DA TRIAGEM                        │
│  • Classificação (Elétrica, Mecânica, etc)                   │
│  • Criticidade (Baixa, Média, Alta, Crítica)                 │
│  • Urgência (Baixa, Normal, Alta, Emergencial)               │
│  • Roteamento (Equipe responsável)                           │
│  • Justificativa (Regras aplicadas)                          │
└─────────────────────────────────────────────────────────────┘
```

### Princípio Fundamental

**A LLM interpreta. O Sistema Especialista decide.**

- **Camada Conexionista (LLM)**: Responsável por extrair e estruturar informações do texto não estruturado
- **Camada Simbólica (Expert System)**: Responsável por todas as decisões finais usando regras determinísticas e explicáveis

---

## ✨ Características Principais

### 🤖 Camada de Linguagem (LLM)

- ✅ **Execução Local**: Integração com Ollama para privacidade e controle
- ✅ **Structured Output**: Saída JSON validada por schema
- ✅ **Modelos Intercambiáveis**: Troca fácil de modelos sem modificar código
- ✅ **Validação Rigorosa**: Pydantic valida todas as respostas
- ✅ **Tratamento de Erros**: Sistema continua funcionando mesmo com falhas da LLM

### 🧠 Sistema Especialista

- ✅ **Regras Determinísticas**: 14+ regras explícitas e auditáveis
- ✅ **Forward Chaining**: Motor de inferência clássico
- ✅ **Explicabilidade Total**: Rastreamento de todas as regras aplicadas
- ✅ **Justificativas Automáticas**: Cada decisão é justificada
- ✅ **Fallback Inteligente**: Sempre produz decisão válida

### 🔧 Funcionalidades

- 📊 **Classificação**: Elétrica, Mecânica, Instrumentação, Automação
- 🚨 **Criticidade**: 4 níveis (Baixa, Média, Alta, Crítica)
- ⚡ **Urgência**: 4 níveis (Baixa, Normal, Alta, Emergencial)
- 🎯 **Roteamento**: Direcionamento para equipes especializadas
- 📈 **Priorização**: Escala numérica (1-5)

### 🛠️ Infraestrutura

- 🌐 **API REST**: FastAPI com documentação OpenAPI automática
- 📝 **Logging Estruturado**: JSON logs para observabilidade
- 🧪 **Testes Unitários**: Cobertura de componentes críticos
- 📊 **Sistema de Avaliação**: Métricas automáticas (acurácia, precisão, recall, F1)
- 🎨 **Configuração Flexível**: Variáveis de ambiente via Pydantic Settings

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.10+**
- **Ollama** (para execução local de LLMs)

### 1. Instalar Ollama

**Windows:**
```powershell
# Baixe e instale de: https://ollama.com/download/windows
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Baixar Modelo de Linguagem

```bash
# Modelo recomendado (7B parâmetros, bom equilíbrio)
ollama pull qwen2.5:7b

# Alternativas:
# ollama pull llama3.1:8b
# ollama pull mistral:7b
# ollama pull phi3:medium
```

### 3. Clonar Repositório

```bash
git clone <repo-url>
cd sistema-triador
```

### 4. Criar Ambiente Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 5. Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### 1. Criar Arquivo de Configuração

```bash
cp .env.example .env
```

### 2. Editar Configurações

Edite o arquivo `.env` conforme necessário:

```bash
# Provedor e Modelo LLM
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
LLM_BASE_URL=http://localhost:11434
LLM_TIMEOUT=60
LLM_TEMPERATURE=0.1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# API REST
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Iniciar Ollama

```bash
ollama serve
```

---

## 💻 Uso

### Teste Rápido - Ordem Única

```bash
python scripts/test_single_order.py \
  --description "Motor da esteira 03 apresenta vibração excessiva e ruído durante operação"
```

**Com explicação detalhada:**

```bash
python scripts/test_single_order.py \
  --description "Disjuntor DJ-23 desarma frequentemente" \
  --explain
```

**Salvar resultado:**

```bash
python scripts/test_single_order.py \
  --description "Sensor de temperatura com leitura inconsistente" \
  --output resultado.json
```

### Iniciar API REST

```bash
python scripts/run_api.py
```

Acesse a documentação interativa:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Executar Avaliação Completa

```bash
python scripts/run_evaluation.py
```

**Com dataset customizado:**

```bash
python scripts/run_evaluation.py \
  --dataset data/meu_dataset.json \
  --output avaliacao_resultado.json \
  --verbose
```

### Usar como Biblioteca Python

```python
from src.models.order import ServiceOrder
from src.triage.pipeline import TriagePipeline

# Cria ordem
order = ServiceOrder(
    order_id="OS-001",
    description="Motor apresenta vibração excessiva"
)

# Inicializa pipeline
pipeline = TriagePipeline()

# Processa
result = pipeline.process(order)

# Acessa resultado
print(f"Classificação: {result.decision.classificacao}")
print(f"Criticidade: {result.decision.criticidade}")
print(f"Urgência: {result.decision.urgencia}")
print(f"Regras aplicadas: {result.rules_applied}")
print(f"Justificativa: {result.justificativa}")
```

---

## 📊 Avaliação

O sistema inclui infraestrutura completa para avaliação:

### Dataset Sintético

Incluído: `data/synthetic_orders.json` com 20 ordens variadas

### Métricas Calculadas

- **Acurácia**: Por campo e geral
- **Precisão, Recall, F1-Score**: Por classe
- **Matriz de Confusão**: Visualização de erros
- **Tempo de Inferência**: LLM e Sistema Especialista

### Executar Avaliação

```bash
python scripts/run_evaluation.py
```

**Saída:**
```
======================================================================
RESUMO DA AVALIAÇÃO
======================================================================
Total de avaliações: 20
Acurácia geral: 85.00%

Acurácia por campo:
  Classificação: 90.00%
  Criticidade:   85.00%
  Urgência:      82.50%
  Especialidade: 87.50%

Total de erros por campo:
  Classificação: 2
  Criticidade:   3
  Urgência:      3
  Especialidade: 2
======================================================================
```

---

## 🌐 API REST

### Endpoints Disponíveis

#### `POST /triage`
Processa uma ordem de serviço

**Request:**
```json
{
  "order_id": "OS-001",
  "description": "Motor apresenta vibração excessiva",
  "requester": "Supervisor",
  "location": "Linha 3"
}
```

**Response:**
```json
{
  "order_id": "OS-001",
  "extraction": {
    "equipamento": "motor",
    "sintomas": ["vibração excessiva"],
    "tipo_manutencao": "corretiva",
    ...
  },
  "decision": {
    "classificacao": "Mecânica",
    "criticidade": "Alta",
    "urgencia": "Alta",
    "especialidade": "Eletromecânica",
    "roteamento": "Equipe Mecânica",
    "prioridade": 2
  },
  "rules_applied": ["REGRA_001", "REGRA_102"],
  "justificativa": "Alta criticidade devido a sintomas de vibração..."
}
```

#### `POST /triage/batch`
Processa múltiplas ordens em lote

#### `POST /triage/explain`
Retorna explicação detalhada da decisão

#### `GET /health`
Verifica status do sistema e disponibilidade da LLM

#### `GET /info`
Retorna informações sobre o pipeline

### Exemplo com cURL

```bash
curl -X POST "http://localhost:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "OS-TEST-001",
    "description": "Motor com vibração excessiva"
  }'
```

---

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest
```

### Executar com Cobertura

```bash
pytest --cov=src --cov-report=html
```

### Executar Testes Específicos

```bash
# Apenas modelos
pytest tests/test_models.py

# Apenas sistema especialista
pytest tests/test_expert.py

# Apenas pipeline
pytest tests/test_pipeline.py
```

### Testes Disponíveis

- ✅ Validação de modelos Pydantic
- ✅ Derivação de fatos
- ✅ Aplicação de regras
- ✅ Motor de inferência
- ✅ Pipeline completo
- ✅ Tratamento de erros

---

## 📁 Estrutura do Projeto

```
sistema-triador/
│
├── src/                          # Código-fonte principal
│   ├── api/                      # API REST (FastAPI)
│   ├── config/                   # Configurações
│   ├── evaluation/               # Sistema de avaliação
│   ├── expert/                   # Sistema Especialista (Camada Simbólica)
│   │   ├── facts.py              # Representação de fatos
│   │   ├── rules.py              # Base de regras
│   │   ├── engine.py             # Motor de inferência
│   │   └── decision.py           # Estrutura de decisão
│   ├── llm/                      # Provedor LLM (Camada Conexionista)
│   │   ├── provider.py           # Interface abstrata
│   │   ├── ollama_provider.py    # Implementação Ollama
│   │   ├── prompts.py            # Templates de prompts
│   │   └── schemas.py            # JSON schemas
│   ├── models/                   # Modelos de dados (Pydantic)
│   ├── triage/                   # Pipeline principal
│   └── utils/                    # Utilidades (logging, etc)
│
├── data/                         # Datasets
│   ├── synthetic_orders.json     # Dataset sintético (20 OS)
│   └── evaluation_results/       # Resultados de avaliações
│
├── tests/                        # Testes unitários
│   ├── conftest.py               # Fixtures
│   ├── test_models.py            # Testes de modelos
│   ├── test_expert.py            # Testes do sistema especialista
│   └── test_pipeline.py          # Testes do pipeline
│
├── scripts/                      # Scripts auxiliares
│   ├── run_api.py                # Inicia API REST
│   ├── run_evaluation.py         # Executa avaliação
│   ├── test_single_order.py      # Testa ordem única
│   └── generate_dataset.py       # Gera datasets
│
├── .env.example                  # Exemplo de configuração
├── .gitignore                    # Arquivos ignorados pelo git
├── requirements.txt              # Dependências Python
└── README.md                     # Este arquivo
```

---

## 🔧 Adicionando Novas Regras

Para adicionar regras ao sistema especialista, edite `src/expert/rules.py`:

```python
# Nova regra de exemplo
self.rules.append(Rule(
    id="REGRA_XXX",
    name="Nome da Regra",
    description="Descrição do que a regra faz",
    priority=50,  # Menor = maior prioridade
    condition=lambda facts: (
        # Condição para aplicar a regra
        facts.has_symptom("seu_sintoma")
    ),
    action=lambda facts, decision: (
        # Ação a executar
        decision.classificacao = "Sua Classificação"
    )
))
```

---

## 📝 Exemplos de Uso

### Exemplo 1: Problema Elétrico Crítico

**Entrada:**
```
"Curto-circuito detectado na fiação do motor M-08. 
Fusível queimado e sinais de aquecimento. 
EQUIPAMENTO DESLIGADO POR SEGURANÇA."
```

**Saída:**
- Classificação: **Elétrica**
- Criticidade: **Crítica**
- Urgência: **Emergencial**
- Regras: REGRA_001 (sintomas críticos), REGRA_101 (termos elétricos)

### Exemplo 2: Manutenção Preventiva

**Entrada:**
```
"Realizar troca do óleo do compressor C-05 
conforme programação trimestral."
```

**Saída:**
- Classificação: **Mecânica**
- Criticidade: **Média**
- Urgência: **Normal**
- Regras: REGRA_202 (preventiva = normal), REGRA_102 (termos mecânicos)

### Exemplo 3: Instrumentação

**Entrada:**
```
"Sensor de temperatura ST-102 indicando valores 
inconsistentes. Leituras variando entre -10°C e 150°C."
```

**Saída:**
- Classificação: **Instrumentação**
- Criticidade: **Média**
- Urgência: **Normal**
- Regras: REGRA_103 (termos instrumentação)

---

## 🤝 Contribuindo

Este é um protótipo acadêmico, mas contribuições são bem-vindas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte de uma monografia de pós-graduação no IFSP.

---

## 👨‍🎓 Autor

Desenvolvido como protótipo para monografia de **Pós-Graduação em Controle e Automação** no **IFSP** (Instituto Federal de São Paulo).

---

## 🙏 Agradecimentos

- **IFSP** - Instituto Federal de São Paulo
- **Comunidade Ollama** - Por tornar LLMs locais acessíveis
- **FastAPI** - Framework web moderno e eficiente
- **Pydantic** - Validação de dados robusta

---

## 📚 Referências

- Arquitetura Neurossimbólica: Combina aprendizado conexionista com raciocínio simbólico
- Sistemas Especialistas: Representação de conhecimento via regras
- Forward Chaining: Método de inferência clássico em IA
- Ollama: Plataforma para execução local de LLMs

---

## 🐛 Problemas Conhecidos e Soluções

### Ollama não está disponível

**Problema:** Erro "LLM provider not available"

**Solução:**
```bash
# Inicie o Ollama
ollama serve

# Em outro terminal, verifique modelos disponíveis
ollama list

# Baixe um modelo se necessário
ollama pull qwen2.5:7b
```

### JSON inválido da LLM

O sistema está preparado para isso. A validação Pydantic captura erros e o sistema especialista continua funcionando com valores padrão.

### Testes falhando

```bash
# Reinstale dependências
pip install -r requirements.txt --force-reinstall

# Limpe cache do pytest
pytest --cache-clear
```

---

## 📞 Suporte

Para questões relacionadas ao projeto acadêmico:
- Consulte a documentação inline no código
- Verifique os exemplos em `scripts/`
- Analise os testes em `tests/`

---

**🎓 Desenvolvido com fins acadêmicos e educacionais**
