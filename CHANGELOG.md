# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2026-09-21

### Implementação Inicial

#### ✨ Funcionalidades

- **Arquitetura Neurossimbólica**
  - Camada Conexionista: Integração com LLM via Ollama
  - Camada Simbólica: Sistema Especialista com 14 regras
  - Pipeline completo de triagem

- **Extração de Informações (LLM)**
  - Suporte a Ollama (local)
  - Structured output com JSON schema
  - Validação com Pydantic
  - Tratamento robusto de erros
  - Abstração para futuros provedores (API externa)

- **Sistema Especialista**
  - Motor de inferência forward chaining
  - 14 regras iniciais (criticidade, classificação, urgência)
  - Regra de fallback para casos não cobertos
  - Explicabilidade completa (rastreamento de regras)
  - Justificativas automáticas

- **API REST**
  - Endpoint `/triage` para processamento individual
  - Endpoint `/triage/batch` para lote
  - Endpoint `/triage/explain` para debugging
  - Endpoint `/health` para status
  - Endpoint `/info` para informações do pipeline
  - Documentação OpenAPI automática

- **Sistema de Avaliação**
  - Gerenciador de datasets JSON
  - Cálculo de acurácia por campo
  - Precisão, Recall, F1-Score
  - Matriz de confusão
  - Relatórios detalhados em JSON
  - Comparação expected vs predicted

#### 📊 Dataset

- Dataset sintético com 20 ordens de serviço
- Cobertura: Elétrica, Mecânica, Instrumentação, Automação
- Criticidades variadas: Baixa, Média, Alta, Crítica
- Linguagem imperfeita com abreviações e termos técnicos

#### 🛠️ Infraestrutura

- **Logging Estruturado**
  - Formatters JSON e texto
  - Logs de eventos específicos (triagem, LLM, inferência)
  - Context manager para adicionar contexto
  - Suporte a arquivo e console

- **Configuração**
  - Pydantic Settings
  - Variáveis de ambiente via .env
  - Configurações separadas para LLM, API, logging

- **Testes**
  - Testes unitários para modelos
  - Testes do sistema especialista
  - Testes do pipeline
  - Mock de LLM para testes isolados
  - Fixtures reutilizáveis

#### 🔧 Scripts Auxiliares

- `run_api.py`: Inicia servidor FastAPI
- `run_evaluation.py`: Executa avaliação completa
- `test_single_order.py`: Testa ordem única (com modo explain)
- `generate_dataset.py`: Gera datasets sintéticos

#### 📚 Documentação

- README.md completo com exemplos
- Documentação inline em todos os módulos
- Docstrings em funções e classes
- Exemplos de uso práticos
- Guia de instalação e configuração

#### 🏗️ Arquitetura

```
src/
├── api/          # FastAPI REST endpoints
├── config/       # Configurações e settings
├── evaluation/   # Sistema de avaliação e métricas
├── expert/       # Sistema Especialista (regras, fatos, engine)
├── llm/          # Provedores LLM e prompts
├── models/       # Modelos Pydantic
├── triage/       # Pipeline principal
└── utils/        # Logging e utilitários
```

#### 🔬 Princípios de Design

- **Separação de responsabilidades**: LLM interpreta, Expert System decide
- **Explicabilidade**: Todas as decisões são rastreáveis
- **Modularidade**: Componentes desacoplados e testáveis
- **Extensibilidade**: Fácil adicionar regras e provedores
- **Observabilidade**: Logs estruturados e métricas

### 🎓 Contexto Acadêmico

Protótipo desenvolvido para monografia de **Pós-Graduação em Controle e Automação** no **IFSP** (Instituto Federal de São Paulo).

**Título:** "Triador de ordens de serviço de manutenção industrial: uma arquitetura híbrida neurossimbólica para classificação, enriquecimento e roteamento de chamados técnicos de automação."

### 📝 Notas

- Sistema implementado mas aguardando validação com Ollama real
- Métricas experimentais pendentes de coleta
- Dataset sintético inicial (20 OS)
- Pronto para demonstração e testes

### 🔮 Próximos Passos

Ver [PENDENCIAS.md](PENDENCIAS.md) para lista completa de melhorias futuras e validações pendentes.

---

## Formato

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## Tipos de Mudanças

- `✨ Funcionalidades` - para novas funcionalidades
- `🔧 Correções` - para correções de bugs
- `📚 Documentação` - para mudanças na documentação
- `🎨 Refatoração` - para refatorações de código
- `⚡ Performance` - para melhorias de performance
- `🧪 Testes` - para adições ou mudanças em testes
- `🔒 Segurança` - para correções de segurança
- `⚠️ Deprecado` - para funcionalidades que serão removidas
- `🗑️ Removido` - para funcionalidades removidas
