
import os
from pathlib import Path

import cohere
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class EmbeddingService:

    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER")
        self.model = os.getenv("EMBEDDING_MODEL")

        if self.provider != "cohere":
            raise ValueError(
                f"Unsupported embedding provider: {self.provider}"
            )

        api_key = os.getenv("COHERE_API_KEY")

        if not api_key:
            raise ValueError("COHERE_API_KEY is missing")

        self.client = cohere.ClientV2(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document",
            embedding_types=["float"]
        )

        return response.embeddings.float_

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="search_query",
            embedding_types=["float"]
        )

        return response.embeddings.float_[0]
    
    
def company_to_text(company: dict) -> str:
    """
    Convert a company record into searchable text.
    """

    fields = [
        f"Company Name: {company.get('name', '')}",
        f"Sector: {company.get('sector', '')}",
        f"Headquarters: {company.get('headquarters', '')}",
        f"Founded: {company.get('founded', '')}",
        f"Valuation: {company.get('valuation_billion', '')} billion USD",
        f"Description: {company.get('description', '')}"
    ]

    return "\n".join(
        field for field in fields
        if field.split(": ", 1)[-1].strip()
    )


    