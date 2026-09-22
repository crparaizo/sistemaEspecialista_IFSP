"""
Modelo de Resultado da Extração (Camada Conexionista).

Representa a saída estruturada da LLM após processar
a descrição em linguagem natural da ordem de serviço.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ExtractionResult(BaseModel):
    """
    Resultado da extração de informações pela LLM.
    
    IMPORTANTE: Este modelo representa APENAS a interpretação e estruturação
    de dados pela camada conexionista. NÃO contém decisões finais.
    
    Attributes:
        equipamento: Equipamento identificado na OS
        componente: Componente específico afetado
        sintomas: Lista de sintomas/problemas observados
        tipo_manutencao: Tipo de manutenção inferido (corretiva, preventiva, etc)
        termos_tecnicos: Termos técnicos relevantes identificados
        especialidade_sugerida: Sugestão de especialidade (NÃO é decisão final)
        confianca: Nível de confiança da extração (0.0 a 1.0)
        observacoes: Observações adicionais relevantes
    """
    
    equipamento: Optional[str] = Field(
        None,
        description="Equipamento ou máquina identificado",
        examples=["motor da esteira 03", "bomba centrífuga B-102"]
    )
    
    componente: Optional[str] = Field(
        None,
        description="Componente específico do equipamento",
        examples=["motor", "rolamento", "válvula de controle"]
    )
    
    sintomas: List[str] = Field(
        default_factory=list,
        description="Lista de sintomas ou problemas observados",
        examples=[["vibração excessiva", "ruído anormal"]]
    )
    
    tipo_manutencao: Optional[str] = Field(
        None,
        description="Tipo de manutenção inferido",
        examples=["corretiva", "preventiva", "preditiva"]
    )
    
    termos_tecnicos: List[str] = Field(
        default_factory=list,
        description="Termos técnicos relevantes identificados",
        examples=[["motor", "vibração", "rolamento", "lubrificação"]]
    )
    
    especialidade_sugerida: Optional[str] = Field(
        None,
        description="Sugestão de especialidade (NÃO é decisão final do sistema)",
        examples=["eletromecânica", "elétrica", "instrumentação"]
    )
    
    confianca: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Nível de confiança da extração (0.0 a 1.0)"
    )
    
    observacoes: Optional[str] = Field(
        None,
        description="Observações ou informações adicionais relevantes"
    )
    
    @field_validator('sintomas', 'termos_tecnicos')
    @classmethod
    def clean_empty_strings(cls, v: List[str]) -> List[str]:
        """Remove strings vazias das listas."""
        return [item.strip() for item in v if item and item.strip()]
    
    class Config:
        json_schema_extra = {
            "example": {
                "equipamento": "motor da esteira 03",
                "componente": "motor elétrico",
                "sintomas": ["vibração excessiva", "ruído durante operação"],
                "tipo_manutencao": "corretiva",
                "termos_tecnicos": ["motor", "vibração", "ruído", "esteira"],
                "especialidade_sugerida": "eletromecânica",
                "confianca": 0.85,
                "observacoes": "Sintomas indicam possível problema em rolamento"
            }
        }
