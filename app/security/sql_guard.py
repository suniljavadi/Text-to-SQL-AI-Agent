import re
from dataclasses import dataclass
import sqlglot
from sqlglot import exp

BLOCKED = {"insert", "update", "delete", "drop", "alter", "truncate", "merge", "exec", "execute", "create", "grant", "revoke", "call"}
@dataclass
class GuardResult:
    valid: bool
    normalized_sql: str | None
    errors: list[str]
    warnings: list[str]

def validate_sql(sql: str) -> GuardResult:
    errors: list[str] = []
    warnings: list[str] = []
    candidate = sql.strip().rstrip(";").strip()
    if not candidate:
        return GuardResult(False, None, ["SQL cannot be empty."], [])
    if "--" in candidate or "/*" in candidate or "*/" in candidate:
        errors.append("SQL comments are not permitted.")
    if ";" in candidate:
        errors.append("Multiple SQL statements are not permitted.")
    try:
        tree = sqlglot.parse_one(candidate, read="postgres")
    except Exception as exc:
        return GuardResult(False, None, errors + [f"SQL parse error: {exc}"], warnings)
    root = tree.__class__.__name__.lower()
    if root not in {"select", "with", "union", "intersect", "except"}:
        errors.append("Only read-only SELECT queries are permitted.")
    upper = candidate.upper()
    for keyword in BLOCKED:
        if re.search(rf"\b{re.escape(keyword.upper())}\b", upper):
            errors.append(f"Blocked SQL operation: {keyword.upper()}.")
    if re.search(r"\b(pg_sleep|dblink|copy)\b", candidate, re.I):
        errors.append("Unsafe database function detected.")
    if not tree.find(exp.Select) and root != "with":
        errors.append("Query must contain a SELECT statement.")
    if len(candidate) > 10000:
        errors.append("SQL exceeds the maximum length.")
    if "LIMIT" not in upper:
        warnings.append("A row limit will be applied by the execution layer.")
    return GuardResult(not errors, tree.sql(dialect="postgres") if not errors else None, errors, warnings)
