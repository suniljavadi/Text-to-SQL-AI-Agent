import os
import requests
import streamlit as st

st.set_page_config(page_title="Enterprise Text-to-SQL", page_icon="SQL", layout="wide")
API_URL = os.getenv("API_URL", "http://localhost:8000")
DEMO_MODE = not os.getenv("API_URL")
st.title("Enterprise Text-to-SQL AI Agent")
st.caption("Synthetic business data | Safe read-only analytics")
if DEMO_MODE:
    st.info("Hosted demo mode: results use a deterministic synthetic response. Set API_URL to connect a FastAPI backend.")
question = st.text_area("Ask a business question", "Show me the top 10 customers by revenue.", height=90)
if st.button("Run analysis", type="primary") and question.strip():
    with st.spinner("Retrieving schema, validating SQL, and analyzing results..."):
        try:
            if DEMO_MODE:
                payload = {
                    "answer": "The top customers by revenue are Customer 001, Customer 002, and Customer 003 in this synthetic demo.",
                    "execution_ms": 2.4,
                    "rows": [
                        {"customer_name": "Customer 001", "revenue": 98500.0},
                        {"customer_name": "Customer 002", "revenue": 87300.0},
                        {"customer_name": "Customer 003", "revenue": 76100.0},
                    ],
                    "sql": "SELECT customer_name, SUM(revenue) AS revenue\nFROM customer_revenue\nGROUP BY customer_name\nORDER BY revenue DESC\nLIMIT 10;",
                    "validation": {"valid": True, "errors": []},
                    "explanation": "Deterministic sample response for the public portfolio demo.",
                    "context": {"mode": "demo", "source": "synthetic sample"},
                }
            else:
                response = requests.post(f"{API_URL}/api/v1/query", json={"question": question}, timeout=30)
                payload = response.json()
            if not DEMO_MODE and response.status_code >= 400: st.error(payload.get("detail", "Request failed"))
            else:
                st.subheader("Answer")
                st.write(payload["answer"])
                metric1, metric2 = st.columns(2)
                metric1.metric("Execution time", f"{payload['execution_ms']:.1f} ms")
                metric2.metric("Rows", len(payload["rows"]))
                st.subheader("Generated SQL")
                st.code(payload.get("sql") or "No SQL generated", language="sql")
                st.subheader("Validation")
                (st.success if payload["validation"]["valid"] else st.error)("Valid read-only SQL" if payload["validation"]["valid"] else "; ".join(payload["validation"]["errors"]))
                if payload["rows"]: st.dataframe(payload["rows"], use_container_width=True)
                with st.expander("Explanation and retrieved context"):
                    st.write(payload["explanation"])
                    st.json(payload["context"])
                if payload.get("error"): st.warning(payload["error"])
        except requests.RequestException as exc: st.error(f"API unavailable: {exc}")
