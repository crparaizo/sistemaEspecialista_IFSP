#!/usr/bin/env python3
"""
Script para executar a API REST.

Inicia o servidor FastAPI com Uvicorn.
"""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.routes import run_api


if __name__ == "__main__":
    print("="*70)
    print("INICIANDO API REST - SISTEMA TRIADOR")
    print("="*70)
    print()
    print("Documentação interativa disponível em:")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/redoc")
    print()
    print("Pressione Ctrl+C para parar")
    print("="*70)
    print()
    
    run_api()
