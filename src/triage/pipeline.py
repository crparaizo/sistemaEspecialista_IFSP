"""
Pipeline de Triagem de Ordens de Serviço.

Orquestra o fluxo completo:
1. Extração de informações (LLM)
2. Validação
3. Transformação em fatos
4. Inferência (Sistema Especialista)
5. Montagem do resultado final
"""

import time
from typing import Optional, Dict, Any

from ..models.order import ServiceOrder
from ..models.extraction import ExtractionResult
from ..models.result import TriageResult
from ..llm.provider import (
    LLMProvider,
    LLMExtractionError,
    LLMValidationError,
    LLMTimeoutError,
    LLMConnectionError
)
from ..llm.ollama_provider import OllamaProvider
from ..expert.facts import Facts
from ..expert.engine import InferenceEngine
from ..config import get_settings


class TriagePipeline:
    """
    Pipeline completo de triagem de OS.
    
    Implementa a arquitetura neurossimbólica:
    - Camada Conexionista: LLM para extração
    - Camada Simbólica: Sistema Especialista para decisão
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        inference_engine: Optional[InferenceEngine] = None
    ):
        """
        Inicializa o pipeline.
        
        Args:
            llm_provider: Provedor LLM (usa Ollama se None)
            inference_engine: Motor de inferência (cria novo se None)
        """
        self.settings = get_settings()
        self.llm_provider = llm_provider or self._create_llm_provider()
        self.inference_engine = inference_engine or InferenceEngine()
    
    def _create_llm_provider(self) -> LLMProvider:
        """
        Cria o provedor LLM baseado nas configurações.
        
        Returns:
            LLMProvider: Provedor configurado
        """
        provider_type = self.settings.llm_provider.lower()
        
        if provider_type == "ollama":
            return OllamaProvider()
        elif provider_type == "api":
            # Futura implementação
            raise NotImplementedError("Provedor API ainda não implementado")
        else:
            raise ValueError(f"Provedor desconhecido: {provider_type}")
    
    def process(self, order: ServiceOrder) -> TriageResult:
        """
        Processa uma ordem de serviço completa.
        
        Este é o método principal do pipeline que:
        1. Extrai informações com LLM
        2. Transforma em fatos
        3. Aplica sistema especialista
        4. Retorna resultado completo
        
        Args:
            order: Ordem de serviço a processar
            
        Returns:
            TriageResult: Resultado completo da triagem
            
        Raises:
            TriagePipelineError: Se o processamento falhar
        """
        start_time = time.time()
        metadata: Dict[str, Any] = {
            "pipeline_version": "1.0",
            "llm_model": self.settings.llm_model,
            "llm_provider": self.settings.llm_provider
        }
        
        try:
            # ============================================================
            # ETAPA 1: EXTRAÇÃO (Camada Conexionista)
            # ============================================================
            
            extraction_start = time.time()
            
            try:
                extraction = self.llm_provider.extract_information(
                    order_description=order.description,
                    order_id=order.order_id
                )
                
                extraction_time = int((time.time() - extraction_start) * 1000)
                metadata["llm_inference_time_ms"] = extraction_time
                metadata["extraction_success"] = True
                
            except (LLMExtractionError, LLMValidationError, LLMTimeoutError) as e:
                # Se a extração falhar, usa valores vazios mas continua
                extraction = ExtractionResult()
                metadata["extraction_success"] = False
                metadata["extraction_error"] = str(e)
                metadata["llm_inference_time_ms"] = int((time.time() - extraction_start) * 1000)
            
            # ============================================================
            # ETAPA 2: TRANSFORMAÇÃO EM FATOS
            # ============================================================
            
            facts = Facts.from_extraction(extraction)
            
            # ============================================================
            # ETAPA 3: INFERÊNCIA (Camada Simbólica)
            # ============================================================
            
            expert_start = time.time()
            
            expert_decision = self.inference_engine.infer(facts)
            
            expert_time = int((time.time() - expert_start) * 1000)
            metadata["expert_inference_time_ms"] = expert_time
            
            # ============================================================
            # ETAPA 4: MONTAGEM DO RESULTADO
            # ============================================================
            
            # Converte decisão do especialista para formato de resultado
            decision = expert_decision.to_result_decision()
            
            # Monta resultado completo
            result = TriageResult(
                order_id=order.order_id,
                extraction=extraction,
                decision=decision,
                rules_applied=expert_decision.regras_aplicadas,
                justificativa=expert_decision.justificativa,
                metadata=metadata
            )
            
            # Adiciona tempo total
            total_time = int((time.time() - start_time) * 1000)
            result.metadata["total_time_ms"] = total_time
            
            return result
            
        except Exception as e:
            # Erro inesperado no pipeline
            raise TriagePipelineError(
                f"Erro ao processar ordem {order.order_id}: {e}"
            ) from e
    
    def process_batch(self, orders: list[ServiceOrder]) -> list[TriageResult]:
        """
        Processa um lote de ordens de serviço.
        
        Args:
            orders: Lista de ordens a processar
            
        Returns:
            list[TriageResult]: Resultados da triagem
        """
        results = []
        
        for order in orders:
            try:
                result = self.process(order)
                results.append(result)
            except TriagePipelineError as e:
                # Em produção, pode-se querer registrar erro mas continuar
                # Por ora, propaga a exceção
                raise
        
        return results
    
    def validate_provider(self) -> Dict[str, Any]:
        """
        Valida se o provedor LLM está disponível.
        
        Returns:
            dict: Status da validação
        """
        is_available = self.llm_provider.is_available()
        model_info = self.llm_provider.get_model_info()
        
        return {
            "available": is_available,
            "provider": self.settings.llm_provider,
            "model": self.settings.llm_model,
            "model_info": model_info
        }
    
    def explain_decision(self, order: ServiceOrder) -> Dict[str, Any]:
        """
        Processa uma OS e retorna explicação detalhada.
        
        Útil para debugging e análise de decisões.
        
        Args:
            order: Ordem de serviço
            
        Returns:
            dict: Explicação detalhada
        """
        # Processa normalmente
        result = self.process(order)
        
        # Reconstrói fatos para explicação
        facts = Facts.from_extraction(result.extraction)
        expert_decision = self.inference_engine.infer(facts)
        
        # Gera explicação
        explanation = self.inference_engine.explain_decision(facts, expert_decision)
        
        # Adiciona resultado completo
        explanation["triage_result"] = {
            "order_id": result.order_id,
            "decision": {
                "classificacao": result.decision.classificacao,
                "criticidade": result.decision.criticidade,
                "urgencia": result.decision.urgencia,
                "especialidade": result.decision.especialidade,
                "roteamento": result.decision.roteamento,
                "prioridade": result.decision.prioridade
            },
            "metadata": result.metadata
        }
        
        return explanation
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o pipeline.
        
        Returns:
            dict: Informações do pipeline
        """
        return {
            "version": "1.0",
            "architecture": "hybrid_neurosymbolic",
            "layers": {
                "connectionist": {
                    "provider": self.settings.llm_provider,
                    "model": self.settings.llm_model,
                    "function": "information_extraction"
                },
                "symbolic": {
                    "type": "rule_based_expert_system",
                    "inference": "forward_chaining",
                    "num_rules": len(self.inference_engine.rule_base.rules),
                    "function": "decision_making"
                }
            },
            "settings": {
                "llm_temperature": self.settings.llm_temperature,
                "llm_timeout": self.settings.llm_timeout,
                "expert_mode": self.settings.expert_mode
            }
        }


class TriagePipelineError(Exception):
    """Exceção levantada quando o pipeline falha."""
    pass
