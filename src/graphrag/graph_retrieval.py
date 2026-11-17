
def retrieve_company_graph(connection, company_names):
    """
    Retrieve companies and their connected entities from Neo4j.
    Includes founders, investors, products, awards, and acquisitions.
    """

    if not company_names:
        return []

    cypher_query = """
    MATCH (c:Company)
    WHERE c.name IN $company_names

    OPTIONAL MATCH (f:Founder)-[founded:FOUNDED]->(c)
    OPTIONAL MATCH (f)-[works:WORKS_AT]->(c)

    OPTIONAL MATCH (i:Investor)-[investment:INVESTED_IN]->(c)

    OPTIONAL MATCH (c)-[:DEVELOPS]->(p:Product)

    OPTIONAL MATCH (c)-[:WON]->(company_award:Award)

    OPTIONAL MATCH (founder:Founder)-[:WON]->(founder_award:Award)
    WHERE EXISTS {
        MATCH (founder)-[:FOUNDED]->(c)
    }

    OPTIONAL MATCH (c)-[acquisition:ACQUIRED]->(acquired:Company)

    RETURN
        c.name AS company,
        c.sector AS sector,
        c.description AS description,

        collect(DISTINCT {
            name: f.name,
            founded_year: founded.year,
            role: works.role,
            current: works.current
        }) AS founders,

        collect(DISTINCT {
            name: i.name,
            round: investment.round,
            amount_million: investment.amount_million,
            year: investment.year
        }) AS investors,

        collect(DISTINCT p.name) AS products,
        collect(DISTINCT company_award.name) AS awards,

        collect(DISTINCT {
            name: acquired.name,
            year: acquisition.year,
            amount_million: acquisition.amount_million
        }) AS acquisitions,

        collect(DISTINCT founder_award.name) AS founder_awards
    """

    with connection.driver.session() as session:
        result = session.run(
            cypher_query,
            company_names=company_names
        )

        return [record.data() for record in result]


from src.embeddings.vector_search import semantic_search
from src.graphrag.context_builder import build_context
from src.graphrag.generation import LLMGeneration


def run_graphrag(connection, question, top_k=5):
    """
    Execute the complete GraphRAG pipeline:
    Semantic Search -> Graph Retrieval -> Context Builder -> LLM.
    """

    # Step 1: Semantic Search
    search_results = semantic_search(
        connection,
        query_text=question,
        top_k=top_k
    )

    if not search_results:
        return {
            "answer": "No relevant companies were found.",
            "sources": [],
            "context": ""
        }

    # Step 2: Graph Retrieval
    company_names = [
        item["company"] for item in search_results
    ]

    graph_results = retrieve_company_graph(
        connection,
        company_names
    )

    # Step 3: Context Building
    context = build_context(graph_results)

    # Step 4: LLM Generation
    llm = LLMGeneration()

    answer = llm.generate_answer(
        question=question,
        context=context
    )

    return {
        "answer": answer,
        "sources": company_names,
        "context": context
    }
