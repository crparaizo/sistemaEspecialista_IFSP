#!/usr/bin/env python3
"""
Script para executar avaliação do sistema.

Processa dataset de ordens de serviço e gera relatório
comparando resultados com valores esperados.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.order import ServiceOrder
from src.triage.pipeline import TriagePipeline
from src.evaluation.dataset import DatasetManager
from src.evaluation.metrics import MetricsCalculator
from src.config import get_settings


def main():
    """Executa avaliação."""
    parser = argparse.ArgumentParser(
        description="Avalia o sistema triador com dataset"
    )
    parser.add_argument(
        "--dataset",
        default="data/synthetic_orders.json",
        help="Caminho para arquivo de dataset JSON"
    )
    parser.add_argument(
        "--output",
        help="Caminho para salvar relatório (opcional)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostra detalhes de cada processamento"
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("AVALIAÇÃO DO SISTEMA TRIADOR")
    print("="*70)
    print()
    
    # Carrega dataset
    print(f"Carregando dataset: {args.dataset}")
    try:
        dataset = DatasetManager(args.dataset)
        print(f"✓ Dataset carregado: {len(dataset)} ordens")
        print()
    except FileNotFoundError as e:
        print(f"✗ Erro: {e}")
        return 1
    
    # Estatísticas do dataset
    stats = dataset.get_statistics()
    print("Estatísticas do dataset:")
    print(f"  Total de itens: {stats['total_items']}")
    print(f"  Com valores esperados: {stats['with_expected']}")
    if stats.get('classifications'):
        print(f"  Classificações: {stats['classifications']}")
    print()
    
    # Inicializa pipeline
    print("Inicializando pipeline...")
    pipeline = TriagePipeline()
    
    # Valida provedor
    validation = pipeline.validate_provider()
    if not validation["available"]:
        print("✗ Provedor LLM não está disponível!")
        print(f"  Provider: {validation['provider']}")
        print(f"  Model: {validation['model']}")
        print()
        print("Certifique-se de que o Ollama está rodando:")
        print("  ollama serve")
        return 1
    
    print(f"✓ Provedor LLM disponível")
    print(f"  Provider: {validation['provider']}")
    print(f"  Model: {validation['model']}")
    print()
    
    # Processa todas as ordens
    print("Processando ordens...")
    print("-" * 70)
    
    orders = dataset.get_orders()
    results = []
    
    for i, order in enumerate(orders, 1):
        if args.verbose:
            print(f"\n[{i}/{len(orders)}] {order.order_id}")
            print(f"  Descrição: {order.description[:60]}...")
        else:
            print(f"[{i}/{len(orders)}] {order.order_id} ", end="", flush=True)
        
        try:
            result = pipeline.process(order)
            results.append(result)
            
            if args.verbose:
                print(f"  Classificação: {result.decision.classificacao}")
                print(f"  Criticidade: {result.decision.criticidade}")
                print(f"  Urgência: {result.decision.urgencia}")
                print(f"  Regras: {', '.join(result.rules_applied)}")
            else:
                print("✓")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    print()
    print("-" * 70)
    print(f"Processamento concluído: {len(results)}/{len(orders)} ordens")
    print()
    
    # Calcula métricas
    print("Calculando métricas...")
    calculator = MetricsCalculator()
    calculator.evaluate(results, dataset)
    
    # Mostra sumário
    calculator.print_summary()
    
    # Salva relatório se solicitado
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/evaluation_results/evaluation_{timestamp}.json"
    
    calculator.save_report(output_path, include_details=True)
    print(f"Relatório salvo em: {output_path}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
