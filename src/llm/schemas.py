"""
Schemas JSON para structured output da LLM.

Define o schema JSON Schema que será usado para forçar
a LLM a produzir saídas estruturadas e válidas.
"""

from typing import Dict, Any


def get_extraction_json_schema() -> Dict[str, Any]:
    """
    Retorna o JSON Schema para extração de informações.
    
    Este schema é usado para forçar a LLM a produzir
    saídas no formato esperado pelo ExtractionResult.
    
    Returns:
        dict: JSON Schema completo
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "equipamento": {
                "type": ["string", "null"],
                "description": "Nome do equipamento ou máquina identificado na descrição"
            },
            "componente": {
                "type": ["string", "null"],
                "description": "Componente específico do equipamento afetado"
            },
            "sintomas": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de sintomas ou problemas observados"
            },
            "tipo_manutencao": {
                "type": ["string", "null"],
                "description": "Tipo de manutenção inferido: corretiva, preventiva ou preditiva"
            },
            "termos_tecnicos": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Termos técnicos relevantes identificados no texto"
            },
            "especialidade_sugerida": {
                "type": ["string", "null"],
                "description": "Sugestão de especialidade técnica (não é decisão final)"
            },
            "confianca": {
                "type": ["number", "null"],
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Nível de confiança da extração entre 0.0 e 1.0"
            },
            "observacoes": {
                "type": ["string", "null"],
                "description": "Observações ou informações adicionais relevantes"
            }
        },
        "required": ["sintomas", "termos_tecnicos"]
    }


class ExtractionSchema:
    """
    Classe de conveniência para acessar schemas.
    """
    
    @staticmethod
    def get_json_schema() -> Dict[str, Any]:
        """Retorna o JSON Schema para extração."""
        return get_extraction_json_schema()
    
    @staticmethod
    def get_schema_description() -> str:
        """
        Retorna uma descrição textual do schema para incluir no prompt.
        
        Returns:
            str: Descrição do schema esperado
        """
        return """
Você deve retornar um JSON com a seguinte estrutura:

{
  "equipamento": "string ou null - nome do equipamento identificado",
  "componente": "string ou null - componente específico afetado",
  "sintomas": ["array de strings - sintomas observados"],
  "tipo_manutencao": "string ou null - corretiva, preventiva ou preditiva",
  "termos_tecnicos": ["array de strings - termos técnicos relevantes"],
  "especialidade_sugerida": "string ou null - sugestão de especialidade",
  "confianca": 0.0 a 1.0 ou null - seu nível de confiança,
  "observacoes": "string ou null - observações adicionais"
}

IMPORTANTE:
- Use null quando não conseguir identificar uma informação
- Não invente informações que não estão no texto
- sintomas e termos_tecnicos devem ser arrays, mesmo que vazios
- confianca deve estar entre 0.0 e 1.0
""".strip()
