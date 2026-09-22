"""
Base de Regras do Sistema Especialista.

Define as regras de negócio que determinam classificação,
criticidade, urgência e roteamento das ordens de serviço.
"""

from typing import Callable, List, Optional
from pydantic import BaseModel, Field

from .facts import Facts
from .decision import ExpertDecision


class Rule(BaseModel):
    """
    Representa uma regra do sistema especialista.
    
    Uma regra tem:
    - Condição: quando a regra se aplica
    - Ação: o que fazer quando a condição é verdadeira
    - Prioridade: ordem de avaliação
    
    Attributes:
        id: Identificador único da regra
        name: Nome descritivo
        description: Descrição do que a regra faz
        priority: Prioridade (menor = maior prioridade)
        condition: Função que avalia se a regra se aplica
        action: Função que modifica a decisão
    """
    
    id: str = Field(..., description="ID único da regra")
    name: str = Field(..., description="Nome da regra")
    description: str = Field(..., description="Descrição da regra")
    priority: int = Field(default=100, description="Prioridade (menor = maior)")
    
    class Config:
        # Permite campos arbitrários (para funções)
        arbitrary_types_allowed = True
    
    # Campos para funções (não serializáveis)
    condition: Optional[Callable[[Facts], bool]] = None
    action: Optional[Callable[[Facts, ExpertDecision], None]] = None
    
    def applies(self, facts: Facts) -> bool:
        """
        Verifica se a regra se aplica aos fatos.
        
        Args:
            facts: Fatos do sistema
            
        Returns:
            bool: True se a regra se aplica
        """
        if self.condition is None:
            return False
        return self.condition(facts)
    
    def execute(self, facts: Facts, decision: ExpertDecision) -> None:
        """
        Executa a ação da regra.
        
        Args:
            facts: Fatos do sistema
            decision: Decisão a ser modificada
        """
        if self.action is not None:
            self.action(facts, decision)
            decision.add_rule(self.id, self.description)


class RuleBase:
    """
    Base de conhecimento com todas as regras do sistema.
    
    Organiza e gerencia o conjunto de regras disponíveis.
    """
    
    def __init__(self):
        """Inicializa a base de regras."""
        self.rules: List[Rule] = []
        self._initialize_rules()
    
    def _initialize_rules(self) -> None:
        """Cria o conjunto inicial de regras."""
        
        # ============================================================
        # REGRAS DE CRITICIDADE
        # ============================================================
        
        # Regra 001: Sintomas críticos = Criticidade CRÍTICA
        self.rules.append(Rule(
            id="REGRA_001",
            name="Criticidade Crítica por Sintomas",
            description="Sintomas críticos detectados (risco de segurança ou parada)",
            priority=10,
            condition=lambda facts: facts.tem_sintomas_criticos,
            action=lambda facts, decision: self._set_critical_severity(decision)
        ))
        
        # Regra 002: Vibração + Ruído = Alta criticidade
        self.rules.append(Rule(
            id="REGRA_002",
            name="Alta Criticidade por Vibração",
            description="Vibração e ruído indicam problema mecânico grave",
            priority=20,
            condition=lambda facts: (
                facts.has_symptom("vibração") and 
                facts.has_symptom("ruído")
            ),
            action=lambda facts, decision: self._set_high_severity(decision)
        ))
        
        # Regra 003: Vazamento = Alta criticidade
        self.rules.append(Rule(
            id="REGRA_003",
            name="Alta Criticidade por Vazamento",
            description="Vazamento detectado",
            priority=20,
            condition=lambda facts: facts.has_symptom("vazamento"),
            action=lambda facts, decision: self._set_high_severity(decision)
        ))
        
        # ============================================================
        # REGRAS DE CLASSIFICAÇÃO E ESPECIALIDADE
        # ============================================================
        
        # Regra 101: Termos elétricos = Classificação Elétrica
        self.rules.append(Rule(
            id="REGRA_101",
            name="Classificação Elétrica",
            description="Termos elétricos identificados",
            priority=50,
            condition=lambda facts: facts.tem_termos_eletricos,
            action=lambda facts, decision: self._classify_electrical(decision)
        ))
        
        # Regra 102: Termos mecânicos = Classificação Mecânica
        self.rules.append(Rule(
            id="REGRA_102",
            name="Classificação Mecânica",
            description="Termos mecânicos identificados",
            priority=50,
            condition=lambda facts: facts.tem_termos_mecanicos,
            action=lambda facts, decision: self._classify_mechanical(decision)
        ))
        
        # Regra 103: Termos instrumentação = Classificação Instrumentação
        self.rules.append(Rule(
            id="REGRA_103",
            name="Classificação Instrumentação",
            description="Termos de instrumentação identificados",
            priority=50,
            condition=lambda facts: facts.tem_termos_instrumentacao,
            action=lambda facts, decision: self._classify_instrumentation(decision)
        ))
        
        # Regra 104: Termos automação = Classificação Automação
        self.rules.append(Rule(
            id="REGRA_104",
            name="Classificação Automação",
            description="Termos de automação identificados",
            priority=50,
            condition=lambda facts: facts.tem_termos_automacao,
            action=lambda facts, decision: self._classify_automation(decision)
        ))
        
        # ============================================================
        # REGRAS DE URGÊNCIA
        # ============================================================
        
        # Regra 201: Criticidade Crítica = Urgência Emergencial
        self.rules.append(Rule(
            id="REGRA_201",
            name="Urgência Emergencial",
            description="Criticidade crítica requer ação imediata",
            priority=30,
            condition=lambda facts: facts.tem_sintomas_criticos,
            action=lambda facts, decision: self._set_emergency_urgency(decision)
        ))
        
        # Regra 202: Manutenção Preventiva = Urgência Normal
        self.rules.append(Rule(
            id="REGRA_202",
            name="Urgência Normal para Preventiva",
            description="Manutenção preventiva tem urgência normal",
            priority=80,
            condition=lambda facts: facts.tipo_manutencao == "preventiva",
            action=lambda facts, decision: self._set_normal_urgency(decision)
        ))
        
        # Regra 203: Corretiva com Alta Criticidade = Alta Urgência
        self.rules.append(Rule(
            id="REGRA_203",
            name="Alta Urgência para Corretiva",
            description="Manutenção corretiva com alta criticidade",
            priority=40,
            condition=lambda facts: (
                facts.tipo_manutencao == "corretiva" and
                (facts.has_symptom("vibração") or facts.has_symptom("vazamento"))
            ),
            action=lambda facts, decision: self._set_high_urgency(decision)
        ))
        
        # ============================================================
        # REGRA DE FALLBACK
        # ============================================================
        
        # Regra 999: Fallback para casos não cobertos
        self.rules.append(Rule(
            id="REGRA_999",
            name="Regra Fallback",
            description="Classificação padrão quando nenhuma regra específica se aplica",
            priority=999,
            condition=lambda facts: True,  # Sempre se aplica
            action=lambda facts, decision: self._apply_fallback(decision)
        ))
    
    # ============================================================
    # MÉTODOS AUXILIARES PARA AÇÕES
    # ============================================================
    
    def _set_critical_severity(self, decision: ExpertDecision) -> None:
        """Define criticidade como CRÍTICA."""
        decision.criticidade = "Crítica"
        decision.prioridade = min(decision.prioridade, 1)
    
    def _set_high_severity(self, decision: ExpertDecision) -> None:
        """Define criticidade como ALTA."""
        if decision.criticidade not in ["Crítica"]:
            decision.criticidade = "Alta"
            decision.prioridade = min(decision.prioridade, 2)
    
    def _set_medium_severity(self, decision: ExpertDecision) -> None:
        """Define criticidade como MÉDIA."""
        if decision.criticidade not in ["Crítica", "Alta"]:
            decision.criticidade = "Média"
            decision.prioridade = min(decision.prioridade, 3)
    
    def _classify_electrical(self, decision: ExpertDecision) -> None:
        """Classifica como Elétrica."""
        decision.classificacao = "Elétrica"
        decision.especialidade = "Elétrica"
        decision.roteamento = "Equipe Elétrica"
    
    def _classify_mechanical(self, decision: ExpertDecision) -> None:
        """Classifica como Mecânica."""
        decision.classificacao = "Mecânica"
        decision.especialidade = "Eletromecânica"
        decision.roteamento = "Equipe Mecânica"
    
    def _classify_instrumentation(self, decision: ExpertDecision) -> None:
        """Classifica como Instrumentação."""
        decision.classificacao = "Instrumentação"
        decision.especialidade = "Instrumentação"
        decision.roteamento = "Equipe Instrumentação"
    
    def _classify_automation(self, decision: ExpertDecision) -> None:
        """Classifica como Automação."""
        decision.classificacao = "Automação"
        decision.especialidade = "Automação"
        decision.roteamento = "Equipe Automação"
    
    def _set_emergency_urgency(self, decision: ExpertDecision) -> None:
        """Define urgência como EMERGENCIAL."""
        decision.urgencia = "Emergencial"
        decision.prioridade = min(decision.prioridade, 1)
    
    def _set_high_urgency(self, decision: ExpertDecision) -> None:
        """Define urgência como ALTA."""
        if decision.urgencia not in ["Emergencial"]:
            decision.urgencia = "Alta"
    
    def _set_normal_urgency(self, decision: ExpertDecision) -> None:
        """Define urgência como NORMAL."""
        if decision.urgencia not in ["Emergencial", "Alta"]:
            decision.urgencia = "Normal"
    
    def _apply_fallback(self, decision: ExpertDecision) -> None:
        """Aplica valores padrão se nenhuma regra específica foi aplicada."""
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
    
    def get_rules(self) -> List[Rule]:
        """
        Retorna todas as regras ordenadas por prioridade.
        
        Returns:
            List[Rule]: Lista de regras ordenadas
        """
        return sorted(self.rules, key=lambda r: r.priority)
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        """
        Busca uma regra pelo ID.
        
        Args:
            rule_id: ID da regra
            
        Returns:
            Rule ou None: Regra encontrada ou None
        """
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
