
import pandas as pd

from src.embeddings.embeddings import (
    EmbeddingService,
    company_to_text
)


def main():
    # Load cleaned companies
    df = pd.read_csv("data/cleaned/companies.csv")

    # Convert companies into documents
    documents = [
        company_to_text(row.to_dict())
        for _, row in df.iterrows()
    ]

    print("Companies loaded:", len(documents))

    # Generate embeddings
    service = EmbeddingService()

    print("\nGenerating embeddings...")

    vectors = service.embed_documents(documents)

    # Validate results
    print("\n========== EMBEDDING RESULTS ==========")
    print("Documents:", len(documents))
    print("Generated vectors:", len(vectors))
    print("Vector dimensions:", len(vectors[0]))

    assert len(documents) == len(vectors)
    assert all(len(vector) == 1024 for vector in vectors)

    print("\nAll company embeddings generated successfully!")


if __name__ == "__main__":
    main()
