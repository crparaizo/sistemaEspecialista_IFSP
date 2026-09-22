"""
Sistema de Logging Estruturado.

Fornece logging configurável com suporte a JSON estruturado
para facilitar observabilidade e análise.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from ..config import get_settings


class StructuredFormatter(logging.Formatter):
    """
    Formatter para logs estruturados em JSON.
    
    Converte LogRecords em JSON estruturado para facilitar
    parsing e análise por ferramentas de observabilidade.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o log record como JSON.
        
        Args:
            record: Log record a formatar
            
        Returns:
            str: Log formatado como JSON
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adiciona informações extras se disponíveis
        if hasattr(record, "order_id"):
            log_data["order_id"] = record.order_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        # Adiciona exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """
    Formatter para logs em texto legível.
    
    Formato mais amigável para desenvolvimento e debugging.
    """
    
    def __init__(self):
        """Inicializa o formatter."""
        fmt = "[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s"
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configura o sistema de logging.
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato (json, text)
        log_file: Caminho para arquivo de log (None = apenas console)
    """
    settings = get_settings()
    
    # Usa configurações passadas ou defaults do settings
    level = log_level or settings.log_level
    format_type = log_format or settings.log_format
    file_path = log_file or settings.log_file
    
    # Converte string de nível para constante
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Limpa handlers existentes
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(numeric_level)
    
    # Escolhe formatter
    if format_type.lower() == "json":
        formatter = StructuredFormatter()
    else:
        formatter = TextFormatter()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if file_path:
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager para adicionar contexto aos logs.
    
    Permite adicionar informações extras a todos os logs
    dentro de um bloco de código.
    
    Example:
        with LogContext(order_id="OS-001"):
            logger.info("Processando ordem")
    """
    
    def __init__(self, **kwargs):
        """
        Inicializa o contexto.
        
        Args:
            **kwargs: Campos extras para adicionar aos logs
        """
        self.context = kwargs
        self.old_factory = None
    
    def __enter__(self):
        """Entra no contexto."""
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sai do contexto."""
        logging.setLogRecordFactory(self.old_factory)


def log_triage_start(logger: logging.Logger, order_id: str) -> None:
    """
    Registra início de triagem.
    
    Args:
        logger: Logger a usar
        order_id: ID da ordem
    """
    logger.info(
        f"Iniciando triagem da ordem {order_id}",
        extra={"order_id": order_id, "event": "triage_start"}
    )


def log_triage_complete(
    logger: logging.Logger,
    order_id: str,
    duration_ms: int,
    classification: str,
    criticality: str
) -> None:
    """
    Registra conclusão de triagem.
    
    Args:
        logger: Logger a usar
        order_id: ID da ordem
        duration_ms: Duração em milissegundos
        classification: Classificação resultante
        criticality: Criticidade resultante
    """
    logger.info(
        f"Triagem concluída: {order_id} | {classification} | {criticality}",
        extra={
            "order_id": order_id,
            "event": "triage_complete",
            "duration_ms": duration_ms,
            "classification": classification,
            "criticality": criticality
        }
    )


def log_llm_call(
    logger: logging.Logger,
    order_id: str,
    model: str,
    duration_ms: int,
    success: bool,
    error: Optional[str] = None
) -> None:
    """
    Registra chamada à LLM.
    
    Args:
        logger: Logger a usar
        order_id: ID da ordem
        model: Nome do modelo
        duration_ms: Duração da chamada
        success: Se foi bem-sucedida
        error: Mensagem de erro (se houver)
    """
    if success:
        logger.info(
            f"LLM extraction successful: {order_id} | {model} | {duration_ms}ms",
            extra={
                "order_id": order_id,
                "event": "llm_call",
                "model": model,
                "duration_ms": duration_ms,
                "success": True
            }
        )
    else:
        logger.error(
            f"LLM extraction failed: {order_id} | {model} | {error}",
            extra={
                "order_id": order_id,
                "event": "llm_call",
                "model": model,
                "duration_ms": duration_ms,
                "success": False,
                "error": error
            }
        )


def log_expert_inference(
    logger: logging.Logger,
    order_id: str,
    rules_applied: list,
    duration_ms: int
) -> None:
    """
    Registra inferência do sistema especialista.
    
    Args:
        logger: Logger a usar
        order_id: ID da ordem
        rules_applied: Lista de regras aplicadas
        duration_ms: Duração da inferência
    """
    logger.info(
        f"Expert inference: {order_id} | {len(rules_applied)} rules | {duration_ms}ms",
        extra={
            "order_id": order_id,
            "event": "expert_inference",
            "rules_applied": rules_applied,
            "num_rules": len(rules_applied),
            "duration_ms": duration_ms
        }
    )


def log_validation_error(
    logger: logging.Logger,
    order_id: str,
    error_type: str,
    error_message: str
) -> None:
    """
    Registra erro de validação.
    
    Args:
        logger: Logger a usar
        order_id: ID da ordem
        error_type: Tipo de erro
        error_message: Mensagem do erro
    """
    logger.warning(
        f"Validation error: {order_id} | {error_type}",
        extra={
            "order_id": order_id,
            "event": "validation_error",
            "error_type": error_type,
            "error_message": error_message
        }
    )


def log_performance_metrics(
    logger: logging.Logger,
    metrics: Dict[str, Any]
) -> None:
    """
    Registra métricas de performance.
    
    Args:
        logger: Logger a usar
        metrics: Dicionário com métricas
    """
    logger.info(
        "Performance metrics",
        extra={
            "event": "performance_metrics",
            "metrics": metrics
        }
    )


# Inicializa logging na importação
setup_logging()
