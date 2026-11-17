
"""
Ontology Design
Tech Startup Knowledge Graph & GraphRAG

Defines:
- Node Labels
- Node Properties
- Relationship Types
- Relationship Properties
- Relationship Directions
"""

# ==========================================
# 1. NODE DEFINITIONS
# ==========================================

NODE_SCHEMA = {

    "Founder": {
        "source_sheet": "Founders",
        "primary_key": "name",
        "properties": [
            "name",
            "born",
            "role",
            "hometown"
        ]
    },

    "Company": {
        "source_sheet": "Companies",
        "primary_key": "name",
        "properties": [
            "name",
            "founded",
            "sector",
            "headquarters",
            "valuation_billion",
            "description"
        ]
    },

    "Investor": {
        "source_sheet": "Investors",
        "primary_key": "name",
        "properties": [
            "name",
            "founded",
            "type",
            "hq"
        ]
    },

    "Product": {
        "source_sheet": "Products",
        "primary_key": "name",
        "properties": [
            "name",
            "category",
            "launch_year"
        ]
    },

    "Award": {
        "source_sheet": "Awards",
        "primary_key": "name",
        "properties": [
            "name",
            "category",
            "year"
        ]
    }
}


# ==========================================
# 2. RELATIONSHIP DEFINITIONS
# ==========================================

RELATIONSHIP_SCHEMA = {

    "FOUNDED": {
        "source_sheet": "Founded",
        "start_node": "Founder",
        "end_node": "Company",
        "start_column": "founder_name",
        "end_column": "company_name",
        "properties": [
            "year"
        ]
    },

    "WORKS_AT": {
        "source_sheet": "WorksAt",
        "start_node": "Founder",
        "end_node": "Company",
        "start_column": "person_name",
        "end_column": "company_name",
        "properties": [
            "role",
            "current"
        ]
    },

    "INVESTED_IN": {
        "source_sheet": "InvestedIn",
        "start_node": "Investor",
        "end_node": "Company",
        "start_column": "investor_name",
        "end_column": "company_name",
        "properties": [
            "round",
            "amount_million",
            "year"
        ]
    },

    "ACQUIRED": {
        "source_sheet": "Acquired",
        "start_node": "Company",
        "end_node": "Company",
        "start_column": "acquirer_company",
        "end_column": "target_company",
        "properties": [
            "year",
            "amount_million"
        ]
    },

    "DEVELOPS": {
        "source_sheet": "Develops",
        "start_node": "Company",
        "end_node": "Product",
        "start_column": "company_name",
        "end_column": "product_name",
        "properties": []
    },

    "WON": {
        "source_sheet": "Won",
        "start_node": None,
        "end_node": "Award",
        "start_column": "entity_name",
        "end_column": "award_name",
        "entity_type_column": "entity_type",
        "entity_type_mapping": {
            "person": "Founder",
            "company": "Company"
        },
        "properties": []
    }
}


# ==========================================
# 3. GRAPH CONFIGURATION
# ==========================================

GRAPH_CONFIG = {
    "database_name": "neo4j",
    "node_count": len(NODE_SCHEMA),
    "relationship_count": len(RELATIONSHIP_SCHEMA),
    "unique_key": "name"
}


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

def get_node_labels():
    """Return all node labels."""
    return list(NODE_SCHEMA.keys())


def get_relationship_types():
    """Return all relationship types."""
    return list(RELATIONSHIP_SCHEMA.keys())


def get_node_definition(label):
    """Return schema for a specific node label."""
    return NODE_SCHEMA.get(label)


def get_relationship_definition(rel_type):
    """Return schema for a specific relationship type."""
    return RELATIONSHIP_SCHEMA.get(rel_type)


def print_ontology():

    print("\n========== NODE TYPES ==========")

    for label, schema in NODE_SCHEMA.items():

        print(f"\n{label}")
        print(f"Source Sheet: {schema['source_sheet']}")
        print(f"Primary Key: {schema['primary_key']}")
        print(f"Properties: {schema['properties']}")

    print("\n========== RELATIONSHIP TYPES ==========")

    for rel_type, schema in RELATIONSHIP_SCHEMA.items():

        print(f"\n{rel_type}")
        print(
            f"Direction: "
            f"{schema['start_node']} -> {schema['end_node']}"
        )
        print(f"Source Sheet: {schema['source_sheet']}")
        print(f"Properties: {schema['properties']}")


if __name__ == "__main__":
    print_ontology()
