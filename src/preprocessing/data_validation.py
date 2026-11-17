
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "data" / "raw" / "tech_startups_dataset_STUDENT.xlsx"

NODE_SHEETS = ["Founders", "Companies", "Investors", "Products", "Awards"]

RELATIONSHIP_SHEETS = [
    "Founded", "WorksAt", "InvestedIn",
    "Acquired", "Develops", "Won"
]


def audit_workbook():

    excel = pd.ExcelFile(DATA_PATH)

    print("\n========== DATA QUALITY AUDIT ==========")

    datasets = {
        sheet: pd.read_excel(excel, sheet_name=sheet)
        for sheet in NODE_SHEETS + RELATIONSHIP_SHEETS
    }

    # 1. Missing values and duplicates
    for sheet, df in datasets.items():

        print(f"\n--- {sheet} ---")
        print("Rows:", len(df))
        print("Missing values:")
        print(df.isnull().sum().to_string())

        print("Duplicate rows:", df.duplicated().sum())

        if "name" in df.columns:
            print("Duplicate names:", df["name"].duplicated().sum())

    # 2. Current values
    print("\n========== WORKS_AT CURRENT VALUES ==========")
    print(
        datasets["WorksAt"]["current"]
        .value_counts(dropna=False)
        .to_string()
    )

    # 3. Won entity types
    print("\n========== WON ENTITY TYPES ==========")
    print(
        datasets["Won"]["entity_type"]
        .value_counts(dropna=False)
        .to_string()
    )

    # 4. Reference validation
    print("\n========== FOREIGN KEY AUDIT ==========")

    founders = set(datasets["Founders"]["name"].dropna().str.strip())
    companies = set(datasets["Companies"]["name"].dropna().str.strip())
    investors = set(datasets["Investors"]["name"].dropna().str.strip())
    products = set(datasets["Products"]["name"].dropna().str.strip())
    awards = set(datasets["Awards"]["name"].dropna().str.strip())

    checks = {
        "Founded founder": ("Founded", "founder_name", founders),
        "Founded company": ("Founded", "company_name", companies),
        "WorksAt person": ("WorksAt", "person_name", founders),
        "WorksAt company": ("WorksAt", "company_name", companies),
        "InvestedIn investor": ("InvestedIn", "investor_name", investors),
        "InvestedIn company": ("InvestedIn", "company_name", companies),
        "Acquired acquirer": ("Acquired", "acquirer_company", companies),
        "Acquired target": ("Acquired", "target_company", companies),
        "Develops company": ("Develops", "company_name", companies),
        "Develops product": ("Develops", "product_name", products),
        "Won award": ("Won", "award_name", awards),
    }

    for label, (sheet, column, valid_values) in checks.items():

        values = datasets[sheet][column].dropna().astype(str).str.strip()
        invalid = sorted(set(values) - valid_values)

        print(f"\n{label}:")
        print("Invalid references:", invalid if invalid else "None")

    # 5. Save audit report
    report_dir = ROOT_DIR / "data" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    print("\nAudit completed.")

def inspect_anomalies():

    excel = pd.ExcelFile(DATA_PATH)

    sheets = {
        name: pd.read_excel(excel, sheet_name=name)
        for name in [
            "Founders", "Companies", "Investors",
            "Products", "Founded", "WorksAt",
            "InvestedIn", "Develops", "Won"
        ]
    }

    print("\n========== DUPLICATE RECORD DETAILS ==========")

    for name, df in sheets.items():

        duplicates = df[df.duplicated(keep=False)]

        if not duplicates.empty:
            print(f"\n{name}:")
            print(duplicates.to_string(index=False))

    print("\n========== CASE-INSENSITIVE MATCHING ==========")

    founders = sheets["Founders"]["name"].dropna().str.strip()
    companies = sheets["Companies"]["name"].dropna().str.strip()
    investors = sheets["Investors"]["name"].dropna().str.strip()

    checks = [
        ("elena rossi", founders),
        ("novapay", companies),
        ("Phantom Capital", investors),
    ]

    for value, reference in checks:

        matches = reference[
            reference.str.casefold() == value.casefold()
        ].tolist()

        print(f"\nInput: {value}")
        print("Matches:", matches if matches else "No match")

    print("\n========== WON PERSON REFERENCES ==========")

    won = sheets["Won"]
    founder_names = set(founders.str.casefold())

    person_records = won[
        won["entity_type"].astype(str).str.strip().str.casefold()
        == "person"
    ]

    for name in person_records["entity_name"].dropna():

        name = str(name).strip()

        exists = name.casefold() in founder_names

        print(
            f"{name}: "
            f"{'Found in Founders' if exists else 'Missing from Founders'}"
        )


if __name__ == "__main__":
    audit_workbook()
    inspect_anomalies()




