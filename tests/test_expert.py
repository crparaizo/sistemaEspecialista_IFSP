"""
Testes para sistema especialista.
"""

import pytest

from src.models.extraction import ExtractionResult
from src.expert.facts import Facts
from src.expert.rules import RuleBase
from src.expert.engine import InferenceEngine
from src.expert.decision import ExpertDecision


class TestFacts:
    """Testes para Facts."""
    
    def test_create_facts_from_extraction(self):
        """Testa criação de fatos a partir de extração."""
        extraction = ExtractionResult(
            equipamento="motor esteira 03",
            componente="motor",
            sintomas=["vibração excessiva", "ruído"],
            tipo_manutencao="corretiva",
            termos_tecnicos=["motor", "vibração", "esteira"]
        )
        
        facts = Facts.from_extraction(extraction)
        
        assert facts.equipamento == "motor esteira 03"
        assert len(facts.sintomas) == 2
        assert facts.tipo_manutencao == "corretiva"
    
    def test_derived_facts_critical_symptoms(self):
        """Testa detecção de sintomas críticos."""
        extraction = ExtractionResult(
            sintomas=["fumaça", "superaquecimento"],
            termos_tecnicos=[]
        )
        
        facts = Facts.from_extraction(extraction)
        
        assert facts.tem_sintomas_criticos is True
    
    def test_derived_facts_electrical_terms(self):
        """Testa detecção de termos elétricos."""
        extraction = ExtractionResult(
            termos_tecnicos=["motor", "disjuntor", "corrente"],
            sintomas=[]
        )
        
        facts = Facts.from_extraction(extraction)
        
        assert facts.tem_termos_eletricos is True
    
    def test_derived_facts_mechanical_terms(self):
        """Testa detecção de termos mecânicos."""
        extraction = ExtractionResult(
            termos_tecnicos=["rolamento", "vibração", "lubrificação"],
            sintomas=[]
        )
        
        facts = Facts.from_extraction(extraction)
        
        assert facts.tem_termos_mecanicos is True
    
    def test_has_symptom_method(self):
        """Testa método has_symptom."""
        extraction = ExtractionResult(
            sintomas=["vibração excessiva", "ruído anormal"]
        )
        
        facts = Facts.from_extraction(extraction)
        
        assert facts.has_symptom("vibração") is True
        assert facts.has_symptom("ruído") is True
        assert facts.has_symptom("vazamento") is False
    
    def test_has_term_method(self):
        """Testa método has_term."""
        extraction = ExtractionResult(
            termos_tecnicos=["motor", "esteira", "rolamento"]
        )
        
        facts = Facts.from_extraction(extraction)
        
        assert facts.has_term("motor") is True
        assert facts.has_term("sensor") is False


class TestRuleBase:
    """Testes para RuleBase."""
    
    def test_create_rule_base(self):
        """Testa criação da base de regras."""
        rule_base = RuleBase()
        
        assert len(rule_base.rules) > 0
        assert rule_base.get_rule_by_id("REGRA_001") is not None
    
    def test_rules_ordered_by_priority(self):
        """Testa ordenação por prioridade."""
        rule_base = RuleBase()
        rules = rule_base.get_rules()
        
        # Verifica se está ordenado
        priorities = [rule.priority for rule in rules]
        assert priorities == sorted(priorities)
    
    def test_fallback_rule_exists(self):
        """Testa existência de regra fallback."""
        rule_base = RuleBase()
        fallback = rule_base.get_rule_by_id("REGRA_999")
        
        assert fallback is not None
        assert fallback.name == "Regra Fallback"


class TestInferenceEngine:
    """Testes para InferenceEngine."""
    
    def test_inference_with_critical_symptoms(self):
        """Testa inferência com sintomas críticos."""
        extraction = ExtractionResult(
            sintomas=["fumaça", "curto-circuito"],
            termos_tecnicos=["disjuntor", "elétrico"]
        )
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        assert decision.criticidade == "Crítica"
        assert decision.urgencia == "Emergencial"
        assert "REGRA_001" in decision.regras_aplicadas
    
    def test_inference_mechanical_issue(self):
        """Testa inferência para problema mecânico."""
        extraction = ExtractionResult(
            sintomas=["vibração", "ruído"],
            termos_tecnicos=["motor", "rolamento", "esteira"]
        )
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        assert decision.classificacao == "Mecânica"
        assert decision.especialidade == "Eletromecânica"
        assert decision.criticidade == "Alta"
    
    def test_inference_preventive_maintenance(self):
        """Testa inferência para manutenção preventiva."""
        extraction = ExtractionResult(
            tipo_manutencao="preventiva",
            termos_tecnicos=["lubrificação", "óleo"]
        )
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        assert decision.urgencia == "Normal"
        assert "REGRA_202" in decision.regras_aplicadas
    
    def test_inference_instrumentation(self):
        """Testa inferência para instrumentação."""
        extraction = ExtractionResult(
            termos_tecnicos=["sensor", "temperatura", "calibração"],
            sintomas=["leitura inconsistente"]
        )
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        assert decision.classificacao == "Instrumentação"
        assert decision.especialidade == "Instrumentação"
    
    def test_fallback_applies_when_no_rules_match(self):
        """Testa que fallback aplica quando nenhuma regra específica casa."""
        extraction = ExtractionResult(
            sintomas=["problema genérico"],
            termos_tecnicos=[]
        )
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        # Fallback deve garantir valores padrão
        assert decision.classificacao != ""
        assert decision.criticidade != ""
        assert decision.urgencia != ""
        assert decision.especialidade != ""
    
    def test_decision_always_complete(self):
        """Testa que decisão sempre tem todos os campos."""
        extraction = ExtractionResult()
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        assert decision.classificacao
        assert decision.criticidade
        assert decision.urgencia
        assert decision.especialidade
        assert decision.roteamento
        assert decision.prioridade > 0
    
    def test_explain_decision(self):
        """Testa explicação de decisão."""
        extraction = ExtractionResult(
            sintomas=["vibração"],
            termos_tecnicos=["motor"]
        )
        
        facts = Facts.from_extraction(extraction)
        engine = InferenceEngine()
        decision = engine.infer(facts)
        
        explanation = engine.explain_decision(facts, decision)
        
        assert "facts_summary" in explanation
        assert "rules_applied" in explanation
        assert "decision" in explanation
        assert isinstance(explanation["rules_applied"], list)
