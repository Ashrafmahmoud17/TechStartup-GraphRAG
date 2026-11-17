
from multiprocessing.dummy import connection
from unittest import result

from src.graph.neo4j_connection import Neo4jConnection
from src.graphrag.graph_retrieval import run_graphrag


def main():
    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        question = "Which fintech companies have received investments, and who invested in them?"

        print("\n========== USER QUESTION ==========")
        print(question)

        result = run_graphrag(
            connection,
            question=question,
            top_k=5
        )

        print("\n========== FINAL ANSWER ==========")
        print(result["answer"])

        print("\n========== RETRIEVED SOURCES ==========")
        for source in result["sources"]:
            print("-", source)

        print("\n========== CONTEXT STATISTICS ==========")
        print("Characters:", len(result["context"]))
        print("Words:", len(result["context"].split()))
        print("\n========== FULL CONTEXT ==========")
        print(result["context"])

        print("\nEnd-to-End GraphRAG completed successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
