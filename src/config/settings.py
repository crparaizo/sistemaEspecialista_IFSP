"""
Configurações do Sistema.

Utiliza Pydantic Settings para gerenciar configurações
via variáveis de ambiente.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configurações do sistema triador.
    
    Todas as configurações podem ser fornecidas via variáveis de ambiente.
    Exemplo: LLM_MODEL=qwen2.5:7b python main.py
    """
    
    # Configurações da LLM
    llm_provider: str = Field(
        default="ollama",
        description="Provedor de LLM (ollama, api)",
        examples=["ollama", "api"]
    )
    
    llm_model: str = Field(
        default="qwen2.5:7b",
        description="Nome do modelo LLM a ser utilizado",
        examples=["qwen2.5:7b", "llama3.1:8b", "mistral:7b"]
    )
    
    llm_base_url: str = Field(
        default="http://localhost:11434",
        description="URL base do servidor Ollama"
    )
    
    llm_timeout: int = Field(
        default=60,
        description="Timeout para chamadas à LLM (segundos)",
        ge=1
    )
    
    llm_temperature: float = Field(
        default=0.1,
        description="Temperatura para geração da LLM (0.0 = determinístico)",
        ge=0.0,
        le=2.0
    )
    
    # Configurações da API Externa (futura)
    api_key: Optional[str] = Field(
        default=None,
        description="Chave de API para provedor externo (se aplicável)"
    )
    
    api_endpoint: Optional[str] = Field(
        default=None,
        description="Endpoint da API externa (se aplicável)"
    )
    
    # Configurações do Sistema Especialista
    expert_mode: str = Field(
        default="strict",
        description="Modo do sistema especialista (strict, flexible)",
        examples=["strict", "flexible"]
    )
    
    enable_fallback_rules: bool = Field(
        default=True,
        description="Habilitar regras de fallback quando nenhuma regra específica se aplica"
    )
    
    # Configurações de Logging
    log_level: str = Field(
        default="INFO",
        description="Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_format: str = Field(
        default="json",
        description="Formato de log (json, text)",
        examples=["json", "text"]
    )
    
    log_file: Optional[str] = Field(
        default=None,
        description="Caminho para arquivo de log (None = apenas console)"
    )
    
    # Configurações da API REST
    api_host: str = Field(
        default="0.0.0.0",
        description="Host da API REST"
    )
    
    api_port: int = Field(
        default=8000,
        description="Porta da API REST",
        ge=1,
        le=65535
    )
    
    api_reload: bool = Field(
        default=False,
        description="Habilitar hot-reload no desenvolvimento"
    )
    
    # Configurações de Avaliação
    evaluation_output_dir: str = Field(
        default="data/evaluation_results",
        description="Diretório para salvar resultados de avaliação"
    )
    
    # Configurações Gerais
    debug: bool = Field(
        default=False,
        description="Modo debug (logs mais verbosos)"
    )
    
    max_retries: int = Field(
        default=3,
        description="Número máximo de tentativas para chamadas que falharem",
        ge=1,
        le=10
    )
    
    # Configuração para carregar do .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Singleton para acesso global às configurações
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Retorna a instância singleton das configurações.
    
    Returns:
        Settings: Configurações do sistema
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """
    Reseta o singleton de configurações.
    
    Útil principalmente para testes.
    """
    global _settings
    _settings = None
