
from src.graph.neo4j_connection import Neo4jConnection
from src.embeddings.vector_search import semantic_search


def main():
    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        question = "Which companies provide financial technology services?"

        print("\nSearch Query:")
        print(question)

        results = semantic_search(
            connection,
            query_text=question,
            top_k=5
        )

        print("\n========== SEARCH RESULTS ==========")

        for index, item in enumerate(results, start=1):
            print(f"\n{index}. {item['company']}")
            print("Sector:", item["sector"])
            print("Description:", item["description"])
            print("Similarity Score:", round(item["score"], 4))

        print("\nSemantic Search completed!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
