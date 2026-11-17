
import os
import pandas as pd
from src.embeddings.embeddings import (
    EmbeddingService,
    company_to_text
)

from src.graph.neo4j_connection import Neo4jConnection


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

CLEANED_DIR = os.path.join(ROOT_DIR, "data", "cleaned")


CONSTRAINTS = [
    """
    CREATE CONSTRAINT founder_name_unique IF NOT EXISTS
    FOR (n:Founder) REQUIRE n.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT company_name_unique IF NOT EXISTS
    FOR (n:Company) REQUIRE n.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT investor_name_unique IF NOT EXISTS
    FOR (n:Investor) REQUIRE n.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT product_name_unique IF NOT EXISTS
    FOR (n:Product) REQUIRE n.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT award_name_unique IF NOT EXISTS
    FOR (n:Award) REQUIRE n.name IS UNIQUE
    """
]


NODE_FILES = {
    "Founder": "founders.csv",
    "Company": "companies.csv",
    "Investor": "investors.csv",
    "Product": "products.csv",
    "Award": "awards.csv"
}


RELATIONSHIP_CONFIG = {
    "FOUNDED": {
        "file": "founded.csv",
        "start_label": "Founder",
        "end_label": "Company",
        "start_col": "founder_name",
        "end_col": "company_name",
        "properties": ["year"],
        "identity": []
    },
    "WORKS_AT": {
        "file": "worksat.csv",
        "start_label": "Founder",
        "end_label": "Company",
        "start_col": "person_name",
        "end_col": "company_name",
        "properties": ["role", "current"],
        "identity": ["role"]
    },
    "INVESTED_IN": {
        "file": "investedin.csv",
        "start_label": "Investor",
        "end_label": "Company",
        "start_col": "investor_name",
        "end_col": "company_name",
        "properties": ["round", "amount_million", "year"],
        "identity": ["round"]
    },
    "ACQUIRED": {
        "file": "acquired.csv",
        "start_label": "Company",
        "end_label": "Company",
        "start_col": "acquirer_company",
        "end_col": "target_company",
        "properties": ["year", "amount_million"],
        "identity": []
    },
    "DEVELOPS": {
        "file": "develops.csv",
        "start_label": "Company",
        "end_label": "Product",
        "start_col": "company_name",
        "end_col": "product_name",
        "properties": [],
        "identity": []
    }
}


def create_constraints(connection):
    with connection.driver.session() as session:
        for constraint in CONSTRAINTS:
            session.run(constraint).consume()

    print("All uniqueness constraints created successfully!")


def load_nodes(connection):
    with connection.driver.session() as session:
        for label, filename in NODE_FILES.items():

            file_path = os.path.join(CLEANED_DIR, filename)
            df = pd.read_csv(file_path)

            records = (
                df.astype(object)
                .where(pd.notna(df), None)
                .to_dict("records")
            )

            query = f"""
            UNWIND $rows AS row
            MERGE (n:{label} {{name: row.name}})
            SET n += row
            """

            result = session.run(query, rows=records)
            summary = result.consume()

            print(
                f"{label}: {len(records)} records, "
                f"{summary.counters.nodes_created} new nodes"
            )

    print("All nodes loaded successfully!")


def load_relationship(connection, rel_type, config):

    file_path = os.path.join(CLEANED_DIR, config["file"])
    df = pd.read_csv(file_path)

    records = (
        df.astype(object)
        .where(pd.notna(df), None)
        .to_dict("records")
    )

    rows = []

    for record in records:
        rows.append({
            "start_name": record[config["start_col"]],
            "end_name": record[config["end_col"]],
            "identity": {
                key: record[key]
                for key in config["identity"]
            },
            "properties": {
                key: record[key]
                for key in config["properties"]
            }
        })

    identity_pattern = ""

    if config["identity"]:
        identity_pattern = " {" + ", ".join(
            f"{key}: row.identity.{key}"
            for key in config["identity"]
        ) + "}"

    query = f"""
    UNWIND $rows AS row

    MATCH (a:{config["start_label"]} {{name: row.start_name}})
    MATCH (b:{config["end_label"]} {{name: row.end_name}})

    MERGE (a)-[r:{rel_type}{identity_pattern}]->(b)

    SET r += row.properties

    RETURN count(r) AS matched
    """

    with connection.driver.session() as session:
        result = session.run(query, rows=rows)
        matched = result.single()["matched"]

    skipped = len(rows) - matched

    print(
        f"{rel_type}: {matched}/{len(rows)} matched, "
        f"{skipped} skipped (missing endpoints)"
    )


def load_won_relationships(connection):

    file_path = os.path.join(CLEANED_DIR, "won.csv")
    df = pd.read_csv(file_path)

    entity_mapping = {
        "person": "Founder",
        "company": "Company"
    }

    total_loaded = 0
    total_skipped = 0

    for entity_type, label in entity_mapping.items():

        subset = df[
            df["entity_type"].astype(str).str.lower() == entity_type
        ]

        rows = []

        for record in subset.to_dict("records"):
            rows.append({
                "start_name": record["entity_name"],
                "end_name": record["award_name"]
            })

        query = f"""
        UNWIND $rows AS row

        MATCH (a:{label} {{name: row.start_name}})
        MATCH (b:Award {{name: row.end_name}})

        MERGE (a)-[r:WON]->(b)

        RETURN count(r) AS matched
        """

        with connection.driver.session() as session:
            result = session.run(query, rows=rows)
            matched = result.single()["matched"]

        skipped = len(rows) - matched

        total_loaded += matched
        total_skipped += skipped

        print(
            f"WON ({label}): {matched}/{len(rows)} matched, "
            f"{skipped} skipped"
        )

    print(
        f"WON TOTAL: {total_loaded} matched, "
        f"{total_skipped} skipped"
    )


def load_all_relationships(connection):

    print("\n========== RELATIONSHIP LOADING ==========")

    for rel_type, config in RELATIONSHIP_CONFIG.items():
        load_relationship(connection, rel_type, config)

    load_won_relationships(connection)

    print("\nAll relationship loading operations completed!")
    

def load_company_embeddings(connection, batch_size=50):
    """
    Generate and store embeddings for Company nodes.
    """

    print("\n========== COMPANY EMBEDDINGS ==========")

    # Load cleaned companies
    file_path = os.path.join(CLEANED_DIR, "companies.csv")
    df = pd.read_csv(file_path)

    records = df.to_dict("records")

    # Convert companies into searchable documents
    documents = [
        company_to_text(record)
        for record in records
    ]

    print(f"Companies loaded: {len(documents)}")

    # Initialize embedding service
    embedding_service = EmbeddingService()

    total_updated = 0

    # Process documents in batches
    for start in range(0, len(records), batch_size):

        batch_records = records[start:start + batch_size]
        batch_documents = documents[start:start + batch_size]

        print(
            f"Generating embeddings: "
            f"{start + 1}-{start + len(batch_records)}"
        )

        vectors = embedding_service.embed_documents(
            batch_documents
        )

        rows = [
            {
                "name": record["name"],
                "embedding": vector,
                "embedding_text": document
            }
            for record, vector, document in zip(
                batch_records,
                vectors,
                batch_documents
            )
        ]

        # Store embeddings in Neo4j
        query = """
        UNWIND $rows AS row

        MATCH (c:Company {name: row.name})

        SET c.embedding = row.embedding,
            c.embedding_text = row.embedding_text

        RETURN count(c) AS updated
        """

        with connection.driver.session() as session:
            result = session.run(query, rows=rows)
            updated = result.single()["updated"]

        total_updated += updated

        print(f"Updated: {updated} companies")

    print("\n========== COMPLETED ==========")
    print(f"Total companies updated: {total_updated}")


if __name__ == "__main__":

    connection = Neo4jConnection()

    try:
        connection.verify_connection()

        create_constraints(connection)

        load_nodes(connection)

        load_all_relationships(connection)

    finally:
        connection.close()
