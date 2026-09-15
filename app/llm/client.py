from openai import OpenAI
from app.config import get_settings

class OpenAICompatibleClient:
    """Optional provider adapter. Fallback mode remains the default for reproducibility."""
    def __init__(self):
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        self.client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        self.model = settings.openai_model

    def generate_sql(self, question: str, context: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": "Generate exactly one safe PostgreSQL SELECT query. Never mutate data. Use only tables and definitions in the supplied context."},
                {"role": "user", "content": f"Question: {question}\nContext: {context}"},
            ],
        )
        return response.choices[0].message.content or ""
