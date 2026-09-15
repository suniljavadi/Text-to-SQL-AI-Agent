# Enterprise Text-to-SQL AI Agent

**Status: Completed portfolio implementation with synthetic data and deterministic fallback mode**

A production-style portfolio project that converts business questions into safe, explainable SQL over synthetic sales data. It demonstrates SQL Server/T-SQL thinking, dimensional modeling, ETL-style seeding, RAG, tool-calling agents, FastAPI, Streamlit, PostgreSQL, Docker, evaluation, and defensive SQL engineering.

## Business Problem
Business users often need answers from operational and warehouse data but cannot write SQL. A useful assistant must understand business definitions, retrieve relevant schema, generate SQL, validate it, execute only read-only statements, and explain the result without inventing values.

## Solution
The agent follows: question -> schema retrieval -> intent-aware SQL generation -> AST and policy validation -> bounded execution -> result analysis. The default mode is deterministic and works without an API key. An OpenAI-compatible provider can be added behind the same service boundary for production experiments.

## Architecture
```mermaid
flowchart LR
 U[User] --> UI[Streamlit UI]
 UI --> API[FastAPI]
 API --> A[TextToSQL Agent]
 A --> R[RAG Schema Retriever]
 A --> G[SQL Generator]
 G --> V[SQL Guard]
 V --> E[Read-only Executor]
 E --> DB[(PostgreSQL)]
 E --> P[Pandas-style Result Analysis]
 P --> API
```

## Stack
Python 3.11+, FastAPI, Streamlit, PostgreSQL, SQLAlchemy, Pydantic, sqlglot, optional OpenAI-compatible API, deterministic hashed-vector retrieval, pytest, Docker Compose.

## Features
- Synthetic customers, products, orders, order items, employees, and departments.
- Constraints, foreign keys, indexes, and deterministic seed data.
- Schema, relationships, KPI definitions, and business glossary retrieval.
- Agent tools: `get_schema`, `search_schema`, `get_business_definition`, `generate_sql`, `validate_sql`, `execute_sql`, `explain_sql`, `analyze_result`.
- SQL parser validation, blocked mutation keywords, comment and multi-statement rejection, row limits, retry limits, request IDs, structured logs, and error recovery.
- FastAPI API and screenshot-ready Streamlit interface.
- 50-question evaluation set covering joins, grouping, ranking, filtering, ambiguity, and invalid input.

## Workflow
1. Validate and bound the natural-language request.
2. Retrieve relevant tables, relationships, definitions, and KPIs.
3. Generate a SQL candidate using known safe templates in fallback mode.
4. Parse and validate the candidate with sqlglot.
5. Execute through SQLAlchemy with a maximum row count.
6. Analyze structured rows and return SQL, context, timings, and explanation.
7. Retry only up to `MAX_RETRIES`; unsafe or unsupported requests fail clearly.

## SQL Security
Generated SQL is never executed directly. Only SELECT-like statements are accepted. INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, MERGE, EXEC, CREATE, comments, multiple statements, unsafe functions, oversized queries, and missing SELECT structures are rejected. Docker credentials are demo-only and should be replaced for real deployments with a least-privilege database role and network controls.

## API
- `GET /health`
- `GET /api/v1/schema`
- `POST /api/v1/validate-sql` with `{ "sql": "SELECT ..." }`
- `POST /api/v1/query` with `{ "question": "Show the top products by revenue." }`

## Screenshots
Add project screenshots to `docs/screenshots/` after starting Streamlit:
- `docs/screenshots/query-result.png`
- `docs/screenshots/sql-validation.png`
- `docs/screenshots/schema-context.png`

## Installation
```powershell
git clone <your-repository-url>
cd text-to-sql-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH = (Get-Location).Path
python database/seed_data.py
```

For a local SQLite setup, the default database is `sqlite:///./textsql.db`. For PostgreSQL, set `DATABASE_URL=postgresql+psycopg://user:password@host:5432/database`.

## Run
```powershell
$env:PYTHONPATH = (Get-Location).Path
uvicorn app.main:app --reload
streamlit run streamlit_app/app.py
```
Open `http://localhost:8501` and API docs at `http://localhost:8000/docs`.

## Docker
```powershell
docker compose up --build
```
The API is at `http://localhost:8000`, Streamlit at `http://localhost:8501`, and PostgreSQL at port `5432`.

## Tests and Evaluation
```powershell
$env:PYTHONPATH = (Get-Location).Path
pytest -q
python evaluation/run_evaluation.py
```
The evaluator writes `evaluation/evaluation_report.json` with validity, execution accuracy, semantic match, retrieval quality, latency, and failure rate. Results depend on the deterministic seed and runtime.

## Configuration
Copy `.env.example` to `.env`. Important settings include `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `USE_LLM`, `MAX_ROWS`, `QUERY_TIMEOUT_SECONDS`, and `MAX_RETRIES`. No secret is required for fallback mode.

## Example Questions
- Show the top 10 customers by revenue.
- What is total revenue from completed orders?
- Compare revenue by product category.
- What is the average order value?
- What is average salary by department?
- What is the weather today? (safe refusal)

## Example Output
```text
Answer: The result is 123456.0 across the requested scope.
SQL: SELECT SUM(oi.quantity * oi.unit_price) AS revenue ...
Validation: valid read-only SQL
Rows: [{"revenue": 123456.0}]
```
Values are generated from synthetic records and are not fixed contract values.

## Limitations and Future Improvements
The fallback generator intentionally supports a bounded set of analytical patterns. Production work would add a provider adapter with structured tool calling, true embedding models and FAISS/pgvector, SQL Server dialect support, query cancellation, row-level security, richer semantic evaluation, tracing with OpenTelemetry, authentication, and a formal migration system.

## GitHub Publishing
```powershell
git init
git add .
git commit -m "Build enterprise text-to-SQL AI agent"
git branch -M main
git remote add origin https://github.com/suniljavadi/Text-to-SQL-AI-Agent.git
git push -u origin main
```

## Resume Bullets
- Built a production-style Text-to-SQL agent with schema-aware RAG, business KPI definitions, SQL AST validation, bounded execution, retry recovery, and structured observability.
- Designed synthetic dimensional sales data with PostgreSQL constraints, indexes, read-only API workflows, Docker Compose, and a Streamlit analytics experience.
- Created a 50-question evaluation harness measuring SQL validity, execution accuracy, semantic correctness, retrieval quality, latency, and failure rate.

## Interview Explanation
**60 seconds:** This project turns natural language into safe business analytics. It retrieves relevant schema and KPI definitions, generates SQL through a deterministic fallback or optional OpenAI-compatible provider, validates the SQL with an AST parser and denylist, executes only bounded read queries, and returns results with context, explanation, timing, and audit-friendly request IDs. PostgreSQL, FastAPI, Streamlit, Docker, and pytest make it deployable and testable.

**5 minutes:** Start with the business problem: users need trusted answers, not merely syntactically valid SQL. The catalog represents schema, joins, revenue, active customers, AOV, and margin. Retrieval narrows context before generation. The agent then uses tools and a bounded retry loop. The security layer is the most important boundary: parse SQL, permit only read roots, reject mutations, comments, multiple statements, dangerous functions, and oversized input, then apply a row limit at execution. Results are structured and analyzed without inventing values. The API exposes validation separately from querying, while Streamlit makes the workflow inspectable for a portfolio audience. Evaluation separates validity from execution and semantic correctness, which prevents a misleading high score from syntax-only tests.

## Interview Questions and Answers
**Why validate generated SQL?** LLM output is untrusted text. Validation creates a policy boundary before database access.

**Why use business definitions in RAG?** Column names do not encode metrics such as completed revenue or active customer semantics.

**How do you prevent infinite retries?** `MAX_RETRIES` is configurable and every failure returns a safe explanation after the limit.

**How do you prevent SQL injection?** The user does not concatenate SQL into execution; generated SQL is parsed and checked, comments and multiple statements are rejected, and execution is bounded.

**Why keep a deterministic fallback?** It makes demos, tests, and evaluation reproducible and prevents API-key dependency.

**What would you change for production?** Add authentication, a true read-only role, query cancellation, provider tool calling, vector storage, OpenTelemetry, row-level security, and stronger semantic benchmarks.
