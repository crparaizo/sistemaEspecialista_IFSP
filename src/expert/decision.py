"""
Estrutura de Decisão do Sistema Especialista.

Define como as decisões são representadas e justificadas.
"""

from typing import List
from pydantic import BaseModel, Field


class ExpertDecision(BaseModel):
    """
    Decisão produzida pelo sistema especialista.
    
    Attributes:
        classificacao: Classificação da OS
        criticidade: Nível de criticidade
        urgencia: Nível de urgência  
        especialidade: Especialidade técnica responsável
        roteamento: Equipe ou pessoa para roteamento
        prioridade: Prioridade numérica (1=máxima, 5=mínima)
        regras_aplicadas: IDs das regras que foram aplicadas
        justificativa: Explicação textual da decisão
    """
    
    classificacao: str = Field(
        ...,
        description="Classificação da ordem de serviço"
    )
    
    criticidade: str = Field(
        ...,
        description="Nível de criticidade: Baixa, Média, Alta, Crítica"
    )
    
    urgencia: str = Field(
        ...,
        description="Nível de urgência: Baixa, Normal, Alta, Emergencial"
    )
    
    especialidade: str = Field(
        ...,
        description="Especialidade técnica necessária"
    )
    
    roteamento: str = Field(
        ...,
        description="Equipe ou responsável para roteamento"
    )
    
    prioridade: int = Field(
        ...,
        ge=1,
        le=5,
        description="Prioridade numérica (1=máxima, 5=mínima)"
    )
    
    regras_aplicadas: List[str] = Field(
        default_factory=list,
        description="IDs das regras aplicadas"
    )
    
    justificativa: str = Field(
        default="",
        description="Justificativa textual da decisão"
    )
    
    def add_rule(self, rule_id: str, description: str = "") -> None:
        """
        Adiciona uma regra aplicada à decisão.
        
        Args:
            rule_id: ID da regra
            description: Descrição do motivo (opcional)
        """
        if rule_id not in self.regras_aplicadas:
            self.regras_aplicadas.append(rule_id)
        
        if description and description not in self.justificativa:
            if self.justificativa:
                self.justificativa += "; "
            self.justificativa += description
    
    def to_result_decision(self):
        """
        Converte para o formato Decision usado em TriageResult.
        
        Returns:
            Decision: Decisão no formato do modelo de resultado
        """
        from ..models.result import Decision
        
        return Decision(
            classificacao=self.classificacao,
            criticidade=self.criticidade,
            urgencia=self.urgencia,
            especialidade=self.especialidade,
            roteamento=self.roteamento,
            prioridade=self.prioridade
        )
