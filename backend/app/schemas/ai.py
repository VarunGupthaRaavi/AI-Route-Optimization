import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# -------------------------------------------------------------------
# 1. AI Chat & Copilot Schemas
# -------------------------------------------------------------------
class AIChatRequest(BaseModel):
    prompt: str = Field(..., description="User query or instruction for AI Copilot")
    context: Optional[str] = Field(default=None, description="Optional logistics context or document excerpt")
    include_rag: bool = Field(default=True, description="Whether to perform RAG retrieval before answering")


class AIChatResponse(BaseModel):
    reply: str = Field(..., description="AI Copilot response string")
    rag_sources: List[str] = Field(default_factory=list, description="Retrieved RAG source titles")
    tokens_used: int = Field(default=0, description="Estimated token count")


# -------------------------------------------------------------------
# 2. Predictive ETA & Dynamic Reroute Schemas
# -------------------------------------------------------------------
class ETAPredictRequest(BaseModel):
    pickup_lat: float = Field(..., description="Origin pickup latitude")
    pickup_lng: float = Field(..., description="Origin pickup longitude")
    delivery_lat: float = Field(..., description="Destination delivery latitude")
    delivery_lng: float = Field(..., description="Destination delivery longitude")
    traffic_factor: float = Field(default=1.0, ge=0.5, le=3.0, description="Traffic congestion factor multiplier")
    weather_condition: str = Field(default="CLEAR", description="Weather condition (CLEAR, RAIN, SNOW, FOG)")
    stop_service_minutes: int = Field(default=10, description="Package dropoff service overhead in minutes")


class ETAPredictResponse(BaseModel):
    estimated_distance_km: float = Field(..., description="Calculated Haversine distance in kilometers")
    estimated_duration_minutes: float = Field(..., description="Predicted travel + service duration in minutes")
    traffic_delay_minutes: float = Field(..., description="Added delay from traffic congestion")
    weather_delay_minutes: float = Field(..., description="Added delay from weather conditions")
    eta_timestamp: str = Field(..., description="Calculated ISO 8601 estimated time of arrival")


class DynamicRerouteRequest(BaseModel):
    route_id: uuid.UUID = Field(..., description="ID of active route to dynamically adjust")
    delayed_stop_sequence: int = Field(..., description="Stop sequence experiencing delay or blockage")
    delay_reason: str = Field(..., description="Reason for rerouting (TRAFFIC_BLOCK, CANCELLATION, WEATHER)")


# -------------------------------------------------------------------
# 3. Enterprise RAG & Vector Search Schemas
# -------------------------------------------------------------------
class RAGDocumentUpload(BaseModel):
    title: str = Field(..., description="Document title or manual name")
    file_type: str = Field(default="PDF", description="Format (PDF, TXT, MD)")
    author: Optional[str] = Field(default="Logistics Ops", description="Authoring department")
    content: str = Field(..., description="Full text document content to chunk and vectorize")


class RAGDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    file_type: str
    chunk_count: int
    created_at: str


class RAGVectorQuery(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of top relevant chunks to retrieve")


class RAGQueryResult(BaseModel):
    document_title: str
    chunk_index: int
    content: str
    similarity_score: float


# -------------------------------------------------------------------
# 4. Multi-Agent Route Planning Schemas
# -------------------------------------------------------------------
class MultiAgentPlanRequest(BaseModel):
    delivery_ids: List[uuid.UUID] = Field(..., description="List of pending delivery IDs to plan")
    vehicle_ids: Optional[List[uuid.UUID]] = Field(default=None, description="Optional list of vehicle IDs")
    max_driving_hours: float = Field(default=8.0, description="Maximum allowed driver shift hours")


class AgentInsight(BaseModel):
    agent_name: str
    summary: str
    decisions: List[str]


class MultiAgentPlanResponse(BaseModel):
    plan_id: uuid.UUID
    agent_insights: List[AgentInsight]
    recommended_stops_order: List[uuid.UUID]
    total_estimated_distance_km: float
    total_estimated_duration_minutes: float
    efficiency_score_pct: float
