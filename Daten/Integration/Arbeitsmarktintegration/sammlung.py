import os
import csv
import pandas as pd

# Pfad zum Verzeichnis, das die Jahresordner enthält
basis_verzeichnis = "."  # <- Hier Pfad anpassen
output_datei = "zusammengefasste_daten.csv"

# Dictionary zum Sammeln aller Daten pro Jahr
jahresdaten = {}

# Alle Jahresordner durchgehen
for jahr in os.listdir(basis_verzeichnis):
    jahr_pfad = os.path.join(basis_verzeichnis, jahr)
    if not os.path.isdir(jahr_pfad):
        continue

    datenzeile = {}  # Hier sammeln wir die Spalten pro Jahr

    for dateiname in os.listdir(jahr_pfad):
        if not dateiname.endswith(".csv"):
            continue

        try:
            indikator, staatsangehoerigkeit, merkmal = dateiname.replace(".csv", "").split("_")
        except ValueError:
            print(f"Überspringe Datei mit unerwartetem Namen: {dateiname}")
            continue

        spaltenname = f"{staatsangehoerigkeit}_{indikator}_{merkmal}"
        dateipfad = os.path.join(jahr_pfad, dateiname)

        with open(dateipfad, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=';')
            zeilen = list(reader)

            # Zeile 11 bis 14 enthalten die echten Daten (Index 10–13)
            for zeile in zeilen[10:14]:
                if len(zeile) < 2:
                    continue
                merkmal_name = zeile[0].strip()
                wert = zeile[1].strip()
                key = f"{spaltenname}_{merkmal_name}"
                datenzeile[key] = wert

    jahresdaten[jahr] = datenzeile

# DataFrame aus gesammelten Daten erstellen
df = pd.DataFrame.from_dict(jahresdaten, orient='index')
df.index.name = 'Jahr'
df.reset_index(inplace=True)

# Punkte aus den Daten raus
df = df.applymap(lambda x: x.replace('.', '') if isinstance(x, str) else x)

# CSV-Datei schreiben
df.to_csv(output_datei, sep=';', index=False, encoding='utf-8')

print(f"Fertig! Datei gespeichert unter: {output_datei}")
