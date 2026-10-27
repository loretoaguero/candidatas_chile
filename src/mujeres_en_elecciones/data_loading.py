from pathlib import Path

import pandas as pd

# Define the data directory and find all Excel files
data_dir = Path(__file__).resolve().parents[2] / "data" / "raw"

file_patterns = {
    "muni": "*Alcaldes_Datos*",
}

sheet_names_muni = {
    "Votación": "voting",
    "Votación por comuna": "voting_by_commune",
    "Participación": "participation",
    "Descripción votantes": "voters",
}


def load_candidate_data() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data/raw/historial_del_candidato_1989-2025_v1.csv"

    return pd.read_csv(data_path, header=6, sep=";")


# Define file patterns for different types of Excel files
def load_municipality_data(data_level: str) -> pd.DataFrame:
    if data_level not in sheet_names_muni.values():
        raise ValueError(f"Invalid data level: {data_level}")

    excel_files = list(data_dir.glob(file_patterns["muni"]))
    muni = []

    for f in excel_files:
        year = int(f.stem[:4])
        print(year)

        for sheet_name, prefix in sheet_names_muni.items():
            if prefix != data_level:
                continue

            sheet_options = (
                ["Votación", "Votación nacional", "Votación en Chile"]
                if prefix == "voting"
                else [sheet_name]
            )

            for option in sheet_options:
                try:
                    raw = pd.read_excel(
                        f,
                        sheet_name=option,
                        header=6,
                    )
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"No matching sheet found in {f.name}")

            raw.columns = raw.columns.map(lambda x: str(x).strip())

            muni.append(raw.assign(year=year).reset_index(drop=True))

    if not muni:
        return pd.DataFrame()

    return pd.concat(muni, ignore_index=True)
