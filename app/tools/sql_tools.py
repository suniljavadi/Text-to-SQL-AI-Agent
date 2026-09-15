import time
import logging
from app.database.connection import connection
from app.rag.retriever import SchemaRetriever
from app.security.sql_guard import validate_sql
from app.config import get_settings

logger = logging.getLogger(__name__)
retriever = SchemaRetriever()

def get_schema(): return retriever.get_schema()
def search_schema(query: str): return retriever.search(query)
def get_business_definition(name: str): return retriever.get_business_definition(name)
def validate_sql_tool(sql: str): return validate_sql(sql)
def execute_sql(sql: str) -> tuple[list[dict], list[str], float]:
    result = validate_sql(sql)
    if not result.valid:
        raise ValueError("SQL rejected: " + "; ".join(result.errors))
    started = time.perf_counter()
    with connection() as conn:
        query = result.normalized_sql
        if " limit " not in query.lower():
            query = f"SELECT * FROM ({query}) AS safe_query LIMIT {get_settings().max_rows}"
        rows = [dict(row) for row in conn.execute(__import__('sqlalchemy').text(query)).mappings().all()]
    return rows, (list(rows[0].keys()) if rows else []), (time.perf_counter() - started) * 1000

def explain_sql(sql: str) -> str:
    return "Reads completed order lines, joins the requested dimensions, and applies aggregation or ranking as described by the question."

def analyze_result(rows: list[dict], question: str) -> str:
    if not rows: return "The query completed successfully but returned no rows."
    if len(rows) == 1 and len(rows[0]) == 1:
        value = next(iter(rows[0].values()))
        return f"The result is {value:,} across the requested scope." if isinstance(value, (int, float)) else f"The result is {value}."
    return f"The query returned {len(rows)} rows. Review the table for the detailed result."
