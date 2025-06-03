import json
import numpy as np
import pandas as pd
from pathlib import Path

# Erstellt aus den Destasis-JSON-Daten ein Pandas Dataframe
def json2df(stat, lng="de"):
    base_path = Path(__file__).parent.parent.parent / "Daten" / "Migration"

    # Daten laden
    with open(base_path / f"{stat}_data.json", encoding="utf8") as f:
        in_json = f.read()
    js = json.loads(in_json)
    data = js["data"][0]

    # Struktur laden
    with open(base_path / f"{stat}_structure.json", encoding="utf8") as f:
        in_json = f.read()
    structure = json.loads(in_json)

    # Daten als Numpy-Array einladen
    arr = np.array(data["value"]).reshape(data["size"])

    # Array flatten und Indices anspeichern
    flat_arr = []
    for idx, subarray in np.ndenumerate(arr):
        # Addiere den Index und den Wert als Tuple
        flat_arr.append((idx, subarray))

    # Liste zur Übersetzung der Indices in Codes erstellen
    dim = []
    for cat in data["id"]:
        ind = data["dimension"][cat]["category"]["index"]
        ind_rev = {value: key for key, value in ind.items()}
        dim.append(ind_rev)

    # Incdies in Codes/Werte übersetzen und Tabelle erstellen
    table = []
    for x in flat_arr:
        row = []
        for i, j in enumerate(x[0]):
            code = dim[i][j]
            if data["id"][i] == "statistic":
                val = structure["statistics"][code]["label"][lng]
            elif data["id"][i] == "content":
                code = code.split('$')[0]
                val = structure["contents"][code]["label"][lng]
            else:
                val = structure["variableValues"][code]["label"][lng]
            
            row.append(code)
            row.append(val)

            
        row.append(int(x[1]))
        table.append(row)

    # Spaltennamen erstellen
    cols = [item for sublist in [[col, structure["variables"][col]["label"][lng] if not col in ["statistic", "content"] else col + "_desc"] for col in data["id"]] for item in sublist] + ["Value"]
    
    # Tabelle als DataFrame zurückgeben
    return pd.DataFrame(table, columns=cols)