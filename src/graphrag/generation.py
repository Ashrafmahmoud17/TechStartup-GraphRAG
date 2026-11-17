
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class LLMGeneration:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing from .env")

        self.client = Groq(api_key=self.api_key)

    def generate_answer(self, question, context):
        if not context or not context.strip():
            return "No relevant information was found in the knowledge graph."

        system_prompt = """
        You are VentureLens, an AI assistant specialized in technology startups.

        Your task is to answer questions using ONLY the provided context.

        Rules:
        1. Do not invent facts or information.
        2. Do not use external knowledge.
        3. If the context does not contain enough information,
           clearly say that the information is not available.
        4. Answer clearly and professionally.
        5. Use the same language as the user's question.
        6. Include relevant company names, people, years, and
           investment amounts when available.
        """

        user_prompt = f"""
        Knowledge Graph Context:
        {context}

        User Question:
        {question}

        Answer based only on the provided context.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_completion_tokens=1024
        )

        return response.choices[0].message.content.strip()
