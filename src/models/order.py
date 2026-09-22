"""
Modelo de Ordem de Serviço (OS).

Representa a entrada bruta do sistema - uma ordem de serviço
de manutenção industrial em linguagem natural.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ServiceOrder(BaseModel):
    """
    Ordem de Serviço de Manutenção Industrial.
    
    Attributes:
        order_id: Identificador único da OS
        description: Descrição em linguagem natural do problema
        created_at: Timestamp de criação
        requester: Solicitante da OS (opcional)
        location: Localização/setor (opcional)
    """
    
    order_id: str = Field(
        ...,
        description="Identificador único da ordem de serviço",
        examples=["OS-001", "OS-2024-123"]
    )
    
    description: str = Field(
        ...,
        min_length=10,
        description="Descrição do problema em linguagem natural",
        examples=["Motor da esteira 03 apresenta vibração excessiva"]
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Data e hora de criação da OS"
    )
    
    requester: Optional[str] = Field(
        None,
        description="Nome ou identificação do solicitante",
        examples=["João Silva", "Operador Turno A"]
    )
    
    location: Optional[str] = Field(
        None,
        description="Localização ou setor da instalação",
        examples=["Linha de Produção 3", "Setor de Embalagem"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "OS-001",
                "description": "Motor da esteira 03 apresenta vibração excessiva e ruído durante operação",
                "requester": "Supervisor Produção",
                "location": "Linha 3 - Setor A"
            }
        }
