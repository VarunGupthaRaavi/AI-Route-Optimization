from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    DynamicRerouteRequest,
    ETAPredictRequest,
    ETAPredictResponse,
    MultiAgentPlanRequest,
    MultiAgentPlanResponse,
    RAGDocumentResponse,
    RAGDocumentUpload,
    RAGQueryResult,
    RAGVectorQuery,
)
from app.schemas.base import ResponseModel
from app.services.ai_gemini import GeminiAIService, LOGISTICS_COPILOT_PROMPT
from app.services.eta_service import ETAPredictionService
from app.services.multi_agent import MultiAgentPlanningEngine
from app.services.rag_service import RAGService

router = APIRouter()


@router.post(
    "/chat",
    response_model=ResponseModel[AIChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Interactive AI Logistics Copilot Chat Assistant"
)
async def ai_chat_copilot(
    payload: AIChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[AIChatResponse]:
    request_id = getattr(request.state, "request_id", None)
    rag_sources = []
    context_text = payload.context or ""

    # Perform RAG Retrieval if enabled
    if payload.include_rag:
        rag_service = RAGService(session=db)
        search_results = await rag_service.search_knowledge_base(query=payload.prompt, top_k=2)
        if search_results:
            rag_sources = list(set([r.document_title for r in search_results]))
            context_text += "\n" + "\n".join([f"[{r.document_title}]: {r.content}" for r in search_results])

    gemini = GeminiAIService()
    full_prompt = LOGISTICS_COPILOT_PROMPT.format(
        rag_context=context_text or "No external context required.",
        user_prompt=payload.prompt
    )

    reply_text = await gemini.generate_content(full_prompt)

    response_data = AIChatResponse(
        reply=reply_text,
        rag_sources=rag_sources,
        tokens_used=len(full_prompt.split()) + len(reply_text.split())
    )

    return ResponseModel(
        success=True,
        data=response_data,
        message="AI Copilot response generated successfully.",
        request_id=request_id
    )


@router.post(
    "/predict-eta",
    response_model=ResponseModel[ETAPredictResponse],
    status_code=status.HTTP_200_OK,
    summary="Predictive ETA & Traffic Delay Calculation"
)
async def predict_eta(
    payload: ETAPredictRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[ETAPredictResponse]:
    request_id = getattr(request.state, "request_id", None)
    eta_service = ETAPredictionService(session=db)
    eta_data = await eta_service.predict_eta(payload)
    return ResponseModel(
        success=True,
        data=eta_data,
        message="Predictive ETA calculated successfully.",
        request_id=request_id
    )


@router.post(
    "/reroute",
    response_model=ResponseModel[dict],
    status_code=status.HTTP_200_OK,
    summary="Dynamic Route Adjustment on Traffic Delays or Closures"
)
async def dynamic_reroute(
    payload: DynamicRerouteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[dict]:
    request_id = getattr(request.state, "request_id", None)
    eta_service = ETAPredictionService(session=db)
    result = await eta_service.dynamically_reroute(payload)
    return ResponseModel(
        success=True,
        data=result,
        message="Dynamic route adjustment completed.",
        request_id=request_id
    )


@router.post(
    "/rag/upload",
    response_model=ResponseModel[RAGDocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Document into Enterprise RAG Vector Base"
)
async def upload_rag_document(
    payload: RAGDocumentUpload,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[RAGDocumentResponse]:
    request_id = getattr(request.state, "request_id", None)
    rag_service = RAGService(session=db)
    doc = await rag_service.ingest_document(payload)
    return ResponseModel(
        success=True,
        data=RAGDocumentResponse(
            id=doc.id,
            title=doc.title,
            file_type=doc.file_type,
            chunk_count=doc.chunk_count,
            created_at=doc.created_at.isoformat()
        ),
        message="Document ingested and vectorized into RAG knowledge base.",
        request_id=request_id
    )


@router.post(
    "/rag/query",
    response_model=ResponseModel[List[RAGQueryResult]],
    status_code=status.HTTP_200_OK,
    summary="Execute Semantic Vector Cosine Similarity Search"
)
async def query_rag_vector_base(
    payload: RAGVectorQuery,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[List[RAGQueryResult]]:
    request_id = getattr(request.state, "request_id", None)
    rag_service = RAGService(session=db)
    results = await rag_service.search_knowledge_base(query=payload.query, top_k=payload.top_k)
    return ResponseModel(
        success=True,
        data=results,
        message=f"Retrieved {len(results)} relevant vector knowledge passages.",
        request_id=request_id
    )


@router.post(
    "/agents/plan",
    response_model=ResponseModel[MultiAgentPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Multi-Agent Route Planning Engine Orchestration"
)
async def multi_agent_planning(
    payload: MultiAgentPlanRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[MultiAgentPlanResponse]:
    request_id = getattr(request.state, "request_id", None)
    engine = MultiAgentPlanningEngine(session=db)
    plan_data = await engine.execute_multi_agent_planning(payload)
    return ResponseModel(
        success=True,
        data=plan_data,
        message="Multi-agent route planning completed.",
        request_id=request_id
    )
