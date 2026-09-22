"""
Representação de Fatos para o Sistema Especialista.

Fatos são assertivas sobre o estado do mundo que o sistema
especialista utiliza para aplicar suas regras.
"""

from typing import List, Optional, Set
from pydantic import BaseModel, Field

from ..models.extraction import ExtractionResult


class Facts(BaseModel):
    """
    Conjunto de fatos extraídos da ordem de serviço.
    
    Representa o conhecimento estruturado sobre a OS que será
    usado pelo motor de inferência para aplicar regras.
    
    Attributes:
        equipamento: Equipamento identificado
        componente: Componente específico
        sintomas: Lista de sintomas observados
        tipo_manutencao: Tipo de manutenção
        termos_tecnicos: Termos técnicos identificados
        especialidade_sugerida: Sugestão da LLM (não é decisão)
        
        # Fatos derivados (calculados)
        tem_sintomas_criticos: Presença de sintomas críticos
        tem_termos_eletricos: Presença de termos elétricos
        tem_termos_mecanicos: Presença de termos mecânicos
        tem_termos_instrumentacao: Presença de termos de instrumentação
        tem_termos_automacao: Presença de termos de automação
    """
    
    # Fatos primários (da extração)
    equipamento: Optional[str] = None
    componente: Optional[str] = None
    sintomas: List[str] = Field(default_factory=list)
    tipo_manutencao: Optional[str] = None
    termos_tecnicos: List[str] = Field(default_factory=list)
    especialidade_sugerida: Optional[str] = None
    
    # Fatos derivados (calculados automaticamente)
    tem_sintomas_criticos: bool = False
    tem_termos_eletricos: bool = False
    tem_termos_mecanicos: bool = False
    tem_termos_instrumentacao: bool = False
    tem_termos_automacao: bool = False
    
    # Conjuntos de termos para classificação
    _sintomas_criticos: Set[str] = {
        "fumaça", "fogo", "incêndio", "curto", "curto-circuito",
        "superaquecimento", "superaquecido", "choque", "vazamento crítico",
        "explosão", "risco", "perigo", "emergência", "parada total",
        "parada produção", "acidente"
    }
    
    _termos_eletricos: Set[str] = {
        "motor", "elétrico", "disjuntor", "fusível", "cabo", "fiação",
        "corrente", "tensão", "voltagem", "curto", "eletricidade",
        "transformador", "gerador", "bateria", "energia", "painel elétrico"
    }
    
    _termos_mecanicos: Set[str] = {
        "rolamento", "correia", "corrente", "engrenagem", "eixo",
        "mancal", "lubrificação", "óleo", "graxa", "vibração",
        "desalinhamento", "desbalanceamento", "folga", "desgaste",
        "bomba", "válvula mecânica", "pistão", "cilindro"
    }
    
    _termos_instrumentacao: Set[str] = {
        "sensor", "transmissor", "medidor", "indicador", "calibração",
        "temperatura", "pressão", "nível", "vazão", "leitura",
        "sinal", "4-20ma", "pt100", "termopar", "manômetro"
    }
    
    _termos_automacao: Set[str] = {
        "clp", "plc", "controlador", "automação", "scada", "hmi",
        "rede", "comunicação", "protocolo", "modbus", "profibus",
        "ethernet", "software", "programa", "lógica"
    }
    
    @classmethod
    def from_extraction(cls, extraction: ExtractionResult) -> "Facts":
        """
        Cria um conjunto de fatos a partir da extração da LLM.
        
        Args:
            extraction: Resultado da extração
            
        Returns:
            Facts: Fatos estruturados
        """
        # Cria fatos primários
        facts = cls(
            equipamento=extraction.equipamento,
            componente=extraction.componente,
            sintomas=extraction.sintomas,
            tipo_manutencao=extraction.tipo_manutencao,
            termos_tecnicos=extraction.termos_tecnicos,
            especialidade_sugerida=extraction.especialidade_sugerida
        )
        
        # Calcula fatos derivados
        facts._calculate_derived_facts()
        
        return facts
    
    def _calculate_derived_facts(self) -> None:
        """
        Calcula fatos derivados a partir dos fatos primários.
        
        Este método identifica padrões nos sintomas e termos técnicos
        para facilitar a aplicação de regras.
        """
        # Normaliza texto para comparação
        all_text = " ".join([
            self.equipamento or "",
            self.componente or "",
            " ".join(self.sintomas),
            " ".join(self.termos_tecnicos)
        ]).lower()
        
        # Verifica sintomas críticos
        self.tem_sintomas_criticos = any(
            termo in all_text for termo in self._sintomas_criticos
        )
        
        # Verifica presença de termos por especialidade
        self.tem_termos_eletricos = any(
            termo in all_text for termo in self._termos_eletricos
        )
        
        self.tem_termos_mecanicos = any(
            termo in all_text for termo in self._termos_mecanicos
        )
        
        self.tem_termos_instrumentacao = any(
            termo in all_text for termo in self._termos_instrumentacao
        )
        
        self.tem_termos_automacao = any(
            termo in all_text for termo in self._termos_automacao
        )
    
    def has_symptom(self, symptom: str) -> bool:
        """
        Verifica se um sintoma específico está presente.
        
        Args:
            symptom: Sintoma a buscar (case-insensitive)
            
        Returns:
            bool: True se o sintoma está presente
        """
        symptom_lower = symptom.lower()
        return any(symptom_lower in s.lower() for s in self.sintomas)
    
    def has_term(self, term: str) -> bool:
        """
        Verifica se um termo técnico está presente.
        
        Args:
            term: Termo a buscar (case-insensitive)
            
        Returns:
            bool: True se o termo está presente
        """
        term_lower = term.lower()
        return any(term_lower in t.lower() for t in self.termos_tecnicos)
    
    def get_all_text(self) -> str:
        """
        Retorna todo o texto dos fatos concatenado.
        
        Útil para buscas gerais.
        
        Returns:
            str: Texto completo normalizado
        """
        return " ".join([
            self.equipamento or "",
            self.componente or "",
            " ".join(self.sintomas),
            " ".join(self.termos_tecnicos)
        ]).lower()
    
    class Config:
        # Permite campos privados no modelo
        underscore_attrs_are_private = True
