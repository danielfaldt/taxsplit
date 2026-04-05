from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


@lru_cache(maxsize=None)
def load_tax_rate_data(year: int) -> list[dict[str, object]]:
    path = DATA_DIR / f"skattesatser-kommuner-{year}.txt"
    if not path.exists():
        raise ValueError(f"No municipal tax dataset is available for {year}.")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows: list[dict[str, object]] = []
        for row in reader:
            rows.append(
                {
                    "year": int(row["År"]),
                    "parish_code": row["Församlings-kod"].strip(),
                    "municipality": row["Kommun"].strip(),
                    "parish": row["Församling"].strip(),
                    "total_including_church": float(row["Summa, inkl. kyrkoavgift"]),
                    "total_excluding_church": float(row["Summa, exkl. kyrkoavgift"]),
                    "municipal_tax": float(row["Kommunal-skatt"]),
                    "regional_tax": float(row["Landstings-skatt"]),
                    "burial_fee": float(row["Begravnings-avgift"]),
                    "church_fee": float(row["Kyrkoavgift"]),
                }
            )
    return rows


@lru_cache(maxsize=None)
def municipality_catalog(year: int) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}

    for row in load_tax_rate_data(year):
        municipality = str(row["municipality"])
        parish = str(row["parish"])
        entry = grouped.setdefault(
            municipality,
            {
                "municipality": municipality,
                "total_excluding_church": float(row["total_excluding_church"]),
                "municipal_tax": float(row["municipal_tax"]),
                "regional_tax": float(row["regional_tax"]),
                "burial_fee": float(row["burial_fee"]),
                "parishes": [],
            },
        )
        entry["parishes"].append(
            {
                "parish": parish,
                "parish_code": str(row["parish_code"]),
                "church_fee": float(row["church_fee"]),
                "total_including_church": float(row["total_including_church"]),
            }
        )

    municipalities = sorted(grouped.values(), key=lambda item: str(item["municipality"]))
    for item in municipalities:
        item["parishes"] = sorted(item["parishes"], key=lambda parish: str(parish["parish"]))
    return municipalities


def municipality_payload(year: int) -> dict[str, object]:
    return {"year": year, "municipalities": municipality_catalog(year)}
