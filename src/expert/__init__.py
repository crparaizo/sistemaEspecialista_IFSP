"""Camada Simbólica - Sistema Especialista."""
from .facts import Facts
from .rules import Rule, RuleBase
from .engine import InferenceEngine
from .decision import Decision

__all__ = ["Facts", "Rule", "RuleBase", "InferenceEngine", "Decision"]
