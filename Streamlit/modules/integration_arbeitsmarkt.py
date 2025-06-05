from io import StringIO
import folium
import matplotlib as mpl
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium
import plotly.express as px
from urllib.parse import quote
from folium.features import DivIcon
from shapely.geometry import shape
from streamlit_folium import st_folium
import geopandas as gpd
import numpy as np
from collections import defaultdict
# Original-Datensatz laden
@st.cache_data
def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Arbeitsmarktintegration/zusammengefuegt.csv",
        sep=";",
        decimal=",",
        encoding="utf-8"
    )
    return df

@st.cache_data
def get_country_files():

    return ['Syria', 'Tunisia', 'Iraq', 'Italy', 'Turkey','Ukraine','Afghanistan', 'United States of America'  ] 
    api_url = "https://api.github.com/repos/Antonijatzele/DSI_Abschlussprojekt/contents/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoten"
    res = requests.get(api_url)
    

    if res.status_code != 200:
        st.write(f"Status Code: {res.status_code}")
        st.write(f"Response Headers: {res.headers}")
        st.write(f"Response Text: {res.text}")
        st.error("Konnte die Dateiliste nicht laden.")
        return []

    files = res.json()
    return [f["name"].replace(".csv", "") for f in files if f["name"].endswith(".csv")]

@st.cache_data
def load_gesamtDaten():
    base_url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Arbeitsmarktintegration/gesamtdaten/"
    filenames = [
        "auslaender_arbeitslose.csv",
        "auslaender_arbeitsuchende.csv",
        "auslaender_auszubildende.csv",
        "auslaender_beschaeftigte.csv",
        "deutsch_arbeitslose.csv",
        "deutsch_arbeitsuchende.csv",
        "deutsch_auszubildende.csv",
        "deutsch_beschaeftigte.csv"
    ]

    # Leerer DataFrame für alle Daten
    all_data = []

    # Daten einlesen und Herkunft/Status ergänzen
    for file in filenames:
        url = base_url + file
        df = pd.read_csv(url, sep=";")  # ggf. sep anpassen
        df_reduced = df.iloc[:, [0, 3]].copy()
        df_reduced.columns = ["Jahr", "Gesamt"]

        herkunft, status = file.replace(".csv", "").split("_", 1)
        df_reduced["Herkunft"] = herkunft
        df_reduced["Status"] = status

        df_reduced["Gesamt"] = df_reduced["Gesamt"].astype(str).str.replace(".", "", regex=False)
        df_reduced["Gesamt"] = pd.to_numeric(df_reduced["Gesamt"], errors="coerce")

        all_data.append(df_reduced)

    # Kombinierter DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

regio_jahre = [2021, 2022, 2023, 2024]
regio_laender = ["Afghanistan", "Iraq", "Italy", "Syria", "Tunisia", "Turkey", "Ukraine", "United States of America"]

@st.cache_data
def load_data_quoteRegional():

    # Leere Liste zum Sammeln der DataFrames
    dfs = []

    for jahr in regio_jahre:
        for land in regio_laender:
            # URL zusammensetzen, dabei Leerzeichen in Ländernamen URL-kodieren
            encoded_land = land.replace(" ", "%20")
            url = f"https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoteregional/{jahr}/{encoded_land}.csv"
            
            # CSV laden und Jahr + Land als Spalten hinzufügen
            try:
                df = pd.read_csv(url, sep=";", decimal=",", quotechar='"')
                df['Jahr'] = jahr
                df['Land'] = land
                dfs.append(df)
            except Exception as e:
                print(f"Fehler beim Laden von {url}: {e}")

    # Alle DataFrames zusammenführen
    final_df = pd.concat(dfs, ignore_index=True)

    # Optional: Spalten umbenennen, falls gewünscht
    # final_df.rename(columns={"Region": "Region", "Beschäftigungsquote": "Quote"}, inplace=True)
    return final_df

# Neuer Datensatz: nach Geschlecht
@st.cache_data
def load_data_geschlecht(): 
    laender = get_country_files()
    dfs = []
    for land in laender:
        encoded_land = quote(land)
        url = f"https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoten/{encoded_land}.csv"

        csv_data = requests.get(url).text
        df = pd.read_csv(
            StringIO(csv_data),
            sep=";",
            decimal=",",
            quotechar='"',
            na_values=["x"],
            skipinitialspace=True,
            encoding="utf-8"
        )
        df.columns = df.columns.str.strip().str.replace('"', '')
        df = df.dropna(subset=["Jahr"])
        df["Jahr"] = df["Jahr"].astype(int)
        df["Land"] = land
        dfs.append(df)
    gesamt_df = pd.concat(dfs, ignore_index=True)
    return gesamt_df

# Spaltennamen zerlegen
def parse_column(col):
    parts = col.split("_")
    if len(parts) == 4:
        return {
            "staat": parts[0],
            "indikator": parts[1],
            "merkmal": parts[2],
            "auspraegung": parts[3],
            "full": col
        }
    else:
        return None


def berechne_deutsch_spalten(df):
    """Berechnet 'Deutsch'-Spalten als Differenz zwischen 'insgesamt' und 'ausländer'."""
    cols = [c for c in df.columns if c != 'Jahr']
    groups = defaultdict(dict)

    for col in cols:
        parts = col.split('_')
        if len(parts) < 4:
            continue
        staat, merkmal, indikator, auspraegung = parts
        groups[(merkmal, indikator, auspraegung)][staat] = col

    df_result = df.copy()

    for (merkmal, indikator, auspraegung), staat_dict in groups.items():
        if 'insgesamt' in staat_dict and 'ausländer' in staat_dict:
            col_insgesamt = staat_dict['insgesamt']
            col_auslaender = staat_dict['ausländer']
            deutsch_col_name = f"deutsch_{merkmal}_{indikator}_{auspraegung}"
            df_result[deutsch_col_name] = df[col_insgesamt] - df[col_auslaender]

    # Optional: Entferne die "insgesamt"-Spalten
    df_result = df_result.drop(columns=[col for col in df_result.columns if col.startswith('insgesamt_')])
    
    return df_result

def filtere_nach_indikatoren(df, indikatoren_liste):
    if 'Jahr' not in df.columns:
        raise ValueError("Der DataFrame muss eine 'Jahr'-Spalte enthalten.")

    gefilterte_spalten = ['Jahr']  # Immer beibehalten
    neue_spalten = {'Jahr': 'Jahr'}
    for col in df.columns:
        if col == 'Jahr':
            continue
        parts = col.split('_')
        if len(parts) < 4:
            continue
        herkunft, merkmal, indikator, auspraegung = parts
        if indikator in indikatoren_liste:
            neuer_name = f"{herkunft} {merkmal} {auspraegung}"
            neue_spalten[col] = neuer_name

    df_gefiltert = df[list(neue_spalten.keys())].rename(columns=neue_spalten)

    return  df_gefiltert

def plot_bar_chart(data, title, xlabel, format):
    labels = [item[0] for item in data[:10]]
    values = [item[1] for item in data[:10]]
    fig, ax = plt.subplots(figsize=(10, 3))
    bars = ax.barh(labels, values)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.invert_yaxis()
    max_value = max(values)
    min_value = min(values)
    ax.set_xlim(min(min_value * 1.01, 0), max_value * 1.2 + 10)

    # Werte auf die Balken schreiben
    for bar in bars:
        width = bar.get_width()#
        position = width
        position = max(position, 0)

        text = width
        if("prozent" == format):
            text = f'{width:.0f} %'
            position = position + max_value / 40

        if("mio" == format):
            text = f'{(width/1000000):.2f} mio'
            position = max(position, 0)
            if(position > 0):
                position = position+10000
        ax.text(position, bar.get_y() + bar.get_height() / 2, text, va='center')
        
    st.pyplot(fig)

def printDeltas(df_filtered, ueberschrift):
    st.subheader(ueberschrift)
    deltas_abs = {}
    deltas_prozent = {}
    min_jahr = 2015
    max_jahr = df_filtered['Jahr'].max()
    df_filtered = df_filtered[df_filtered['Jahr'].isin([min_jahr, max_jahr])]

    for col in df_filtered.columns:
        if col == 'Jahr':
            continue
        start_wert = df_filtered.loc[df_filtered['Jahr'] == min_jahr, col].values
        end_wert = df_filtered.loc[df_filtered['Jahr'] == max_jahr, col].values
        if start_wert.size > 0 and end_wert.size > 0:
            start = start_wert[0]
            end = end_wert[0]
            delta = end - start
            deltas_abs[col] = delta
            if start != 0:
                prozent_delta = delta / start * 100
                deltas_prozent[col] = prozent_delta
            else:
                deltas_prozent[col] = None  # Division durch 0 vermeiden

    sorted_abs = sorted(deltas_abs.items(), key=lambda x: abs(x[1]), reverse=True)
    plot_bar_chart(sorted_abs, f"Top 10 absolute Entwicklung (mio) ({min_jahr} → {max_jahr})", "Delta absolut", "mio")

    filtered_prozent = {k: v for k, v in deltas_prozent.items() if v is not None and v > 0}
    sorted_prozent = sorted(filtered_prozent.items(), key=lambda x: abs(x[1]), reverse=True)
    plot_bar_chart(sorted_prozent, f"Top 10 prozentualer Zuwachs ({min_jahr} → {max_jahr})", "Delta in %", "prozent")

    negative_prozent = {k: v for k, v in deltas_prozent.items() if v is not None and v < 0}
    sorted_negative = sorted(negative_prozent.items(), key=lambda x: abs(x[1]), reverse=True)
    plot_bar_chart(sorted_negative, f"Top 10 prozentualer Rückgang ({min_jahr} → {max_jahr})", "Delta in %", "prozent")

def printRegionaleKarte(merged, land, jahr, container=None):
    data = merged[(merged['Land'] == land) & (merged['Jahr'] == jahr)]
    fig = px.choropleth(
        data,
        geojson=data.geometry,
        locations=data.index,
        color="Beschäftigungsquote ",
        hover_name="Region ",
        projection="mercator",
        color_continuous_scale="Viridis"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    if container:
        container.plotly_chart(fig)
    else:
        st.plotly_chart(fig)


# Norm und Colormap definieren (für Werte von 1 bis 100)
vmin, vmax = 1, 70
cmap = plt.cm.viridis
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
def printRegionaleKarte_matplotlib(merged, land, jahr, ax):
    # Filtere die Daten für Land und Jahr
    data = merged[(merged['Land'] == land) & (merged['Jahr'] == jahr)]
    
    # Zeichne die Karte mit der "Beschäftigungsquote " als Farbwert
    data.plot(column='Beschäftigungsquote ', cmap=cmap, norm=norm, linewidth=0.8, ax=ax, edgecolor='0.8')
    
    ax.axis('off')

# Hauptfunktion
def show():
    st.title("Integration: Arbeitsmarkt")
    

    tab1, tab2, tab3 = st.tabs(["Übersicht","Aufteilung", "Entwicklung"])
    
    

    with tab1:
        df = load_gesamtDaten()
        # Plotly-Liniendiagramm
        
        # Kombinierte Gruppenspalte
        df["Gruppe"] = df["Herkunft"] + " – " + df["Status"]

        # Optional: Filter
        herkunft_optionen = df['Herkunft'].unique()
        status_optionen = df['Status'].unique()

        herkunft = st.multiselect("Herkunft auswählen", herkunft_optionen, default=herkunft_optionen)
        status = st.multiselect("Status auswählen", status_optionen, default=status_optionen)

        # Filter anwenden
        df_filtered = df[df['Herkunft'].isin(herkunft) & df['Status'].isin(status)]
        df_filtered["Gruppe"] = df_filtered["Herkunft"] + " – " + df_filtered["Status"]

        # Liniendiagramm
        fig = px.line(
            df_filtered,
            x="Jahr",
            y="Gesamt",
            color="Gruppe",  # klare Unterscheidung nach Herkunft+Status
            markers=True,
            title="Gesamtzahlen nach Jahr für jede Herkunft–Status-Kombination"
        )

        st.plotly_chart(fig, use_container_width=True)

        jahre = [2015, 2024]
        df_tabelle = df_filtered[df_filtered['Jahr'].isin(jahre)]

        # Pivot-Tabelle erstellen
        df_pivot = df_tabelle.pivot_table(index="Gruppe", columns="Jahr", values="Gesamt")
        df_pivot = df_pivot[[2015, 2024]]
        df_pivot.columns = ["Wert 2015", "Wert 2024"]

        # Deltas berechnen
        df_pivot["Δ Absolut"] = df_pivot["Wert 2024"] - df_pivot["Wert 2015"]
        df_pivot["Δ Relativ (%)"] = (df_pivot["Δ Absolut"] / df_pivot["Wert 2015"]) * 100

        # Formatieren
        df_formatiert = df_pivot.copy()
        df_formatiert = df_formatiert.reset_index()

        df_formatiert["Wert 2015"] = df_formatiert["Wert 2015"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        df_formatiert["Wert 2024"] = df_formatiert["Wert 2024"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        df_formatiert["Δ Absolut"] = df_formatiert["Δ Absolut"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        df_formatiert["Δ Relativ (%)"] = df_formatiert["Δ Relativ (%)"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

        # Tabelle anzeigen (rechtsbündig durch monospace-Layout)
        st.subheader("Vergleichstabelle: Werte für 2015 und 2024 inkl. Entwicklung")
        st.table(df_formatiert)
        
    with tab3:
        df = load_data()
        jahr_col = df.columns[0]
        cols = [c for c in df.columns if c != 'Jahr']
        groups = defaultdict(dict)

        for col in cols:
            parts = col.split('_')
            if len(parts) < 4:
                continue
            staat, merkmal, indikator, auspraegung = parts
            groups[(merkmal, indikator, auspraegung)][staat] = col

        df_deutsch = berechne_deutsch_spalten(df)
        df_filtered = filtere_nach_indikatoren(df_deutsch, ['nachaltersgruppe'])
        printDeltas(df_filtered, "Nach Altersgruppe")

        df_filtered = filtere_nach_indikatoren(df_deutsch, ['nachgeschlecht'])
        printDeltas(df_filtered, "Nach Geschlecht")

        df_filtered = filtere_nach_indikatoren(df_deutsch, ['nachberufsabschluss'])
        printDeltas(df_filtered, "Nach Berufsabschluss")
            

    with tab2:
        df = load_data()
        jahr_col = df.columns[0]
        st.subheader("Arbeitsmarktintegration — Deutsch vs. Ausländer")
        cols = df.columns[1:]
        parsed_cols = [parse_column(c) for c in cols]
        parsed_cols = [p for p in parsed_cols if p is not None]
        indikator_options = sorted(set(p['indikator'] for p in parsed_cols))
        merkmal_options = sorted(set(p['merkmal'] for p in parsed_cols))
        indikator = st.selectbox("Indikator", indikator_options)
        merkmal = st.selectbox("Merkmal", merkmal_options)
        relevante_spalten = [p for p in parsed_cols if p['indikator'] == indikator and p['merkmal'] == merkmal]

        if not relevante_spalten:
            st.warning("Keine Daten für diese Kombination gefunden.")
            return

        auspraegungen = sorted(set(p['auspraegung'] for p in relevante_spalten))
        data_plot = pd.DataFrame()
        data_plot[jahr_col] = df[jahr_col]

        for auspraegung in auspraegungen:
            sp_insgesamt = None
            sp_auslaender = None
            for p in relevante_spalten:
                if p['auspraegung'] == auspraegung:
                    if p['staat'].lower() == 'insgesamt':
                        sp_insgesamt = p['full']
                    elif p['staat'].lower() in ['ausländer', 'auslaender']:
                        sp_auslaender = p['full']
            if sp_insgesamt and sp_auslaender:
                data_plot[f"Ausländer_{auspraegung}"] = df[sp_auslaender]
                data_plot[f"Deutsch_{auspraegung}"] = df[sp_insgesamt] - df[sp_auslaender]
            elif sp_auslaender:
                data_plot[f"Ausländer_{auspraegung}"] = df[sp_auslaender]
            elif sp_insgesamt:
                data_plot[f"Deutsch_{auspraegung}"] = df[sp_insgesamt]

       # diagramm_typ = st.selectbox("Diagrammtyp wählen", [
       #     "Liniendiagramm",
       #     "Gestapeltes Balkendiagramm",
       #     "Vergleich nach Altersgruppen (Balken)"
        #])

        diagramm_typ = "Liniendiagramm"

        if diagramm_typ == "Liniendiagramm":
            


            # Daten für Plotly vorbereiten
            df_plotly = pd.DataFrame()
            df_plotly[jahr_col] = data_plot[jahr_col]
            
            for auspraegung in auspraegungen:
                for gruppe in ['Ausländer', 'Deutsch']:
                    col_name = f"{gruppe}_{auspraegung}"
                    if col_name in data_plot.columns:
                        df_plotly[f"{gruppe} - {auspraegung}"] = data_plot[col_name]

            # Daten ins lange Format transformieren für Plotly
            df_long = df_plotly.melt(id_vars=[jahr_col], var_name='Gruppe_Ausprägung', value_name='Wert')

            fig = px.line(
                df_long,
                x=jahr_col,
                y='Wert',
                color='Gruppe_Ausprägung',
                markers=True,
                title=f"Vergleich Deutsch vs. Ausländer für {indikator} - {merkmal}",
                labels={jahr_col: "Jahr", "Wert": "Anzahl"}
            )
            
            fig.update_layout(legend_title_text='Gruppe - Ausprägung')
            st.plotly_chart(fig, use_container_width=True)


        elif diagramm_typ == "Gestapeltes Balkendiagramm":
            data_plot_sum = data_plot.drop(columns=[jahr_col]).groupby(lambda x: x.split('_')[1], axis=1).sum()
            data_plot_sum[jahr_col] = df[jahr_col]
            data_plot_sum.set_index(jahr_col).plot(kind="bar", stacked=True, figsize=(12, 7))
            plt.title(f"Gestapeltes Balkendiagramm: {indikator} - {merkmal}")
            plt.ylabel("Anzahl")
            st.pyplot(plt.gcf())

        elif diagramm_typ == "Vergleich nach Altersgruppen (Balken)":
            jahr = st.selectbox("Jahr auswählen", data_plot[jahr_col])
            row = data_plot[data_plot[jahr_col] == jahr].drop(columns=[jahr_col]).T
            row.columns = ["Wert"]
            row["Gruppe"] = row.index.str.split('_').str[0]
            row["Ausprägung"] = row.index.str.split('_').str[1]

            fig = px.bar(
                row.reset_index(),
                x="Ausprägung",
                y="Wert",
                color="Gruppe",
                barmode="group",
                text_auto=True  # Werte auf die Balken schreiben
            )
            fig.update_layout(title=f"Vergleich nach Altersgruppen für {jahr}")
            st.plotly_chart(fig, use_container_width=True)


show()