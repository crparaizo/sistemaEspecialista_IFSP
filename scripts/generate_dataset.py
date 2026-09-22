#!/usr/bin/env python3
"""
Script para gerar dataset sintético de ordens de serviço.

Útil para criar novos datasets de teste.
"""

import sys
import json
import argparse
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_sample_orders():
    """Gera ordens de serviço de exemplo."""
    orders = [
        {
            "order_id": "OS-GEN-001",
            "description": "Bomba centrífuga B-15 com vazamento no selo mecânico. Perda estimada de 5 litros/hora.",
            "requester": "Operador Utilidades",
            "location": "Casa de Bombas",
            "expected": {
                "classificacao": "Mecânica",
                "criticidade": "Alta",
                "urgencia": "Alta",
                "especialidade": "Mecânica"
            }
        },
        {
            "order_id": "OS-GEN-002",
            "description": "Transformador TR-03 apresentando ruído anormal e aquecimento elevado. Temperatura 20°C acima do normal.",
            "requester": "Eletricista Subestação",
            "location": "Subestação Principal",
            "expected": {
                "classificacao": "Elétrica",
                "criticidade": "Crítica",
                "urgencia": "Emergencial",
                "especialidade": "Elétrica"
            }
        },
        {
            "order_id": "OS-GEN-003",
            "description": "Realizar inspeção visual e teste de funcionamento do sistema de alarme de incêndio conforme NR-23.",
            "requester": "Engenharia Segurança",
            "location": "Todas as áreas",
            "expected": {
                "classificacao": "Geral",
                "criticidade": "Média",
                "urgencia": "Normal",
                "especialidade": "Manutenção Geral"
            }
        }
    ]
    
    return orders


def main():
    """Gera dataset."""
    parser = argparse.ArgumentParser(
        description="Gera dataset sintético de ordens de serviço"
    )
    parser.add_argument(
        "--output",
        default="data/generated_dataset.json",
        help="Caminho para salvar dataset"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Número de ordens a gerar (usa templates)"
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("GERADOR DE DATASET SINTÉTICO")
    print("="*70)
    print()
    
    # Gera ordens
    orders = generate_sample_orders()[:args.count]
    
    print(f"Gerando {len(orders)} ordens...")
    for order in orders:
        print(f"  - {order['order_id']}: {order['description'][:50]}...")
    
    print()
    
    # Salva
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Dataset salvo em: {output_path}")
    print()
    print("Para adicionar mais ordens, edite o arquivo manualmente ou")
    print("modifique a função generate_sample_orders() neste script.")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
