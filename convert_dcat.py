import json

import pandas as pd
import numpy as np


def write_dataset(row: pd.DataFrame, identifier: str):
    dataset = dict()
    dataset['rdf:type'] = 'dcat:Dataset'
    dataset['rdf:identifier'] = identifier
    dataset['dct:title'] = {
        'de': row['title']
    }
    dataset['dct:description'] = {
        'de': row['description'] if row['description'] is not np.nan else ""
    }
    dataset['dcat:theme'] = "environment"
    dataset['dcat:keyword'] = row['keywords']
    dataset['adms:status'] = "published"
    dataset['dct:accessRights'] = "PUBLIC"
    dataset["bvclassification"] = "none"
    dataset["dcat:contactPoint"] = {
        "schema:name": row["Kontakt"] if row["Kontakt"] is not np.nan else "data@bafu.admin.ch",
        "schema:email": row["Kontakt"] if row["Kontakt"] is not np.nan else "data@bafu.admin.ch"
    }
    dataset["dct:issued"] = row["modified"] if row["modified"] is not np.nan else "2025-07-23"
    dataset["dct:modified"] = row["modified"] if row["modified"] is not np.nan else "2025-07-23"
    dataset["accrualPeriodicity"] = "YEARLY"
    dataset["dct:temporal"] = {
        "dcat:start_date": "1970-01-01",
        "dcat:end_date": "2025-01-01"
    }
    dataset["dcat:distribution"] = list()
    dataset["dcat:distribution"].append({
        "dct:identifier": identifier + "dist_a",
        "dct:title": row["title"] + " - Fake Distribution",
        "dct:format": "JSON",
        "dct:modified": row["modified"] if row["modified"] is not np.nan else "2025-07-23"
    })
    if row["URL"] is not np.nan:
        dataset["dcat:distribution"].append({
            "dct:identifier": identifier + "dist_indicator",
            "dct:title": row["title"] + " - Indikator",
            "dct:format": "CSV",
            "dct:modified": row["modified"] if row["modified"] is not np.nan else "2025-07-23",
            "dcat:accessURL": row["URL"]
        })
    return dataset

if __name__ == "__main__":
    df = pd.read_csv("Metadaten.csv", sep=";")
    datasets = list()
    for index, row in df.iterrows():
        datasets.append(write_dataset(row, str(index)))

    with open("bafu_datacatalog.json", "w", encoding="utf-8") as f:
        json.dump(datasets,f,indent=4, ensure_ascii=False)


