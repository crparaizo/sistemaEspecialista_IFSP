"""
Cálculo de Métricas de Avaliação.

Calcula métricas para avaliar o desempenho do sistema,
comparando resultados produzidos com valores esperados.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..models.result import TriageResult
from .dataset import DatasetManager, DatasetItem


class EvaluationResult:
    """
    Resultado de uma avaliação.
    
    Attributes:
        order_id: ID da ordem avaliada
        expected: Valores esperados
        predicted: Valores produzidos pelo sistema
        matches: Campos que coincidiram
        mismatches: Campos que não coincidiram
    """
    
    def __init__(
        self,
        order_id: str,
        expected: Dict[str, Any],
        predicted: Dict[str, Any]
    ):
        """
        Inicializa resultado de avaliação.
        
        Args:
            order_id: ID da ordem
            expected: Valores esperados
            predicted: Valores preditos
        """
        self.order_id = order_id
        self.expected = expected
        self.predicted = predicted
        self.matches: Dict[str, bool] = {}
        self.mismatches: Dict[str, tuple] = {}
        
        self._compare()
    
    def _compare(self) -> None:
        """Compara valores esperados com preditos."""
        for field in self.expected:
            expected_val = self.expected[field]
            predicted_val = self.predicted.get(field)
            
            if expected_val == predicted_val:
                self.matches[field] = True
            else:
                self.matches[field] = False
                self.mismatches[field] = (expected_val, predicted_val)
    
    def is_correct(self, field: Optional[str] = None) -> bool:
        """
        Verifica se predição está correta.
        
        Args:
            field: Campo específico (None = todos)
            
        Returns:
            bool: True se correto
        """
        if field:
            return self.matches.get(field, False)
        return all(self.matches.values())
    
    def accuracy(self) -> float:
        """
        Calcula acurácia (proporção de campos corretos).
        
        Returns:
            float: Acurácia entre 0 e 1
        """
        if not self.matches:
            return 0.0
        
        correct = sum(1 for v in self.matches.values() if v)
        total = len(self.matches)
        
        return correct / total if total > 0 else 0.0


class MetricsCalculator:
    """
    Calculador de métricas de avaliação.
    
    Compara resultados do sistema com valores esperados
    e calcula métricas de desempenho.
    """
    
    def __init__(self):
        """Inicializa o calculador."""
        self.evaluations: List[EvaluationResult] = []
    
    def evaluate(
        self,
        triage_results: List[TriageResult],
        dataset: DatasetManager
    ) -> None:
        """
        Avalia resultados contra dataset.
        
        Args:
            triage_results: Resultados do sistema
            dataset: Dataset com valores esperados
        """
        self.evaluations = []
        
        for result in triage_results:
            # Busca item no dataset
            item = dataset.get_item(result.order_id)
            
            if not item or not item.expected:
                continue
            
            # Extrai valores preditos
            predicted = {
                "classificacao": result.decision.classificacao,
                "criticidade": result.decision.criticidade,
                "urgencia": result.decision.urgencia,
                "especialidade": result.decision.especialidade
            }
            
            # Cria avaliação
            eval_result = EvaluationResult(
                order_id=result.order_id,
                expected=item.expected,
                predicted=predicted
            )
            
            self.evaluations.append(eval_result)
    
    def accuracy(self, field: Optional[str] = None) -> float:
        """
        Calcula acurácia geral.
        
        Args:
            field: Campo específico (None = média de todos)
            
        Returns:
            float: Acurácia entre 0 e 1
        """
        if not self.evaluations:
            return 0.0
        
        if field:
            # Acurácia para campo específico
            correct = sum(
                1 for eval_r in self.evaluations
                if eval_r.is_correct(field)
            )
            return correct / len(self.evaluations)
        else:
            # Acurácia média de todos os campos
            accuracies = [eval_r.accuracy() for eval_r in self.evaluations]
            return sum(accuracies) / len(accuracies) if accuracies else 0.0
    
    def precision_recall_f1(
        self,
        field: str,
        positive_class: str
    ) -> Dict[str, float]:
        """
        Calcula precisão, recall e F1-score para uma classe.
        
        Args:
            field: Campo a avaliar (ex: "criticidade")
            positive_class: Classe positiva (ex: "Alta")
            
        Returns:
            dict: Métricas calculadas
        """
        tp = 0  # True Positives
        fp = 0  # False Positives
        fn = 0  # False Negatives
        
        for eval_r in self.evaluations:
            expected = eval_r.expected.get(field)
            predicted = eval_r.predicted.get(field)
            
            if predicted == positive_class and expected == positive_class:
                tp += 1
            elif predicted == positive_class and expected != positive_class:
                fp += 1
            elif predicted != positive_class and expected == positive_class:
                fn += 1
        
        # Calcula métricas
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) \
            if (precision + recall) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "support": tp + fn  # Total de casos da classe
        }
    
    def confusion_matrix(
        self,
        field: str
    ) -> Dict[str, Dict[str, int]]:
        """
        Gera matriz de confusão para um campo.
        
        Args:
            field: Campo a avaliar
            
        Returns:
            dict: Matriz de confusão
        """
        matrix: Dict[str, Dict[str, int]] = {}
        
        for eval_r in self.evaluations:
            expected = eval_r.expected.get(field, "Unknown")
            predicted = eval_r.predicted.get(field, "Unknown")
            
            if expected not in matrix:
                matrix[expected] = {}
            
            matrix[expected][predicted] = \
                matrix[expected].get(predicted, 0) + 1
        
        return matrix
    
    def get_mismatches(self, field: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retorna lista de casos onde houve erro.
        
        Args:
            field: Campo específico (None = todos os erros)
            
        Returns:
            list: Lista de erros
        """
        mismatches = []
        
        for eval_r in self.evaluations:
            if field:
                if not eval_r.is_correct(field):
                    mismatches.append({
                        "order_id": eval_r.order_id,
                        "field": field,
                        "expected": eval_r.expected.get(field),
                        "predicted": eval_r.predicted.get(field)
                    })
            else:
                if not eval_r.is_correct():
                    mismatches.append({
                        "order_id": eval_r.order_id,
                        "mismatches": eval_r.mismatches
                    })
        
        return mismatches
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de avaliação.
        
        Returns:
            dict: Relatório estruturado
        """
        if not self.evaluations:
            return {"error": "Nenhuma avaliação disponível"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_evaluations": len(self.evaluations),
            "overall_accuracy": self.accuracy(),
            "field_accuracies": {
                "classificacao": self.accuracy("classificacao"),
                "criticidade": self.accuracy("criticidade"),
                "urgencia": self.accuracy("urgencia"),
                "especialidade": self.accuracy("especialidade")
            },
            "confusion_matrices": {
                "classificacao": self.confusion_matrix("classificacao"),
                "criticidade": self.confusion_matrix("criticidade"),
                "urgencia": self.confusion_matrix("urgencia")
            },
            "mismatches_summary": {
                "total": len(self.get_mismatches()),
                "by_field": {
                    "classificacao": len(self.get_mismatches("classificacao")),
                    "criticidade": len(self.get_mismatches("criticidade")),
                    "urgencia": len(self.get_mismatches("urgencia")),
                    "especialidade": len(self.get_mismatches("especialidade"))
                }
            }
        }
        
        return report
    
    def save_report(
        self,
        output_path: str,
        include_details: bool = True
    ) -> None:
        """
        Salva relatório em arquivo JSON.
        
        Args:
            output_path: Caminho do arquivo de saída
            include_details: Incluir detalhes dos erros
        """
        report = self.generate_report()
        
        if include_details:
            report["mismatches_detail"] = self.get_mismatches()
        
        # Cria diretório se não existir
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Salva
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def print_summary(self) -> None:
        """Imprime sumário das métricas no console."""
        if not self.evaluations:
            print("Nenhuma avaliação disponível.")
            return
        
        print("\n" + "="*60)
        print("RESUMO DA AVALIAÇÃO")
        print("="*60)
        print(f"Total de avaliações: {len(self.evaluations)}")
        print(f"Acurácia geral: {self.accuracy():.2%}")
        print("\nAcurácia por campo:")
        print(f"  Classificação: {self.accuracy('classificacao'):.2%}")
        print(f"  Criticidade:   {self.accuracy('criticidade'):.2%}")
        print(f"  Urgência:      {self.accuracy('urgencia'):.2%}")
        print(f"  Especialidade: {self.accuracy('especialidade'):.2%}")
        print("\nTotal de erros por campo:")
        print(f"  Classificação: {len(self.get_mismatches('classificacao'))}")
        print(f"  Criticidade:   {len(self.get_mismatches('criticidade'))}")
        print(f"  Urgência:      {len(self.get_mismatches('urgencia'))}")
        print(f"  Especialidade: {len(self.get_mismatches('especialidade'))}")
        print("="*60 + "\n")
