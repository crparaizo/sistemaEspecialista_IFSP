"""
API REST do Sistema Triador.

Expõe endpoints para triagem de ordens de serviço
via HTTP usando FastAPI.
"""

from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..models.order import ServiceOrder
from ..models.result import TriageResult
from ..triage.pipeline import TriagePipeline, TriagePipelineError
from ..config import get_settings


# Inicializa aplicação FastAPI
app = FastAPI(
    title="Sistema Triador de OS - Arquitetura Neurossimbólica",
    description="""
    Sistema de triagem de ordens de serviço de manutenção industrial
    utilizando arquitetura híbrida neurossimbólica:
    
    - **Camada Conexionista**: LLM/SLM para extração de informações
    - **Camada Simbólica**: Sistema Especialista para decisões determinísticas
    
    Desenvolvido para IFSP - Pós-Graduação em Controle e Automação
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurações
settings = get_settings()

# Pipeline global (singleton)
pipeline: TriagePipeline = TriagePipeline()

# CORS (se necessário para frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELOS DE REQUEST/RESPONSE
# ============================================================

class TriageRequest(BaseModel):
    """Request para triagem de OS."""
    
    order_id: str = Field(
        ...,
        description="Identificador único da ordem de serviço",
        examples=["OS-001"]
    )
    
    description: str = Field(
        ...,
        min_length=10,
        description="Descrição do problema em linguagem natural",
        examples=["Motor da esteira 03 apresenta vibração excessiva"]
    )
    
    requester: str | None = Field(
        None,
        description="Solicitante da OS",
        examples=["João Silva"]
    )
    
    location: str | None = Field(
        None,
        description="Localização ou setor",
        examples=["Linha 3"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "OS-001",
                "description": "Motor da esteira 03 apresenta vibração excessiva e ruído durante operação",
                "requester": "Supervisor Produção",
                "location": "Linha 3 - Setor A"
            }
        }


class BatchTriageRequest(BaseModel):
    """Request para triagem em lote."""
    
    orders: List[TriageRequest] = Field(
        ...,
        description="Lista de ordens de serviço a processar",
        min_length=1
    )


class HealthResponse(BaseModel):
    """Response do health check."""
    
    status: str
    timestamp: datetime
    version: str
    llm_available: bool
    llm_provider: str
    llm_model: str


class ExplainResponse(BaseModel):
    """Response detalhada com explicação."""
    
    triage_result: TriageResult
    explanation: Dict[str, Any]


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raiz com informações básicas da API.
    """
    return {
        "name": "Sistema Triador de OS",
        "version": "1.0.0",
        "architecture": "Hybrid Neurosymbolic",
        "institution": "IFSP - Pós-Graduação em Controle e Automação",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "triage": "/triage",
            "batch": "/triage/batch",
            "explain": "/triage/explain",
            "info": "/info"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Verifica o status do sistema e disponibilidade da LLM.
    """
    validation = pipeline.validate_provider()
    
    return HealthResponse(
        status="healthy" if validation["available"] else "degraded",
        timestamp=datetime.now(),
        version="1.0.0",
        llm_available=validation["available"],
        llm_provider=validation["provider"],
        llm_model=validation["model"]
    )


@app.get("/info", tags=["System"])
async def get_info():
    """
    Retorna informações detalhadas sobre o pipeline.
    """
    return pipeline.get_pipeline_info()


@app.post("/triage", response_model=TriageResult, tags=["Triage"])
async def triage_order(request: TriageRequest):
    """
    Processa uma ordem de serviço e retorna a triagem.
    
    O sistema executa:
    1. Extração de informações com LLM
    2. Transformação em fatos
    3. Aplicação de regras do sistema especialista
    4. Retorno da decisão com justificativa
    """
    try:
        # Cria ServiceOrder a partir do request
        order = ServiceOrder(
            order_id=request.order_id,
            description=request.description,
            requester=request.requester,
            location=request.location
        )
        
        # Processa com pipeline
        result = pipeline.process(order)
        
        return result
        
    except TriagePipelineError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar triagem: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}"
        )


@app.post("/triage/batch", response_model=List[TriageResult], tags=["Triage"])
async def triage_batch(request: BatchTriageRequest):
    """
    Processa múltiplas ordens de serviço em lote.
    
    Útil para processar várias OS de uma vez.
    Retorna lista de resultados na mesma ordem das entradas.
    """
    try:
        # Converte requests em ServiceOrders
        orders = [
            ServiceOrder(
                order_id=req.order_id,
                description=req.description,
                requester=req.requester,
                location=req.location
            )
            for req in request.orders
        ]
        
        # Processa em batch
        results = pipeline.process_batch(orders)
        
        return results
        
    except TriagePipelineError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar lote: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}"
        )


@app.post("/triage/explain", tags=["Triage"])
async def explain_triage(request: TriageRequest):
    """
    Processa uma OS e retorna explicação detalhada da decisão.
    
    Útil para debugging e entendimento do sistema.
    Mostra:
    - Fatos extraídos e derivados
    - Regras aplicadas
    - Justificativa da decisão
    """
    try:
        # Cria ServiceOrder
        order = ServiceOrder(
            order_id=request.order_id,
            description=request.description,
            requester=request.requester,
            location=request.location
        )
        
        # Gera explicação
        explanation = pipeline.explain_decision(order)
        
        return explanation
        
    except TriagePipelineError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar explicação: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================
# FUNÇÃO PARA EXECUTAR A API
# ============================================================

def run_api():
    """
    Executa a API com Uvicorn.
    
    Para uso direto ou via script.
    """
    import uvicorn
    
    uvicorn.run(
        "src.api.routes:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_api()
