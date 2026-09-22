"""
Interface Abstrata para Provedores de LLM.

Define o contrato que todos os provedores de LLM devem seguir,
permitindo trocar a implementação sem afetar o resto do sistema.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.extraction import ExtractionResult


class LLMProvider(ABC):
    """
    Interface abstrata para provedores de LLM.
    
    Esta abstração permite que o sistema seja desacoplado da implementação
    específica do provedor de LLM, facilitando:
    - Troca entre Ollama local e APIs externas
    - Troca de modelos sem alterar código
    - Testes com providers mockados
    - Adição de novos provedores no futuro
    """
    
    @abstractmethod
    def extract_information(
        self,
        order_description: str,
        order_id: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extrai informações estruturadas de uma descrição de OS.
        
        Este método é a interface principal da camada conexionista.
        Recebe texto em linguagem natural e retorna dados estruturados.
        
        Args:
            order_description: Descrição da ordem de serviço em linguagem natural
            order_id: Identificador da OS (opcional, para logging)
            
        Returns:
            ExtractionResult: Informações estruturadas extraídas
            
        Raises:
            LLMExtractionError: Se a extração falhar
            LLMValidationError: Se a resposta não puder ser validada
            LLMTimeoutError: Se a chamada exceder o timeout
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se o provedor está disponível.
        
        Returns:
            bool: True se o provedor está acessível e funcionando
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """
        Retorna informações sobre o modelo em uso.
        
        Returns:
            dict: Informações do modelo (nome, versão, etc)
        """
        pass


class LLMExtractionError(Exception):
    """Exceção levantada quando a extração falha."""
    pass


class LLMValidationError(Exception):
    """Exceção levantada quando a validação da resposta falha."""
    pass


class LLMTimeoutError(Exception):
    """Exceção levantada quando a chamada excede o timeout."""
    pass


class LLMConnectionError(Exception):
    """Exceção levantada quando não é possível conectar ao provedor."""
    pass
