from app.rag.retriever import SchemaRetriever

def test_retriever_finds_revenue_context():
    results = SchemaRetriever().search("revenue by product")
    assert results
    assert any(item["name"] in {"revenue", "products", "order_lines"} for item in results)

def test_business_definition():
    assert SchemaRetriever().get_business_definition("revenue")["type"] == "definition"
