
from src.embeddings.embeddings import EmbeddingService

def main():
    service = EmbeddingService()

    # Sample startup data
    documents = [
        "Paymob is an Egyptian fintech company providing digital payment solutions.",
        "MNT-Halan is a fintech company offering financial services and digital lending.",
        "Breadfast is an Egyptian e-commerce startup focused on grocery delivery."
    ]

    print("Generating document embeddings...")

    vectors = service.embed_documents(documents)

    print("Number of vectors:", len(vectors))
    print("Vector dimensions:", len(vectors[0]))

    query = "Which companies provide financial technology services?"

    print("\nGenerating query embedding...")

    query_vector = service.embed_query(query)

    print("Query vector dimensions:", len(query_vector))

    print("\nEmbedding test completed successfully!")


if __name__ == "__main__":
    main()
