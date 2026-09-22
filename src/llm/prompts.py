"""
Templates de Prompts para a LLM.

Define os prompts utilizados para extrair informações estruturadas
das ordens de serviço. Os prompts são versionados e documentados.
"""

from typing import Optional
from .schemas import ExtractionSchema


# Versão atual do prompt
PROMPT_VERSION = "1.0"


def get_extraction_prompt(order_description: str) -> str:
    """
    Gera o prompt para extração de informações de uma OS.
    
    Este prompt é projetado para:
    1. Instruir claramente a LLM sobre sua função
    2. Enfatizar que ela NÃO deve tomar decisões finais
    3. Forçar saída estruturada em JSON
    4. Evitar alucinações
    
    Args:
        order_description: Descrição da ordem de serviço
        
    Returns:
        str: Prompt completo formatado
    """
    
    schema_description = ExtractionSchema.get_schema_description()
    
    prompt = f"""Você é um assistente especializado em interpretar ordens de serviço (OS) de manutenção industrial.

Sua função é APENAS extrair e estruturar informações presentes no texto, NÃO tomar decisões finais sobre classificação, criticidade, urgência ou roteamento.

INSTRUÇÕES:

1. Analise cuidadosamente a descrição da ordem de serviço
2. Extraia as seguintes informações quando presentes:
   - Equipamento ou máquina mencionado
   - Componente específico afetado
   - Sintomas ou problemas observados
   - Tipo de manutenção (corretiva, preventiva, preditiva)
   - Termos técnicos relevantes
   - Possível especialidade técnica envolvida (apenas sugestão)

3. IMPORTANTE:
   - Use null para informações não presentes no texto
   - NÃO invente ou assuma informações
   - NÃO tome decisões sobre criticidade, urgência ou prioridade
   - Preserve termos técnicos originais quando possível
   - Sua análise será usada por um sistema especialista para decisões finais

{schema_description}

ORDEM DE SERVIÇO:
{order_description}

Retorne APENAS o JSON estruturado, sem texto adicional antes ou depois."""

    return prompt


def get_validation_prompt(
    order_description: str,
    extraction_result: dict
) -> str:
    """
    Gera um prompt para validar/revisar uma extração.
    
    Útil para implementar verificação em duas etapas (futura).
    
    Args:
        order_description: Descrição original da OS
        extraction_result: Resultado da extração inicial
        
    Returns:
        str: Prompt de validação
    """
    
    prompt = f"""Revise a extração de informações abaixo e confirme se está correta.

ORDEM DE SERVIÇO ORIGINAL:
{order_description}

EXTRAÇÃO REALIZADA:
{extraction_result}

A extração está correta? Se houver algum erro ou informação faltante, corrija-a.

Retorne o JSON corrigido ou o mesmo JSON se estiver correto."""

    return prompt


def get_few_shot_examples() -> list[dict]:
    """
    Retorna exemplos few-shot para melhorar a qualidade da extração.
    
    Estes exemplos podem ser incluídos no prompt para modelos que
    se beneficiam de exemplos (opcional).
    
    Returns:
        list: Lista de exemplos (input, output)
    """
    
    examples = [
        {
            "input": "Motor da esteira 03 apresenta vibração excessiva e ruído durante operação",
            "output": {
                "equipamento": "esteira 03",
                "componente": "motor",
                "sintomas": ["vibração excessiva", "ruído durante operação"],
                "tipo_manutencao": "corretiva",
                "termos_tecnicos": ["motor", "esteira", "vibração", "ruído"],
                "especialidade_sugerida": "eletromecânica",
                "confianca": 0.9,
                "observacoes": "Sintomas indicam possível problema em rolamento ou desbalanceamento"
            }
        },
        {
            "input": "Realizar troca do óleo do compressor C-05 conforme programação trimestral",
            "output": {
                "equipamento": "compressor C-05",
                "componente": "sistema de lubrificação",
                "sintomas": [],
                "tipo_manutencao": "preventiva",
                "termos_tecnicos": ["compressor", "óleo", "lubrificação"],
                "especialidade_sugerida": "mecânica",
                "confianca": 0.95,
                "observacoes": "Manutenção preventiva programada"
            }
        },
        {
            "input": "Sensor de temperatura ST-102 indicando valores inconsistentes. Leituras variando entre -10°C e 150°C sem padrão",
            "output": {
                "equipamento": "sensor ST-102",
                "componente": "sensor de temperatura",
                "sintomas": ["valores inconsistentes", "leituras erráticas"],
                "tipo_manutencao": "corretiva",
                "termos_tecnicos": ["sensor", "temperatura", "leitura", "calibração"],
                "especialidade_sugerida": "instrumentação",
                "confianca": 0.85,
                "observacoes": "Possível falha no sensor ou problemas de calibração"
            }
        },
        {
            "input": "Disjuntor DJ-23 desarma frequentemente sob carga nominal",
            "output": {
                "equipamento": "disjuntor DJ-23",
                "componente": "disjuntor",
                "sintomas": ["desarme frequente", "desarme sob carga nominal"],
                "tipo_manutencao": "corretiva",
                "termos_tecnicos": ["disjuntor", "desarme", "carga", "proteção elétrica"],
                "especialidade_sugerida": "elétrica",
                "confianca": 0.9,
                "observacoes": "Possível sobredimensionamento da proteção ou problema de contato"
            }
        }
    ]
    
    return examples


def format_few_shot_prompt(order_description: str) -> str:
    """
    Gera um prompt com exemplos few-shot.
    
    Args:
        order_description: Descrição da OS
        
    Returns:
        str: Prompt com exemplos
    """
    
    examples = get_few_shot_examples()
    schema_description = ExtractionSchema.get_schema_description()
    
    examples_text = "\n\n".join([
        f"EXEMPLO {i+1}:\nEntrada: {ex['input']}\nSaída: {ex['output']}"
        for i, ex in enumerate(examples[:2])  # Usa apenas 2 exemplos para não inflar o prompt
    ])
    
    prompt = f"""Você é um assistente especializado em interpretar ordens de serviço (OS) de manutenção industrial.

Sua função é APENAS extrair e estruturar informações, NÃO tomar decisões finais.

{schema_description}

EXEMPLOS:

{examples_text}

Agora analise a seguinte ordem de serviço:

ORDEM DE SERVIÇO:
{order_description}

Retorne APENAS o JSON estruturado."""

    return prompt


# Metadados do sistema de prompts
PROMPT_METADATA = {
    "version": PROMPT_VERSION,
    "description": "Sistema de prompts para extração de informações de OS",
    "functions": [
        "get_extraction_prompt",
        "get_validation_prompt",
        "get_few_shot_examples",
        "format_few_shot_prompt"
    ]
}
