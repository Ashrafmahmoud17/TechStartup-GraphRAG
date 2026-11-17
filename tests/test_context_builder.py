
from src.graph.neo4j_connection import Neo4jConnection
from src.graphrag.graph_retrieval import retrieve_company_graph
from src.graphrag.context_builder import build_context


def main():
    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        companies = ["NovaPay", "FinLedger"]

        graph_results = retrieve_company_graph(
            connection,
            company_names=companies
        )

        context = build_context(graph_results)

        print("\n========== GENERATED CONTEXT ==========\n")
        print(context)

        print("\n========== CONTEXT STATISTICS ==========")
        print("Characters:", len(context))
        print("Words:", len(context.split()))

        print("\nContext Builder completed successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
