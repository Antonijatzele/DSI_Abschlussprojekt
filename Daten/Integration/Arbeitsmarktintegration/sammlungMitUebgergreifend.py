import os
import csv
from collections import defaultdict

INPUT_ROOT = '.'  # Pfad, wo alle Jahresordner und uebergreifendeDaten liegen
OUTPUT_FILE = 'zusammengefuegt.csv'
START_ROW = 10  # Zeile 11 == Index 10

def remove_thousand_separators(value):
    return value.replace('.', '')

def parse_filename(filename):
    name, _ = os.path.splitext(filename)
    parts = name.split('_')
    if len(parts) != 3:
        return None
    return parts[1], parts[0], parts[2]  # Staatsangehörigkeit, Indikator, Merkmal

def process_yearly_data(base_dir, year_data):
    for folder in os.listdir(base_dir):
        print(f"Checking Folder: {folder}")
        if folder == 'uebergreifendeDaten' or not folder.isdigit():
            continue
        print(f"-Verarbeiter Folder: {folder}")
        year = folder
        folder_path = os.path.join(base_dir, folder)
        for filename in os.listdir(folder_path):
            if not filename.endswith('.csv'):
                continue
            parts = parse_filename(filename)
            if not parts:
                continue
            print(f"Verarbeite File: {filename}")
            staats, indikator, merkmal = parts
            col_name = f"{staats}_{indikator}_{merkmal}"
            file_path = os.path.join(folder_path, filename)
            with open(file_path, encoding='utf-8') as f:
                reader = list(csv.reader(f, delimiter=';'))
                for row in reader[START_ROW:START_ROW+4]:  # Zeilen 11–14
                    print(f"Verarbeite Row: {row}")
                    if len(row) < 2:
                        print(f"Skip Row: {row}")
                        continue
                    value = remove_thousand_separators(row[1])
                    year_data[year][f"{col_name}_{row[0].strip()}"] = value
                    print(f"ERgänze year Data: {year_data}")

def process_uebergreifende_daten(base_dir, year_data):
    path = os.path.join(base_dir, 'uebergreifendeDaten')
    if not os.path.isdir(path):
        return
    for filename in os.listdir(path):
        if not filename.endswith('.csv'):
            continue
        parts = parse_filename(filename)
        if not parts:
            continue
        staats, indikator, merkmal = parts
        file_path = os.path.join(path, filename)
        with open(file_path, encoding='utf-8') as f:
            reader = list(csv.reader(f, delimiter=';'))
            for row in reader[START_ROW:]:
                if len(row) < 3:
                    continue
                year = row[0].strip()
                if not year.isdigit():
                    continue
                year = year
                col_name_w = f"{staats}_{indikator}_{merkmal}_Frauen"
                col_name_m = f"{staats}_{indikator}_{merkmal}_Maenner"
                value_w = remove_thousand_separators(row[1].strip())
                value_m = remove_thousand_separators(row[2].strip())
                year_data[year][col_name_w] = value_w
                year_data[year][col_name_m] = value_m

def write_combined_csv(year_data, output_file):
    all_columns = set()
    for year in year_data:
        all_columns.update(year_data[year].keys())
    all_columns = sorted(all_columns)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Jahr'] + all_columns)
        for year in sorted(year_data.keys()):
            row = [year]
            data = year_data[year]
            for col in all_columns:
                row.append(data.get(col, ''))
            writer.writerow(row)

def main():
    year_data = defaultdict(dict)
    process_yearly_data(INPUT_ROOT, year_data)
    process_uebergreifende_daten(INPUT_ROOT, year_data)
    write_combined_csv(year_data, OUTPUT_FILE)
    print(f"CSV-Datei wurde erstellt: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
