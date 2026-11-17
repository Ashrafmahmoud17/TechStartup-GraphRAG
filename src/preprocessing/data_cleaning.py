
from pathlib import Path
import pandas as pd


# ==========================================
# PATHS
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

RAW_PATH = ROOT_DIR / "data" / "raw" / "tech_startups_dataset_STUDENT.xlsx"
OUTPUT_DIR = ROOT_DIR / "data" / "cleaned"


# ==========================================
# SHEETS
# ==========================================

NODE_SHEETS = [
    "Founders",
    "Companies",
    "Investors",
    "Products",
    "Awards"
]

RELATIONSHIP_SHEETS = [
    "Founded",
    "WorksAt",
    "InvestedIn",
    "Acquired",
    "Develops",
    "Won"
]


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def normalize_text(df):
    """Remove leading and trailing spaces from text columns."""

    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return df


def build_name_lookup(df):
    """Create case-insensitive entity name mapping."""

    return {
        name.casefold(): name
        for name in df["name"].dropna().unique()
    }


def normalize_reference(df, column, lookup):
    """Normalize relationship references."""

    df[column] = df[column].map(
        lambda value: (
            lookup.get(value.casefold(), value)
            if isinstance(value, str)
            else value
        )
    )


def normalize_boolean(series):
    """Convert different boolean formats into True / False."""

    mapping = {
        "true": True,
        "yes": True,
        "y": True,
        "false": False,
        "no": False,
        "n": False
    }

    def convert(value):

        if pd.isna(value):
            return pd.NA

        if isinstance(value, bool):
            return value

        key = str(value).strip().casefold()

        if key not in mapping:
            raise ValueError(f"Unknown boolean value: {value}")

        return mapping[key]

    return series.map(convert).astype("boolean")


# ==========================================
# GHOSTAPP INVESTIGATION
# ==========================================

def investigate_ghostapp(raw_path, companies_df):

    print("\n========== GHOSTAPP INVESTIGATION ==========")

    raw_won = pd.read_excel(
        raw_path,
        sheet_name="Won"
    )

    ghostapp_rows = raw_won[
        raw_won["entity_name"]
        .astype(str)
        .str.contains("GhostApp", case=False, na=False)
    ]

    if ghostapp_rows.empty:
        print("No GhostApp records found in raw Won sheet.")

    else:
        print("\nGhostApp records in raw dataset:")
        print(ghostapp_rows.to_string(index=False))

    print("\n========== AVAILABLE COMPANIES ==========")

    print(
        companies_df["name"]
        .sort_values()
        .to_string(index=False)
    )


# ==========================================
# MAIN CLEANING FUNCTION
# ==========================================

def clean_workbook():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_PATH}"
        )

    excel = pd.ExcelFile(RAW_PATH)

    data = {
        sheet: normalize_text(
            pd.read_excel(excel, sheet_name=sheet)
        )
        for sheet in NODE_SHEETS + RELATIONSHIP_SHEETS
    }

    # 1. Remove exact duplicate rows

    print("\n========== DUPLICATE REMOVAL ==========")

    for sheet, df in data.items():

        before = len(df)

        data[sheet] = (
            df.drop_duplicates()
            .reset_index(drop=True)
        )

        removed = before - len(data[sheet])

        print(f"{sheet}: removed {removed} duplicate rows")

    # 2. Build entity name lookups

    lookups = {
        sheet: build_name_lookup(data[sheet])
        for sheet in NODE_SHEETS
    }

    # 3. Normalize relationship references

    reference_rules = {
        "Founded": {
            "founder_name": "Founders",
            "company_name": "Companies"
        },

        "WorksAt": {
            "person_name": "Founders",
            "company_name": "Companies"
        },

        "InvestedIn": {
            "investor_name": "Investors",
            "company_name": "Companies"
        },

        "Acquired": {
            "acquirer_company": "Companies",
            "target_company": "Companies"
        },

        "Develops": {
            "company_name": "Companies",
            "product_name": "Products"
        }
    }

    for sheet, rules in reference_rules.items():

        for column, entity_sheet in rules.items():

            normalize_reference(
                data[sheet],
                column,
                lookups[entity_sheet]
            )

    # 4. Normalize Won entity references

    won = data["Won"]

    for index, row in won.iterrows():

        entity_type = str(row["entity_type"]).casefold()
        entity_name = row["entity_name"]

        if not isinstance(entity_name, str):
            continue

        if entity_type == "person":
            lookup = lookups["Founders"]

        elif entity_type == "company":
            lookup = lookups["Companies"]

        else:
            continue

        won.at[index, "entity_name"] = lookup.get(
            entity_name.casefold(),
            entity_name
        )

    # Normalize award names

    normalize_reference(
        won,
        "award_name",
        lookups["Awards"]
    )

    # 5. Normalize boolean values

    data["WorksAt"]["current"] = normalize_boolean(
        data["WorksAt"]["current"]
    )

    # 6. Investigate GhostApp

    investigate_ghostapp(
        RAW_PATH,
        data["Companies"]
    )

    # 7. Detect unresolved references

    print("\n========== UNRESOLVED REFERENCES ==========")

    checks = {
        "Founded": {
            "founder_name": "Founders",
            "company_name": "Companies"
        },

        "WorksAt": {
            "person_name": "Founders",
            "company_name": "Companies"
        },

        "InvestedIn": {
            "investor_name": "Investors",
            "company_name": "Companies"
        },

        "Acquired": {
            "acquirer_company": "Companies",
            "target_company": "Companies"
        },

        "Develops": {
            "company_name": "Companies",
            "product_name": "Products"
        },

        "Won": {
            "award_name": "Awards"
        }
    }

    unresolved = []

    for sheet, rules in checks.items():

        df = data[sheet]

        for column, entity_sheet in rules.items():

            valid_names = set(
                lookups[entity_sheet].values()
            )

            invalid_mask = (
                df[column].notna()
                & ~df[column].isin(valid_names)
            )

            for index, value in df.loc[
                invalid_mask, column
            ].items():

                unresolved.append({
                    "sheet": sheet,
                    "row": index,
                    "column": column,
                    "value": value,
                    "expected_entity": entity_sheet
                })

    # Validate Won entity names separately

    for index, row in won.iterrows():

        entity_type = str(row["entity_type"]).casefold()

        if entity_type == "person":
            entity_sheet = "Founders"

        elif entity_type == "company":
            entity_sheet = "Companies"

        else:
            unresolved.append({
                "sheet": "Won",
                "row": index,
                "column": "entity_type",
                "value": row["entity_type"],
                "expected_entity": "Founders or Companies"
            })
            continue

        valid_names = set(
            lookups[entity_sheet].values()
        )

        if row["entity_name"] not in valid_names:

            unresolved.append({
                "sheet": "Won",
                "row": index,
                "column": "entity_name",
                "value": row["entity_name"],
                "expected_entity": entity_sheet
            })

    unresolved_df = pd.DataFrame(unresolved)

    unresolved_df.to_csv(
        OUTPUT_DIR / "unresolved_references.csv",
        index=False,
        encoding="utf-8-sig"
    )

    if unresolved:
        print(unresolved_df.to_string(index=False))

    else:
        print("No unresolved references found.")

    # 8. Save cleaned CSV files

    print("\n========== SAVING CLEANED DATA ==========")

    for sheet, df in data.items():

        output_path = OUTPUT_DIR / f"{sheet.lower()}.csv"

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"{sheet}: {len(df)} rows saved")

    print("\nCleaning completed successfully!")


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    clean_workbook()
