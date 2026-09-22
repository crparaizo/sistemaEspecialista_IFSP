"""
Gerenciador de Dataset para Avaliação.

Carrega e gerencia datasets de ordens de serviço
para avaliação do sistema.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.order import ServiceOrder


class DatasetItem:
    """
    Item do dataset com ordem e valores esperados.
    
    Attributes:
        order: Ordem de serviço
        expected: Valores esperados para comparação
    """
    
    def __init__(
        self,
        order: ServiceOrder,
        expected: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa item do dataset.
        
        Args:
            order: Ordem de serviço
            expected: Valores esperados (opcional)
        """
        self.order = order
        self.expected = expected or {}
    
    def __repr__(self) -> str:
        return f"DatasetItem(order_id={self.order.order_id})"


class DatasetManager:
    """
    Gerenciador de datasets para avaliação.
    
    Carrega datasets de arquivos JSON e fornece
    interface para iteração e análise.
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            dataset_path: Caminho para arquivo JSON do dataset
        """
        self.dataset_path = dataset_path
        self.items: List[DatasetItem] = []
        
        if dataset_path:
            self.load(dataset_path)
    
    def load(self, path: str) -> None:
        """
        Carrega dataset de um arquivo JSON.
        
        Formato esperado:
        [
            {
                "order_id": "...",
                "description": "...",
                "requester": "...",
                "location": "...",
                "expected": {
                    "classificacao": "...",
                    "criticidade": "...",
                    ...
                }
            },
            ...
        ]
        
        Args:
            path: Caminho do arquivo JSON
        """
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset não encontrado: {path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.items = []
        
        for item in data:
            # Extrai campos da ordem
            order = ServiceOrder(
                order_id=item.get("order_id", ""),
                description=item.get("description", ""),
                requester=item.get("requester"),
                location=item.get("location")
            )
            
            # Extrai valores esperados
            expected = item.get("expected", {})
            
            self.items.append(DatasetItem(order, expected))
    
    def get_orders(self) -> List[ServiceOrder]:
        """
        Retorna lista de ordens de serviço do dataset.
        
        Returns:
            List[ServiceOrder]: Ordens do dataset
        """
        return [item.order for item in self.items]
    
    def get_item(self, order_id: str) -> Optional[DatasetItem]:
        """
        Busca um item pelo ID da ordem.
        
        Args:
            order_id: ID da ordem
            
        Returns:
            DatasetItem ou None: Item encontrado ou None
        """
        for item in self.items:
            if item.order.order_id == order_id:
                return item
        return None
    
    def __len__(self) -> int:
        """Retorna quantidade de itens no dataset."""
        return len(self.items)
    
    def __iter__(self):
        """Permite iteração sobre os itens."""
        return iter(self.items)
    
    def __getitem__(self, index: int) -> DatasetItem:
        """Permite acesso por índice."""
        return self.items[index]
    
    def filter_by_expected(
        self,
        field: str,
        value: str
    ) -> List[DatasetItem]:
        """
        Filtra itens por valor esperado.
        
        Args:
            field: Campo a filtrar (ex: "classificacao")
            value: Valor esperado
            
        Returns:
            List[DatasetItem]: Itens filtrados
        """
        return [
            item for item in self.items
            if item.expected.get(field) == value
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do dataset.
        
        Returns:
            dict: Estatísticas
        """
        if not self.items:
            return {}
        
        stats = {
            "total_items": len(self.items),
            "with_expected": sum(1 for item in self.items if item.expected),
            "classifications": {},
            "criticalities": {},
            "urgencies": {}
        }
        
        # Conta distribuição de valores esperados
        for item in self.items:
            if not item.expected:
                continue
            
            # Classificação
            classif = item.expected.get("classificacao")
            if classif:
                stats["classifications"][classif] = \
                    stats["classifications"].get(classif, 0) + 1
            
            # Criticidade
            critic = item.expected.get("criticidade")
            if critic:
                stats["criticalities"][critic] = \
                    stats["criticalities"].get(critic, 0) + 1
            
            # Urgência
            urgency = item.expected.get("urgencia")
            if urgency:
                stats["urgencies"][urgency] = \
                    stats["urgencies"].get(urgency, 0) + 1
        
        return stats
    
    def export_subset(
        self,
        output_path: str,
        indices: Optional[List[int]] = None,
        order_ids: Optional[List[str]] = None
    ) -> None:
        """
        Exporta subset do dataset.
        
        Args:
            output_path: Caminho de saída
            indices: Índices dos itens (opcional)
            order_ids: IDs das ordens (opcional)
        """
        if indices is not None:
            subset = [self.items[i] for i in indices if i < len(self.items)]
        elif order_ids is not None:
            subset = [item for item in self.items if item.order.order_id in order_ids]
        else:
            subset = self.items
        
        # Converte para formato JSON
        data = []
        for item in subset:
            data.append({
                "order_id": item.order.order_id,
                "description": item.order.description,
                "requester": item.order.requester,
                "location": item.order.location,
                "expected": item.expected
            })
        
        # Salva
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
