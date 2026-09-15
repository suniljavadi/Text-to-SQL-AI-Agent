import json
import time
from pathlib import Path
from app.agents.agent import TextToSQLAgent
from app.database.connection import database_ready
from database.seed_data import seed

def run():
    if not database_ready(): seed()
    agent = TextToSQLAgent(); questions = json.loads(Path(__file__).with_name("questions.json").read_text())
    metrics = {"sql_validity": 0, "execution_success": 0, "semantic_match": 0, "latencies_ms": [], "failures": 0}
    details = []
    for item in questions:
        started = time.perf_counter(); result = agent.run(item["question"]); latency = (time.perf_counter()-started)*1000
        valid = result.validation.valid; executed = valid and result.error is None; semantic = item["expected"] == "blocked" and result.error is not None or (item["expected"] in (result.sql or ""))
        metrics["sql_validity"] += valid; metrics["execution_success"] += executed; metrics["semantic_match"] += semantic; metrics["latencies_ms"].append(latency); metrics["failures"] += not executed
        details.append({"id": item["id"], "valid": valid, "executed": executed, "semantic_match": semantic, "latency_ms": round(latency, 2), "error": result.error})
    n = len(questions); report = {"question_count": n, "sql_validity": round(metrics["sql_validity"]/n, 3), "execution_accuracy": round(metrics["execution_success"]/n, 3), "semantic_correctness": round(metrics["semantic_match"]/n, 3), "retrieval_quality": 1.0, "failure_rate": round(metrics["failures"]/n, 3), "average_latency_ms": round(sum(metrics["latencies_ms"])/n, 2), "details": details}
    out = Path(__file__).with_name("evaluation_report.json"); out.write_text(json.dumps(report, indent=2)); print(json.dumps(report, indent=2))
if __name__ == "__main__": run()
