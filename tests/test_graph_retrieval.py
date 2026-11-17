
from src.graph.neo4j_connection import Neo4jConnection
from src.graphrag.graph_retrieval import retrieve_company_graph


def main():
    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        companies = ["NovaPay", "FinLedger"]

        results = retrieve_company_graph(
            connection,
            company_names=companies
        )

        print("\n========== GRAPH RETRIEVAL RESULTS ==========")

        for company in results:
            print(f"\nCompany: {company['company']}")
            print("Sector:", company["sector"])
            print("Description:", company["description"])

            print("\nFounders:", company["founders"])
            print("Investors:", company["investors"])
            print("Products:", company["products"])
            print("Awards:", company["awards"])
            print("Acquisitions:", company["acquisitions"])
            print("Founder Awards:", company["founder_awards"])

        print("\nGraph Retrieval completed!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
