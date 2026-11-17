import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

load_dotenv(os.path.join(ROOT_DIR, ".env"))


class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")

        if not all([self.uri, self.username, self.password]):
            raise ValueError("Neo4j credentials are missing in .env")

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    def verify_connection(self):
        self.driver.verify_connectivity()
        print("Neo4j connection successful!")

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    connection = Neo4jConnection()
    try:
        connection.verify_connection()
    finally:
        connection.close()