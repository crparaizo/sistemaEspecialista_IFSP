"""
Testes para pipeline de triagem.
"""

import pytest
from unittest.mock import Mock, patch

from src.models.order import ServiceOrder
from src.models.extraction import ExtractionResult
from src.triage.pipeline import TriagePipeline, TriagePipelineError
from src.llm.provider import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock do provedor LLM para testes."""
    
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.calls = []
    
    def extract_information(self, order_description, order_id=None):
        """Simula extração."""
        self.calls.append({
            "order_description": order_description,
            "order_id": order_id
        })
        
        if self.should_fail:
            from src.llm.provider import LLMExtractionError
            raise LLMExtractionError("Simulated failure")
        
        return ExtractionResult(
            equipamento="motor teste",
            sintomas=["vibração"],
            termos_tecnicos=["motor", "vibração"],
            tipo_manutencao="corretiva"
        )
    
    def is_available(self):
        """Simula disponibilidade."""
        return not self.should_fail
    
    def get_model_info(self):
        """Retorna info simulada."""
        return {
            "provider": "mock",
            "model": "test-model"
        }


class TestTriagePipeline:
    """Testes para TriagePipeline."""
    
    def test_process_order_success(self):
        """Testa processamento bem-sucedido de ordem."""
        mock_provider = MockLLMProvider()
        pipeline = TriagePipeline(llm_provider=mock_provider)
        
        order = ServiceOrder(
            order_id="OS-TEST-001",
            description="Motor da esteira apresenta vibração excessiva"
        )
        
        result = pipeline.process(order)
        
        assert result.order_id == "OS-TEST-001"
        assert result.extraction is not None
        assert result.decision is not None
        assert len(result.rules_applied) > 0
        assert result.justificativa != ""
        assert "llm_inference_time_ms" in result.metadata
        assert "expert_inference_time_ms" in result.metadata
    
    def test_process_handles_llm_failure(self):
        """Testa que pipeline continua mesmo com falha da LLM."""
        mock_provider = MockLLMProvider(should_fail=True)
        pipeline = TriagePipeline(llm_provider=mock_provider)
        
        order = ServiceOrder(
            order_id="OS-TEST-002",
            description="Problema no equipamento"
        )
        
        # Pipeline deve continuar mesmo com falha da LLM
        result = pipeline.process(order)
        
        assert result.order_id == "OS-TEST-002"
        assert result.metadata["extraction_success"] is False
        assert "extraction_error" in result.metadata
        # Sistema especialista deve usar fallback
        assert result.decision is not None
    
    def test_process_batch(self):
        """Testa processamento em lote."""
        mock_provider = MockLLMProvider()
        pipeline = TriagePipeline(llm_provider=mock_provider)
        
        orders = [
            ServiceOrder(
                order_id=f"OS-BATCH-{i:03d}",
                description=f"Problema {i}"
            )
            for i in range(3)
        ]
        
        results = pipeline.process_batch(orders)
        
        assert len(results) == 3
        assert all(r.order_id.startswith("OS-BATCH") for r in results)
    
    def test_validate_provider(self):
        """Testa validação de provedor."""
        mock_provider = MockLLMProvider()
        pipeline = TriagePipeline(llm_provider=mock_provider)
        
        validation = pipeline.validate_provider()
        
        assert "available" in validation
        assert "provider" in validation
        assert "model" in validation
        assert validation["available"] is True
    
    def test_explain_decision(self):
        """Testa geração de explicação."""
        mock_provider = MockLLMProvider()
        pipeline = TriagePipeline(llm_provider=mock_provider)
        
        order = ServiceOrder(
            order_id="OS-EXPLAIN-001",
            description="Motor com vibração"
        )
        
        explanation = pipeline.explain_decision(order)
        
        assert "facts_summary" in explanation
        assert "derived_facts" in explanation
        assert "rules_applied" in explanation
        assert "decision" in explanation
        assert "triage_result" in explanation
    
    def test_get_pipeline_info(self):
        """Testa obtenção de informações do pipeline."""
        mock_provider = MockLLMProvider()
        pipeline = TriagePipeline(llm_provider=mock_provider)
        
        info = pipeline.get_pipeline_info()
        
        assert "version" in info
        assert "architecture" in info
        assert info["architecture"] == "hybrid_neurosymbolic"
        assert "layers" in info
        assert "connectionist" in info["layers"]
        assert "symbolic" in info["layers"]
