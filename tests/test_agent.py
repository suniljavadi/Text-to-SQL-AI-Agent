from app.agents.agent import TextToSQLAgent

def test_agent_generates_and_executes_revenue():
    result = TextToSQLAgent().run("What is total revenue from completed orders?")
    assert result.validation.valid
    assert result.error is None
    assert result.rows[0]["revenue"] is not None

def test_agent_recovers_from_unsupported_question():
    result = TextToSQLAgent().run("What is the weather today?")
    assert result.error
    assert not result.rows
