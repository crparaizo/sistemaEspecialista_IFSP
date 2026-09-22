"""
Modelos de Resultado Final da Triagem.

Combina os resultados da camada conexionista (LLM) e
da camada simbólica (Sistema Especialista).
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .extraction import ExtractionResult


class Decision(BaseModel):
    """
    Decisão do Sistema Especialista.
    
    Representa a decisão DETERMINÍSTICA produzida pela camada simbólica
    baseada em regras explícitas.
    
    Attributes:
        classificacao: Classificação da OS
        criticidade: Nível de criticidade
        urgencia: Nível de urgência
        especialidade: Especialidade técnica responsável
        roteamento: Equipe ou pessoa para quem rotear
        prioridade: Prioridade numérica (1=máxima)
    """
    
    classificacao: str = Field(
        ...,
        description="Classificação da ordem de serviço",
        examples=["Elétrica", "Mecânica", "Instrumentação"]
    )
    
    criticidade: str = Field(
        ...,
        description="Nível de criticidade",
        examples=["Baixa", "Média", "Alta", "Crítica"]
    )
    
    urgencia: str = Field(
        ...,
        description="Nível de urgência",
        examples=["Baixa", "Normal", "Alta", "Emergencial"]
    )
    
    especialidade: str = Field(
        ...,
        description="Especialidade técnica necessária",
        examples=["Eletromecânica", "Elétrica", "Mecânica", "Instrumentação"]
    )
    
    roteamento: str = Field(
        ...,
        description="Equipe ou responsável para roteamento",
        examples=["Equipe Mecânica A", "Eletricista Especializado", "Engenharia"]
    )
    
    prioridade: int = Field(
        ...,
        ge=1,
        le=5,
        description="Prioridade numérica (1=máxima, 5=mínima)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "classificacao": "Mecânica",
                "criticidade": "Alta",
                "urgencia": "Alta",
                "especialidade": "Eletromecânica",
                "roteamento": "Equipe Mecânica A",
                "prioridade": 2
            }
        }


class TriageResult(BaseModel):
    """
    Resultado completo da triagem.
    
    Combina informações das duas camadas:
    - Camada Conexionista: extração de informações pela LLM
    - Camada Simbólica: decisão do sistema especialista
    
    Attributes:
        order_id: Identificador da OS
        extraction: Resultado da extração (camada conexionista)
        decision: Decisão final (camada simbólica)
        rules_applied: Lista de IDs das regras aplicadas
        justificativa: Justificativa textual da decisão
        metadata: Metadados do processamento
        timestamp: Timestamp do processamento
    """
    
    order_id: str = Field(
        ...,
        description="Identificador da ordem de serviço"
    )
    
    extraction: ExtractionResult = Field(
        ...,
        description="Resultado da extração pela camada conexionista (LLM)"
    )
    
    decision: Decision = Field(
        ...,
        description="Decisão da camada simbólica (Sistema Especialista)"
    )
    
    rules_applied: List[str] = Field(
        ...,
        description="Lista de IDs das regras aplicadas pelo sistema especialista",
        examples=[["REGRA_001", "REGRA_005"]]
    )
    
    justificativa: str = Field(
        ...,
        description="Justificativa textual baseada nas regras aplicadas"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados do processamento (modelo LLM, tempos, etc)"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp do processamento"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "OS-001",
                "extraction": {
                    "equipamento": "motor da esteira 03",
                    "componente": "motor",
                    "sintomas": ["vibração excessiva", "ruído"],
                    "tipo_manutencao": "corretiva",
                    "termos_tecnicos": ["motor", "vibração"],
                    "especialidade_sugerida": "eletromecânica",
                    "confianca": 0.9
                },
                "decision": {
                    "classificacao": "Mecânica",
                    "criticidade": "Alta",
                    "urgencia": "Alta",
                    "especialidade": "Eletromecânica",
                    "roteamento": "Equipe Mecânica A",
                    "prioridade": 2
                },
                "rules_applied": ["REGRA_001", "REGRA_003"],
                "justificativa": "Alta criticidade devido a sintomas de vibração em motor",
                "metadata": {
                    "llm_model": "qwen2.5:7b",
                    "llm_inference_time_ms": 234,
                    "expert_inference_time_ms": 12
                }
            }
        }
