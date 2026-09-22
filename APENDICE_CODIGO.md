# APÊNDICE - Visão Geral do Sistema Implementado

## Resumo da Implementação

Este apêndice apresenta uma visão geral da arquitetura e implementação do **Sistema Triador de Ordens de Serviço de Manutenção Industrial**, desenvolvido como protótipo para esta monografia. O sistema utiliza uma arquitetura híbrida neurossimbólica que combina Large Language Models (LLM) com sistemas especialistas baseados em regras.

---

## 1. Arquitetura do Sistema

### 1.1 Visão Geral

O sistema implementa uma arquitetura neurossimbólica em duas camadas distintas:

```
┌─────────────────────────────────────────────────────────────┐
│              ORDEM DE SERVIÇO (Texto Natural)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         CAMADA CONEXIONISTA (Large Language Model)          │
│  • Extração de entidades e atributos                        │
│  • Normalização de termos técnicos                          │
│  • Identificação de sintomas e equipamentos                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              VALIDAÇÃO E TRANSFORMAÇÃO                      │
│  • Schema JSON (Pydantic)                                   │
│  • Derivação de fatos simbólicos                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│       CAMADA SIMBÓLICA (Sistema Especialista)               │
│  • Forward Chaining Inference Engine                        │
│  • Aplicação de regras determinísticas                      │
│  • Geração de decisão e justificativa                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     RESULTADO DA TRIAGEM                    │
│  • Classificação técnica                                    │
│  • Níveis de criticidade e urgência                         │
│  • Roteamento e priorização                                 │
│  • Rastreabilidade completa                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Princípio Arquitetural

**Separação de Responsabilidades:**
- **Camada Conexionista (LLM)**: Responsável exclusivamente pela interpretação e extração de informações do texto não estruturado.
- **Camada Simbólica (Expert System)**: Responsável por todas as decisões finais através de regras explícitas e auditáveis.

Esta separação garante **explicabilidade**, **auditabilidade** e **controle** sobre as decisões do sistema, atributos essenciais para aplicações industriais críticas.

---

## 2. Componentes Principais

### 2.1 Modelos de Dados (Pydantic)

O sistema utiliza validação rigorosa de dados através de modelos Pydantic:

- **ServiceOrder**: Representa a ordem de serviço de entrada
- **ExtractionResult**: Schema JSON para saída estruturada da LLM
- **Facts**: Representação simbólica dos fatos extraídos
- **ExpertDecision**: Estrutura da decisão do sistema especialista
- **TriageResult**: Resultado completo com metadados

### 2.2 Provedor LLM (Ollama)

Implementação local de Large Language Models:

- **Execução Local**: Privacidade de dados garantida
- **Structured Output**: JSON Schema validation
- **Modelos Intercambiáveis**: Suporte a múltiplos modelos (Qwen, Llama, Mistral)
- **Tratamento Robusto de Erros**: Sistema continua funcionando mesmo com falhas da LLM

**Modelos Testados:**
- Qwen 2.5 (7B parâmetros) - Recomendado
- Llama 3.1 (8B parâmetros)
- Mistral 7B

### 2.3 Sistema Especialista

#### 2.3.1 Base de Conhecimento (Rules)

O sistema implementa 14+ regras determinísticas organizadas em categorias:

**Categorias de Regras:**
1. **Sintomas Críticos**: Identificação de condições de emergência
2. **Classificação Técnica**: Determinação da disciplina (Elétrica, Mecânica, etc.)
3. **Tipo de Manutenção**: Impacto na urgência (Preventiva, Corretiva, Preditiva)
4. **Impacto Operacional**: Análise de paradas e perdas
5. **Equipamentos Críticos**: Tratamento especial para ativos essenciais

**Estrutura de uma Regra:**
```python
Rule(
    id="REGRA_XXX",
    name="Nome da Regra",
    description="Descrição técnica",
    priority=N,  # Menor valor = maior prioridade
    condition=lambda facts: <expressão booleana>,
    action=lambda facts, decision: <ação>
)
```

#### 2.3.2 Motor de Inferência (Inference Engine)

Implementa **Forward Chaining** clássico:

1. **Inicialização**: Carrega base de regras ordenadas por prioridade
2. **Avaliação**: Testa condições de cada regra contra os fatos
3. **Execução**: Aplica ações das regras que satisfazem condições
4. **Rastreamento**: Registra todas as regras aplicadas
5. **Justificativa**: Gera explicação textual da decisão

**Garantias do Motor:**
- Sempre produz decisão válida (fallback para valores padrão)
- Rastreabilidade completa (lista de regras aplicadas)
- Explicabilidade total (justificativas geradas automaticamente)

#### 2.3.3 Representação de Fatos (Facts)

Os fatos são derivados da extração da LLM e incluem:

**Fatos Diretos:**
- Equipamento identificado
- Sintomas descritos
- Tipo de manutenção
- Localização e solicitante

**Fatos Derivados (calculados automaticamente):**
- `has_critical_symptoms`: Presença de sintomas críticos
- `has_electrical_terms`: Presença de terminologia elétrica
- `has_mechanical_terms`: Presença de terminologia mecânica
- `has_instrumentation_terms`: Presença de terminologia de instrumentação
- `has_operational_impact`: Indicação de impacto operacional

---

## 3. Pipeline de Processamento

### 3.1 Fluxo Principal (TriagePipeline)

O pipeline orquestra o fluxo completo em 4 etapas:

**Etapa 1 - Extração (LLM):**
```python
extraction = llm_provider.extract_information(
    order_description=order.description,
    order_id=order.order_id
)
```
- Tempo médio: 2-5 segundos (depende do modelo)
- Saída: JSON estruturado validado

**Etapa 2 - Transformação:**
```python
facts = Facts.from_extraction(extraction)
```
- Conversão para representação simbólica
- Derivação automática de fatos adicionais

**Etapa 3 - Inferência:**
```python
expert_decision = inference_engine.infer(facts)
```
- Tempo médio: < 10 milissegundos
- Aplicação de regras em ordem de prioridade

**Etapa 4 - Resultado:**
```python
result = TriageResult(
    order_id=order.order_id,
    extraction=extraction,
    decision=decision,
    rules_applied=expert_decision.regras_aplicadas,
    justificativa=expert_decision.justificativa,
    metadata=metadata
)
```

### 3.2 Metadados de Performance

Cada resultado inclui métricas de performance:
- `llm_inference_time_ms`: Tempo da camada conexionista
- `expert_inference_time_ms`: Tempo da camada simbólica
- `total_time_ms`: Tempo total de processamento
- `extraction_success`: Status da extração LLM

---

## 4. Interface de Uso

### 4.1 API REST (FastAPI)

Endpoints implementados:

- `POST /triage`: Processa ordem individual
- `POST /triage/batch`: Processamento em lote
- `POST /triage/explain`: Explicação detalhada
- `GET /health`: Status do sistema
- `GET /info`: Informações arquiteturais

**Documentação Automática:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4.2 Scripts de Linha de Comando

- `test_single_order.py`: Teste de ordem única
- `run_evaluation.py`: Avaliação com dataset
- `run_api.py`: Inicialização do servidor
- `generate_dataset.py`: Geração de dados sintéticos

### 4.3 Uso Programático

```python
from src.triage.pipeline import TriagePipeline
from src.models.order import ServiceOrder

# Inicializa pipeline
pipeline = TriagePipeline()

# Cria ordem
order = ServiceOrder(
    order_id="OS-001",
    description="Motor apresenta vibração excessiva"
)

# Processa
result = pipeline.process(order)

# Acessa resultado
print(f"Classificação: {result.decision.classificacao}")
print(f"Criticidade: {result.decision.criticidade}")
print(f"Regras: {result.rules_applied}")
```

---

## 5. Sistema de Avaliação

### 5.1 Métricas Implementadas

O sistema inclui infraestrutura completa de avaliação:

- **Acurácia**: Por campo e geral
- **Precisão, Recall, F1-Score**: Por classe de classificação
- **Matriz de Confusão**: Análise de erros
- **Tempo de Inferência**: Performance de ambas as camadas
- **Taxa de Sucesso da Extração**: Confiabilidade da LLM

### 5.2 Dataset Sintético

Incluído dataset com 20 ordens de serviço variadas cobrindo:
- Diferentes disciplinas (Elétrica, Mecânica, Instrumentação, Automação)
- Diversos níveis de criticidade
- Múltiplos tipos de manutenção
- Diferentes estilos de redação

---

## 6. Tecnologias Utilizadas

### 6.1 Core
- **Python 3.10+**: Linguagem principal
- **Pydantic 2.x**: Validação de dados e schemas
- **FastAPI**: Framework web assíncrono

### 6.2 LLM
- **Ollama**: Execução local de modelos de linguagem
- **JSON Schema**: Structured output validation

### 6.3 Testes e Qualidade
- **Pytest**: Framework de testes unitários
- **Coverage.py**: Análise de cobertura de código

### 6.4 Logging e Observabilidade
- **Logging estruturado JSON**: Rastreabilidade completa
- **Metadados de performance**: Métricas por requisição

---

## 7. Características Técnicas Relevantes

### 7.1 Robustez

- **Fallback Inteligente**: Sistema sempre produz decisão válida mesmo com falha da LLM
- **Validação em Camadas**: Pydantic, JSON Schema, regras de negócio
- **Tratamento de Erros**: Captura e logging de exceções

### 7.2 Explicabilidade

- **Rastreamento de Regras**: Todas as regras aplicadas são registradas
- **Justificativas Automáticas**: Texto explicativo gerado para cada decisão
- **Modo Explicação**: Endpoint dedicado para análise detalhada

### 7.3 Extensibilidade

- **Base de Regras Modular**: Fácil adição de novas regras
- **Provedores LLM Intercambiáveis**: Interface abstrata permite múltiplas implementações
- **Configuração Flexível**: Variáveis de ambiente para todos os parâmetros

### 7.4 Performance

- **Latência Total**: ~2-5 segundos por ordem
  - LLM: 2-5 segundos (95% do tempo)
  - Expert System: < 10ms (5% do tempo)
- **Escalabilidade**: Processamento em lote suportado
- **Overhead Mínimo**: Pipeline adiciona < 1ms de overhead

---

## 8. Estrutura de Diretórios

```
sistema-triador/
├── src/                    # Código-fonte principal
│   ├── api/                # Endpoints REST
│   ├── config/             # Configurações
│   ├── evaluation/         # Sistema de avaliação
│   ├── expert/             # Sistema especialista (14 arquivos)
│   │   ├── facts.py        # Representação simbólica
│   │   ├── rules.py        # Base de conhecimento
│   │   ├── engine.py       # Motor de inferência
│   │   └── decision.py     # Estrutura de decisão
│   ├── llm/                # Camada conexionista
│   │   ├── provider.py     # Interface abstrata
│   │   ├── ollama_provider.py
│   │   ├── prompts.py      # Templates de prompts
│   │   └── schemas.py      # JSON schemas
│   ├── models/             # Modelos Pydantic
│   ├── triage/             # Pipeline principal
│   └── utils/              # Utilidades
├── data/                   # Datasets e resultados
├── tests/                  # Testes unitários (pytest)
├── scripts/                # Scripts auxiliares
└── requirements.txt        # Dependências Python
```

---

## 9. Decisões de Design

### 9.1 Arquitetura Híbrida

**Motivação**: Combinar interpretação flexível de linguagem natural (LLM) com decisões determinísticas e auditáveis (regras).

**Benefícios**:
- Explicabilidade total das decisões
- Controle sobre lógica crítica
- Robustez a falhas da LLM
- Facilidade de ajuste de regras

### 9.2 Execução Local de LLM

**Motivação**: Privacidade de dados industriais sensíveis.

**Benefícios**:
- Dados não saem do ambiente controlado
- Sem custos por requisição
- Latência previsível
- Independência de APIs externas

### 9.3 Validação em Múltiplas Camadas

**Motivação**: Garantir integridade dos dados em sistema crítico.

**Camadas**:
1. Pydantic: Validação de tipos
2. JSON Schema: Validação estrutural da LLM
3. Regras de Negócio: Validação semântica
4. Fallback: Valores padrão seguros

---

## 10. Limitações e Trabalhos Futuros

### 10.1 Limitações Atuais

- Dataset de avaliação limitado (20 ordens sintéticas)
- Regras baseadas em conhecimento de um único especialista
- Sem aprendizado contínuo das decisões
- Interface limitada a API REST

### 10.2 Extensões Possíveis

- Integração com sistemas ERP/CMMS
- Interface web para visualização
- Aprendizado de regras a partir de feedback
- Suporte multilíngue
- Modelo de recomendação de peças/procedimentos

---

## Código Completo

O código-fonte completo deste sistema, incluindo todos os módulos, testes, documentação detalhada e exemplos de uso, está disponível no repositório GitHub:

**🔗 [github.com/seu-usuario/sistema-triador-os](https://github.com/crparaizo/sistemaEspecialista_IFSP)**

O repositório inclui:
- Código-fonte completo com documentação inline
- Suite completa de testes unitários
- Dataset sintético para avaliação
- Scripts de demonstração e uso
- Guia de instalação e configuração
- Exemplos de uso da API
- Documentação técnica detalhada

---

## Referências do Código

Este apêndice apresentou uma visão resumida da implementação. Para detalhes específicos sobre:

- **Implementação das regras**: Ver `src/expert/rules.py`
- **Motor de inferência**: Ver `src/expert/engine.py`
- **Pipeline completo**: Ver `src/triage/pipeline.py`
- **Schemas de validação**: Ver `src/models/` e `src/llm/schemas.py`
- **Testes e avaliação**: Ver `tests/` e `src/evaluation/`

---

*Este sistema foi desenvolvido como protótipo para monografia de Pós-Graduação em Controle e Automação no Instituto Federal de São Paulo (IFSP).*
