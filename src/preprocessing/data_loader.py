
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "raw"
    / "tech_startups_dataset_STUDENT.xlsx"
)


def load_workbook():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    excel_file = pd.ExcelFile(DATA_PATH)

    print("=" * 60)
    print("TECH STARTUP DATASET INSPECTION")
    print("=" * 60)

    print(f"\nNumber of sheets: {len(excel_file.sheet_names)}")

    for sheet in excel_file.sheet_names:

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet
        )

        print("\n" + "=" * 60)
        print(f"SHEET: {sheet}")
        print("=" * 60)

        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 3 Rows:")
        print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    load_workbook()
