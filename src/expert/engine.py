"""
Motor de Inferência do Sistema Especialista.

Implementa o mecanismo de inferência forward chaining
que aplica regras aos fatos para produzir decisões.
"""

from typing import List, Optional
import time

from .facts import Facts
from .rules import RuleBase, Rule
from .decision import ExpertDecision
from ..config import get_settings


class InferenceEngine:
    """
    Motor de inferência forward chaining.
    
    Aplica regras de forma sequencial aos fatos, modificando
    a decisão conforme as condições são satisfeitas.
    """
    
    def __init__(self, rule_base: Optional[RuleBase] = None):
        """
        Inicializa o motor de inferência.
        
        Args:
            rule_base: Base de regras (cria uma nova se None)
        """
        self.settings = get_settings()
        self.rule_base = rule_base or RuleBase()
    
    def infer(self, facts: Facts) -> ExpertDecision:
        """
        Executa inferência sobre os fatos fornecidos.
        
        Aplica as regras em ordem de prioridade, modificando
        a decisão conforme as condições são satisfeitas.
        
        Args:
            facts: Fatos do sistema
            
        Returns:
            ExpertDecision: Decisão produzida
        """
        start_time = time.time()
        
        # Inicializa decisão vazia
        decision = ExpertDecision(
            classificacao="",
            criticidade="",
            urgencia="",
            especialidade="",
            roteamento="",
            prioridade=5  # Menor prioridade por padrão
        )
        
        # Obtém regras ordenadas por prioridade
        rules = self.rule_base.get_rules()
        
        # Aplica regras em ordem
        rules_applied = 0
        for rule in rules:
            # Verifica se a condição da regra é satisfeita
            if rule.applies(facts):
                # Executa a ação da regra
                rule.execute(facts, decision)
                rules_applied += 1
        
        # Se nenhuma regra foi aplicada (exceto fallback), aplica fallback
        if rules_applied == 0:
            fallback = self.rule_base.get_rule_by_id("REGRA_999")
            if fallback:
                fallback.execute(facts, decision)
        
        # Garante que todos os campos estão preenchidos
        self._ensure_complete_decision(decision)
        
        # Adiciona metadata
        inference_time = int((time.time() - start_time) * 1000)  # ms
        
        return decision
    
    def _ensure_complete_decision(self, decision: ExpertDecision) -> None:
        """
        Garante que todos os campos da decisão estão preenchidos.
        
        Args:
            decision: Decisão a validar
        """
        if not decision.classificacao:
            decision.classificacao = "Geral"
        if not decision.criticidade:
            decision.criticidade = "Média"
        if not decision.urgencia:
            decision.urgencia = "Normal"
        if not decision.especialidade:
            decision.especialidade = "Manutenção Geral"
        if not decision.roteamento:
            decision.roteamento = "Equipe Manutenção"
        if decision.prioridade == 0:
            decision.prioridade = 3
        if not decision.justificativa:
            decision.justificativa = "Classificação padrão aplicada"
    
    def explain_decision(self, facts: Facts, decision: ExpertDecision) -> dict:
        """
        Gera explicação detalhada de uma decisão.
        
        Args:
            facts: Fatos utilizados
            decision: Decisão produzida
            
        Returns:
            dict: Explicação estruturada
        """
        explanation = {
            "facts_summary": {
                "equipamento": facts.equipamento,
                "componente": facts.componente,
                "num_sintomas": len(facts.sintomas),
                "num_termos_tecnicos": len(facts.termos_tecnicos),
                "tipo_manutencao": facts.tipo_manutencao
            },
            "derived_facts": {
                "tem_sintomas_criticos": facts.tem_sintomas_criticos,
                "tem_termos_eletricos": facts.tem_termos_eletricos,
                "tem_termos_mecanicos": facts.tem_termos_mecanicos,
                "tem_termos_instrumentacao": facts.tem_termos_instrumentacao,
                "tem_termos_automacao": facts.tem_termos_automacao
            },
            "rules_applied": [],
            "decision": {
                "classificacao": decision.classificacao,
                "criticidade": decision.criticidade,
                "urgencia": decision.urgencia,
                "especialidade": decision.especialidade,
                "roteamento": decision.roteamento,
                "prioridade": decision.prioridade
            },
            "justificativa": decision.justificativa
        }
        
        # Adiciona detalhes das regras aplicadas
        for rule_id in decision.regras_aplicadas:
            rule = self.rule_base.get_rule_by_id(rule_id)
            if rule:
                explanation["rules_applied"].append({
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "priority": rule.priority
                })
        
        return explanation
    
    def test_rule(self, rule_id: str, facts: Facts) -> dict:
        """
        Testa se uma regra específica se aplica aos fatos.
        
        Útil para debugging e validação de regras.
        
        Args:
            rule_id: ID da regra a testar
            facts: Fatos a testar
            
        Returns:
            dict: Resultado do teste
        """
        rule = self.rule_base.get_rule_by_id(rule_id)
        
        if not rule:
            return {
                "error": f"Regra {rule_id} não encontrada"
            }
        
        applies = rule.applies(facts)
        
        return {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "applies": applies,
            "description": rule.description
        }
    
    def get_applicable_rules(self, facts: Facts) -> List[Rule]:
        """
        Retorna todas as regras aplicáveis aos fatos.
        
        Args:
            facts: Fatos do sistema
            
        Returns:
            List[Rule]: Regras aplicáveis
        """
        applicable = []
        for rule in self.rule_base.get_rules():
            if rule.applies(facts):
                applicable.append(rule)
        return applicable
