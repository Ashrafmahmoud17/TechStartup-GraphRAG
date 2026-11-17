
from src.graph.neo4j_connection import Neo4jConnection
from src.graph.neo4j_loader import load_company_embeddings


def main():
    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        load_company_embeddings(connection)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
