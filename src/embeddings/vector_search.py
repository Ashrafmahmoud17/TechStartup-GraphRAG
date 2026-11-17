
from src.embeddings.embeddings import EmbeddingService


def semantic_search(connection, query_text, top_k=5):
    embedding_service = EmbeddingService()
    query_vector = embedding_service.embed_query(query_text)

    cypher_query = """
    CALL db.index.vector.queryNodes(
        'startup_embeddings',
        $top_k,
        $query_vector
    )
    YIELD node, score

    RETURN
        node.name AS company,
        node.sector AS sector,
        node.description AS description,
        score

    ORDER BY score DESC
    """

    with connection.driver.session() as session:
        result = session.run(
            cypher_query,
            top_k=top_k,
            query_vector=query_vector
        )

        return [record.data() for record in result]
