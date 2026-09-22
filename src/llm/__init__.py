"""Camada Conexionista - LLM/SLM Provider."""
from .provider import LLMProvider
from .ollama_provider import OllamaProvider
from .schemas import ExtractionSchema

__all__ = ["LLMProvider", "OllamaProvider", "ExtractionSchema"]
