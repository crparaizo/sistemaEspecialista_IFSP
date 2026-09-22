"""
Configuração de fixtures para testes.
"""

import pytest
from pathlib import Path

from src.config.settings import reset_settings


@pytest.fixture(autouse=True)
def reset_config():
    """Reseta configurações antes de cada teste."""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def sample_order_data():
    """Dados de exemplo para ordens de serviço."""
    return [
        {
            "order_id": "OS-001",
            "description": "Motor da esteira 03 apresenta vibração excessiva",
            "requester": "Supervisor",
            "location": "Linha 3"
        },
        {
            "order_id": "OS-002",
            "description": "Disjuntor desarma frequentemente",
            "requester": "Eletricista",
            "location": "Painel CCM"
        },
        {
            "order_id": "OS-003",
            "description": "Sensor de temperatura com leituras inconsistentes",
            "requester": "Operador",
            "location": "Linha Processo"
        }
    ]


@pytest.fixture
def temp_dataset_file(tmp_path, sample_order_data):
    """Cria arquivo temporário de dataset."""
    import json
    
    dataset_file = tmp_path / "test_dataset.json"
    
    with open(dataset_file, 'w', encoding='utf-8') as f:
        json.dump(sample_order_data, f)
    
    return str(dataset_file)
