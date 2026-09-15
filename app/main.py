import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database.connection import database_ready
from app.logging_config import configure_logging
from app.models import QueryRequest, QueryResponse, ValidationRequest, ValidationResponse, HealthResponse
from app.security.sql_guard import validate_sql
from app.rag.retriever import SchemaRetriever
from app.agents.agent import TextToSQLAgent
from app.tools.sql_tools import get_schema

configure_logging(get_settings().log_level)
logger = logging.getLogger(__name__)
app = FastAPI(title="Enterprise Text-to-SQL AI Agent", version="1.0.0")
retriever = SchemaRetriever()
agent = TextToSQLAgent(retriever)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed request_id=%s", request_id)
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    response.headers["X-Request-ID"] = request_id
    logger.info("request_completed request_id=%s path=%s duration_ms=%.2f", request_id, request.url.path, (time.perf_counter()-started)*1000)
    return response

@app.get("/health", response_model=HealthResponse)
def health():
    ready = database_ready()
    return HealthResponse(status="ok" if ready else "degraded", database="ready" if ready else "unavailable")

@app.get("/api/v1/schema")
def schema(): return {"tables": get_schema()}

@app.post("/api/v1/validate-sql", response_model=ValidationResponse)
def validate_endpoint(request: ValidationRequest):
    result = validate_sql(request.sql)
    return ValidationResponse(valid=result.valid, normalized_sql=result.normalized_sql, errors=result.errors, warnings=result.warnings)

@app.post("/api/v1/query", response_model=QueryResponse)
def query(request: QueryRequest, raw_request: Request):
    request_id = raw_request.state.request_id
    logger.info("query_started request_id=%s question=%s", request_id, request.question[:1000])
    result = agent.run(request.question, get_settings().max_retries)
    logger.info("query_result request_id=%s sql=%s valid=%s execution_ms=%.2f row_count=%s error=%s", request_id, result.sql, result.validation.valid, result.execution_ms, len(result.rows), result.error)
    return QueryResponse(request_id=request_id, question=request.question, answer=result.answer, sql=result.sql, validation=ValidationResponse(valid=result.validation.valid, normalized_sql=result.validation.normalized_sql, errors=result.validation.errors, warnings=result.validation.warnings), rows=result.rows, columns=result.columns, explanation=result.explanation, context=result.context, execution_ms=result.execution_ms, error=result.error)
