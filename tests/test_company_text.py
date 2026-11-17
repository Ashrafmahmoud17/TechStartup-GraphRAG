
import pandas as pd

from src.embeddings.embeddings import company_to_text

# Load cleaned companies
df = pd.read_csv("data/cleaned/companies.csv")

print("Total companies:", len(df))

# Convert company records into searchable text
company_documents = []

for _, row in df.iterrows():
    company = row.to_dict()
    company_documents.append({
        "name": company["name"],
        "text": company_to_text(company)
    })

# Display first 3 companies
for company in company_documents[:3]:
    print("\n" + "=" * 50)
    print("Company:", company["name"])
    print(company["text"])

print("\nTotal documents generated:", len(company_documents))
