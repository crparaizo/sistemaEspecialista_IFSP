#!/usr/bin/env python3
"""
Script para testar triagem de uma única ordem.

Útil para debugging e demonstração interativa.
"""

import sys
import json
import argparse
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.order import ServiceOrder
from src.triage.pipeline import TriagePipeline


def main():
    """Testa triagem de uma ordem."""
    parser = argparse.ArgumentParser(
        description="Testa triagem de uma ordem de serviço"
    )
    parser.add_argument(
        "--order-id",
        default="OS-TEST-001",
        help="ID da ordem"
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Descrição do problema"
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Mostra explicação detalhada"
    )
    parser.add_argument(
        "--output",
        help="Salva resultado em arquivo JSON"
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("TESTE DE TRIAGEM - ORDEM ÚNICA")
    print("="*70)
    print()
    
    # Cria ordem
    order = ServiceOrder(
        order_id=args.order_id,
        description=args.description
    )
    
    print(f"Ordem: {order.order_id}")
    print(f"Descrição: {order.description}")
    print()
    
    # Inicializa pipeline
    print("Inicializando pipeline...")
    pipeline = TriagePipeline()
    
    # Valida provedor
    validation = pipeline.validate_provider()
    if not validation["available"]:
        print("✗ Provedor LLM não está disponível!")
        print()
        print("Certifique-se de que o Ollama está rodando:")
        print("  ollama serve")
        return 1
    
    print(f"✓ LLM disponível: {validation['model']}")
    print()
    
    # Processa
    print("Processando...")
    print("-" * 70)
    
    try:
        if args.explain:
            explanation = pipeline.explain_decision(order)
            result_data = explanation["triage_result"]
            
            print("\n=== EXTRAÇÃO (Camada Conexionista) ===")
            extraction = explanation.get("facts_summary", {})
            print(f"  Equipamento: {extraction.get('equipamento', 'N/A')}")
            print(f"  Componente: {extraction.get('componente', 'N/A')}")
            print(f"  Tipo Manutenção: {extraction.get('tipo_manutencao', 'N/A')}")
            print(f"  Sintomas: {extraction.get('num_sintomas', 0)}")
            print(f"  Termos Técnicos: {extraction.get('num_termos_tecnicos', 0)}")
            
            print("\n=== FATOS DERIVADOS ===")
            derived = explanation.get("derived_facts", {})
            for key, value in derived.items():
                print(f"  {key}: {value}")
            
            print("\n=== REGRAS APLICADAS ===")
            for rule in explanation.get("rules_applied", []):
                print(f"  [{rule['id']}] {rule['name']}")
                print(f"      {rule['description']}")
            
            print("\n=== DECISÃO (Camada Simbólica) ===")
            decision = result_data["decision"]
            print(f"  Classificação: {decision['classificacao']}")
            print(f"  Criticidade: {decision['criticidade']}")
            print(f"  Urgência: {decision['urgencia']}")
            print(f"  Especialidade: {decision['especialidade']}")
            print(f"  Roteamento: {decision['roteamento']}")
            print(f"  Prioridade: {decision['prioridade']}")
            
            print("\n=== JUSTIFICATIVA ===")
            print(f"  {explanation.get('justificativa', 'N/A')}")
            
            print("\n=== PERFORMANCE ===")
            metadata = result_data.get("metadata", {})
            print(f"  LLM Inference: {metadata.get('llm_inference_time_ms', 0)}ms")
            print(f"  Expert Inference: {metadata.get('expert_inference_time_ms', 0)}ms")
            print(f"  Total: {metadata.get('total_time_ms', 0)}ms")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(explanation, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n✓ Explicação salva em: {args.output}")
        
        else:
            result = pipeline.process(order)
            
            print("\n=== RESULTADO ===")
            print(f"  Classificação: {result.decision.classificacao}")
            print(f"  Criticidade: {result.decision.criticidade}")
            print(f"  Urgência: {result.decision.urgencia}")
            print(f"  Especialidade: {result.decision.especialidade}")
            print(f"  Roteamento: {result.decision.roteamento}")
            print(f"  Prioridade: {result.decision.prioridade}")
            print(f"\n  Regras aplicadas: {', '.join(result.rules_applied)}")
            print(f"  Justificativa: {result.justificativa}")
            
            print(f"\n  Tempo total: {result.metadata.get('total_time_ms', 0)}ms")
            
            if args.output:
                # Converte resultado para dict
                result_dict = result.model_dump(mode='json')
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result_dict, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n✓ Resultado salvo em: {args.output}")
        
        print()
        print("-" * 70)
        print("✓ Triagem concluída com sucesso")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Erro ao processar: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
