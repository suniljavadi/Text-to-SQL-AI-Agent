# Evaluation Guide

The public golden fixture is `golden-dataset-v1.jsonl`. It is synthetic and safe to share.

## Metrics

Track SQL validity, unsafe-query rejection, execution success, semantic correctness, clarification behavior, query latency, retries, and timeout rate.

## Observability

Record request ID, application and schema version, validation result, execution duration, row count, and error class. Never log credentials or unrestricted result data.

## Release Checks

Run security cases first, then semantic cases, and compare latency and failure rate with the previous version. A passing HTTP check does not prove semantic correctness.
