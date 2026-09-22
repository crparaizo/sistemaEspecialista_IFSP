"""
Implementação do Provedor LLM usando Ollama.

Ollama permite executar modelos de linguagem localmente,
garantindo privacidade e controle sobre os dados.
"""

import json
import time
from typing import Optional, Dict, Any

import requests
from pydantic import ValidationError

from .provider import (
    LLMProvider,
    LLMExtractionError,
    LLMValidationError,
    LLMTimeoutError,
    LLMConnectionError
)
from .prompts import get_extraction_prompt
from ..models.extraction import ExtractionResult
from ..config import get_settings


class OllamaProvider(LLMProvider):
    """
    Provedor de LLM usando Ollama.
    
    Integra com o Ollama para executar modelos localmente,
    com suporte a structured outputs via JSON schema.
    """
    
    def __init__(self):
        """Inicializa o provedor Ollama com configurações do sistema."""
        self.settings = get_settings()
        self.base_url = self.settings.llm_base_url
        self.model = self.settings.llm_model
        self.timeout = self.settings.llm_timeout
        self.temperature = self.settings.llm_temperature
        
    def extract_information(
        self,
        order_description: str,
        order_id: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extrai informações estruturadas usando Ollama.
        
        Args:
            order_description: Descrição da OS
            order_id: ID da OS (para logging)
            
        Returns:
            ExtractionResult: Dados estruturados extraídos
        """
        start_time = time.time()
        
        try:
            # Monta o prompt
            prompt = get_extraction_prompt(order_description)
            
            # Prepara a requisição para Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Força saída JSON
                "options": {
                    "temperature": self.temperature,
                    "num_predict": 1024  # Limite de tokens na resposta
                }
            }
            
            # Chama a API do Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extrai a resposta
            raw_response = result.get("response", "")
            
            if not raw_response:
                raise LLMExtractionError("Resposta vazia da LLM")
            
            # Tenta parsear o JSON
            try:
                parsed_json = json.loads(raw_response)
            except json.JSONDecodeError as e:
                raise LLMValidationError(f"Resposta não é JSON válido: {e}")
            
            # Valida com Pydantic
            try:
                extraction_result = ExtractionResult(**parsed_json)
            except ValidationError as e:
                raise LLMValidationError(f"Resposta não corresponde ao schema: {e}")
            
            # Adiciona metadata de tempo
            inference_time = int((time.time() - start_time) * 1000)  # ms
            
            return extraction_result
            
        except requests.exceptions.Timeout:
            raise LLMTimeoutError(
                f"Timeout ao chamar Ollama após {self.timeout}s"
            )
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(
                f"Não foi possível conectar ao Ollama em {self.base_url}: {e}"
            )
        except requests.exceptions.HTTPError as e:
            raise LLMExtractionError(
                f"Erro HTTP ao chamar Ollama: {e}"
            )
    
    def is_available(self) -> bool:
        """
        Verifica se o Ollama está disponível e acessível.
        
        Returns:
            bool: True se disponível
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo em uso.
        
        Returns:
            dict: Informações do modelo
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "provider": "ollama",
                    "model": self.model,
                    "base_url": self.base_url,
                    "details": data
                }
        except Exception:
            pass
        
        # Fallback se não conseguir obter detalhes
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url
        }
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Tenta extrair JSON de uma resposta que pode conter texto extra.
        
        Args:
            text: Texto que pode conter JSON
            
        Returns:
            str: JSON extraído
        """
        # Procura por blocos JSON (entre chaves)
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        
        return text
