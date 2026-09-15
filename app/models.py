from typing import Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

class ValidationRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=10000)

class ValidationResponse(BaseModel):
    valid: bool
    normalized_sql: str | None = None
    errors: list[str] = []
    warnings: list[str] = []

class QueryResponse(BaseModel):
    request_id: str
    question: str
    answer: str
    sql: str | None
    validation: ValidationResponse
    rows: list[dict[str, Any]] = []
    columns: list[str] = []
    explanation: str = ""
    context: list[dict[str, Any]] = []
    execution_ms: float = 0
    error: str | None = None

class HealthResponse(BaseModel):
    status: str
    database: str
