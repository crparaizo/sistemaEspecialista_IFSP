"""
Testes para modelos de dados.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.order import ServiceOrder
from src.models.extraction import ExtractionResult
from src.models.result import Decision, TriageResult


class TestServiceOrder:
    """Testes para ServiceOrder."""
    
    def test_create_valid_order(self):
        """Testa criação de ordem válida."""
        order = ServiceOrder(
            order_id="OS-001",
            description="Motor apresenta vibração excessiva"
        )
        
        assert order.order_id == "OS-001"
        assert order.description == "Motor apresenta vibração excessiva"
        assert isinstance(order.created_at, datetime)
    
    def test_order_with_optional_fields(self):
        """Testa ordem com campos opcionais."""
        order = ServiceOrder(
            order_id="OS-002",
            description="Sensor com falha",
            requester="João Silva",
            location="Linha 3"
        )
        
        assert order.requester == "João Silva"
        assert order.location == "Linha 3"
    
    def test_order_description_too_short(self):
        """Testa validação de descrição muito curta."""
        with pytest.raises(ValidationError):
            ServiceOrder(
                order_id="OS-003",
                description="Curto"  # Menos de 10 caracteres
            )


class TestExtractionResult:
    """Testes para ExtractionResult."""
    
    def test_create_empty_extraction(self):
        """Testa criação de extração vazia."""
        extraction = ExtractionResult()
        
        assert extraction.equipamento is None
        assert extraction.sintomas == []
        assert extraction.termos_tecnicos == []
    
    def test_create_full_extraction(self):
        """Testa criação de extração completa."""
        extraction = ExtractionResult(
            equipamento="motor esteira 03",
            componente="motor",
            sintomas=["vibração", "ruído"],
            tipo_manutencao="corretiva",
            termos_tecnicos=["motor", "vibração"],
            especialidade_sugerida="eletromecânica",
            confianca=0.85
        )
        
        assert extraction.equipamento == "motor esteira 03"
        assert len(extraction.sintomas) == 2
        assert extraction.confianca == 0.85
    
    def test_confidence_validation(self):
        """Testa validação de confiança."""
        # Confiança válida
        extraction = ExtractionResult(confianca=0.5)
        assert extraction.confianca == 0.5
        
        # Confiança inválida (>1.0)
        with pytest.raises(ValidationError):
            ExtractionResult(confianca=1.5)
        
        # Confiança inválida (<0.0)
        with pytest.raises(ValidationError):
            ExtractionResult(confianca=-0.1)
    
    def test_clean_empty_strings(self):
        """Testa limpeza de strings vazias em listas."""
        extraction = ExtractionResult(
            sintomas=["vibração", "", "ruído", "  "],
            termos_tecnicos=["motor", "", "  ", "esteira"]
        )
        
        assert "vibração" in extraction.sintomas
        assert "ruído" in extraction.sintomas
        assert "" not in extraction.sintomas
        assert len(extraction.sintomas) == 2


class TestDecision:
    """Testes para Decision."""
    
    def test_create_valid_decision(self):
        """Testa criação de decisão válida."""
        decision = Decision(
            classificacao="Mecânica",
            criticidade="Alta",
            urgencia="Alta",
            especialidade="Eletromecânica",
            roteamento="Equipe Mecânica",
            prioridade=2
        )
        
        assert decision.classificacao == "Mecânica"
        assert decision.prioridade == 2
    
    def test_priority_validation(self):
        """Testa validação de prioridade."""
        # Prioridade válida
        decision = Decision(
            classificacao="Test",
            criticidade="Test",
            urgencia="Test",
            especialidade="Test",
            roteamento="Test",
            prioridade=3
        )
        assert decision.prioridade == 3
        
        # Prioridade inválida (< 1)
        with pytest.raises(ValidationError):
            Decision(
                classificacao="Test",
                criticidade="Test",
                urgencia="Test",
                especialidade="Test",
                roteamento="Test",
                prioridade=0
            )


class TestTriageResult:
    """Testes para TriageResult."""
    
    def test_create_complete_result(self):
        """Testa criação de resultado completo."""
        extraction = ExtractionResult(
            equipamento="motor",
            sintomas=["vibração"]
        )
        
        decision = Decision(
            classificacao="Mecânica",
            criticidade="Alta",
            urgencia="Alta",
            especialidade="Mecânica",
            roteamento="Equipe A",
            prioridade=2
        )
        
        result = TriageResult(
            order_id="OS-001",
            extraction=extraction,
            decision=decision,
            rules_applied=["REGRA_001"],
            justificativa="Alta criticidade por vibração"
        )
        
        assert result.order_id == "OS-001"
        assert len(result.rules_applied) == 1
        assert isinstance(result.timestamp, datetime)
