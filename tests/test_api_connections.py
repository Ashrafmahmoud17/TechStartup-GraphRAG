
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
import cohere

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Read credentials
groq_key = os.getenv("GROQ_API_KEY")
cohere_key = os.getenv("COHERE_API_KEY")


print("\n========== GROQ DIAGNOSTIC ==========")

try:
    client = Groq(api_key=groq_key)

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {
                "role": "user",
                "content": "What is 2 + 2? Explain in one short sentence."
            }
        ],
        max_tokens=100
    )

    choice = response.choices[0]

    print("Model:", response.model)
    print("Finish reason:", choice.finish_reason)
    print("Content:", repr(choice.message.content))
    print("Usage:", response.usage)

except Exception as e:
    print("Groq Error:", repr(e))

# Test Cohere
print("\n========== COHERE TEST ==========")

try:
    client = cohere.ClientV2(api_key=cohere_key)

    response = client.embed(
        texts=["Technology startups build innovative products."],
        model=os.getenv("EMBEDDING_MODEL"),
        input_type="search_document",
        embedding_types=["float"]
    )

    vector = response.embeddings.float_[0]

    print("Cohere: Connected")
    print("Embedding dimensions:", len(vector))

except Exception as e:
    print("Cohere Error:", str(e))
