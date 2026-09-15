import re
import time
import logging
from dataclasses import dataclass
from app.rag.retriever import SchemaRetriever
from app.tools.sql_tools import execute_sql, explain_sql, analyze_result
from app.security.sql_guard import validate_sql
from app.config import get_settings

logger = logging.getLogger(__name__)
@dataclass
class AgentResult:
    sql: str | None
    validation: object
    rows: list[dict]
    columns: list[str]
    answer: str
    explanation: str
    context: list[dict]
    execution_ms: float
    error: str | None = None

class TextToSQLAgent:
    def __init__(self, retriever=None): self.retriever = retriever or SchemaRetriever()
    def generate_sql(self, question: str, context: list[dict]) -> str:
        if get_settings().use_llm and get_settings().openai_api_key:
            from app.llm.client import OpenAICompatibleClient
            return OpenAICompatibleClient().generate_sql(question, context)
        q = question.lower()
        if any(word in q for word in ["weather", "joke", "password", "delete", "insert", "update"]):
            raise ValueError("I can only answer safe analytical questions about the synthetic business database.")
        if "top" in q and "product" in q:
            return "SELECT p.product_name, SUM(oi.quantity * oi.unit_price) AS revenue FROM products p JOIN order_items oi ON oi.product_id = p.product_id JOIN orders o ON o.order_id = oi.order_id WHERE o.status = 'Completed' GROUP BY p.product_name ORDER BY revenue DESC LIMIT 10"
        if "customer" in q and ("revenue" in q or "sales" in q):
            return "SELECT c.customer_name, SUM(oi.quantity * oi.unit_price) AS revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items oi ON oi.order_id = o.order_id WHERE o.status = 'Completed' GROUP BY c.customer_name ORDER BY revenue DESC LIMIT 10"
        if "department" in q and "salary" in q:
            return "SELECT d.name AS department, ROUND(AVG(e.salary), 2) AS average_salary FROM departments d JOIN employees e ON e.department_id = d.department_id GROUP BY d.name ORDER BY average_salary DESC"
        if "category" in q and ("revenue" in q or "sales" in q):
            return "SELECT p.category, SUM(oi.quantity * oi.unit_price) AS revenue FROM products p JOIN order_items oi ON oi.product_id = p.product_id JOIN orders o ON o.order_id = oi.order_id WHERE o.status = 'Completed' GROUP BY p.category ORDER BY revenue DESC"
        if "average order" in q or "aov" in q:
            return "SELECT ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS average_order_value FROM orders o JOIN order_items oi ON oi.order_id = o.order_id WHERE o.status = 'Completed'"
        if "revenue" in q or "total sales" in q:
            return "SELECT SUM(oi.quantity * oi.unit_price) AS revenue FROM orders o JOIN order_items oi ON oi.order_id = o.order_id WHERE o.status = 'Completed'"
        if "list" in q or "show" in q or "customers" in q:
            return "SELECT customer_id, customer_name, city, segment, signup_date FROM customers ORDER BY customer_id LIMIT 50"
        raise ValueError("The question is ambiguous. Please specify a business metric, table, or dimension.")

    def run(self, question: str, max_retries: int = 2) -> AgentResult:
        context = self.retriever.search(question)
        started = time.perf_counter(); last_error = None; sql = None
        for attempt in range(max_retries + 1):
            try:
                sql = self.generate_sql(question, context)
                validation = validate_sql(sql)
                if not validation.valid: raise ValueError("; ".join(validation.errors))
                rows, columns, execution_ms = execute_sql(sql)
                return AgentResult(sql, validation, rows, columns, analyze_result(rows, question), explain_sql(sql), context, execution_ms)
            except Exception as exc:
                last_error = str(exc)
                logger.warning("agent_attempt_failed attempt=%s error=%s", attempt + 1, last_error)
                if attempt >= max_retries: break
                time.sleep(0.01)
        validation = validate_sql(sql) if sql else validate_sql("SELECT 1")
        return AgentResult(sql, validation, [], [], "I could not safely answer this question.", "", context, (time.perf_counter()-started)*1000, last_error)
