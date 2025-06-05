from io import StringIO
import folium
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
        "auslaender_arbeitssuchende.csv",
        "auslaender_auszubildende.csv",
        "auslaender_beschaeftigte.csv",
        "deutsch_arbeitslose.csv",
        "deutsch_arbeitssuchende.csv",
        "deutsch_auszubildende.csv",
        "deutsch_beschaeftigte.csv"
    ]

    # Leerer DataFrame für alle Daten
    all_data = []

    # Daten einlesen und Herkunft/Status ergänzen
    for file in filenames:
        url = base_url + file
        df = pd.read_csv(url, sep=";")  # ggf. sep anpassen
        herkunft, status = file.replace(".csv", "").split("_", 1)
        df["Herkunft"] = herkunft
        df["Status"] = status
        all_data.append(df)

    # Kombinierter DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)

    # Anzeige in Streamlit
    st.title("Arbeitsmarktintegration - Kombinierte Daten")
    st.write(combined_df)
    return combined_df


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


# Hauptfunktion
def show():
    st.title("Integration: Arbeitsmarkt")
    df = load_data()
    jahr_col = df.columns[0]

    tab1, tab2, tab3, tab4 = st.tabs(["Übersicht","Aufteilung", "Entwicklung", "Nach Herkunftsland"])
    
    with tab1:
        df = load_gesamtDaten()

    with tab3:
        
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
            

    with tab4:
        with st.expander("📊 DataFrame anzeigen"):
            df_geschlecht = load_data_geschlecht()
            st.dataframe(df_geschlecht)

        st.header('Beschäftigungsquote (Top-Herkunftsländer) nach Jahr')

        # Jahr auswählen
        jahr = st.selectbox("Wähle ein Jahr", sorted(df_geschlecht["Jahr"].unique()))
        df_filtered = df_geschlecht[df_geschlecht["Jahr"] == jahr]

        wert_spalte = "Beschäftigungsquote"
        st.markdown(f"**Färbung basiert auf der Spalte:** `{wert_spalte}`")

        # Top 3 Länder
        top3 = df_filtered.nlargest(10, wert_spalte)
        farben = ["#FFD700", "#C0C0C0", "#CD7F32"]

        # GeoJSON laden
        geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
        geojson_data = requests.get(geojson_url).json()

        col1, col2 = st.columns([3, 1])

        with col1:
            # Karte erstellen
            m = folium.Map(location=[20, 10], zoom_start=2, tiles="cartodbpositron")

            # Choroplethen-Karte
            folium.Choropleth(
                geo_data=geojson_data,
                data=df_filtered,
                columns=["Land", "Beschäftigungsquote"],
                key_on="feature.properties.name",
                fill_color="YlGnBu",
                threshold_scale=[0, 20, 30, 40, 50, 60, 70, 80],
                fill_opacity=0.8,
                line_opacity=0.2,
                legend_name="Beschäftigungsquote (%)",
                nan_fill_color="lightgray",
                highlight=True
            ).add_to(m)

            # Länder-Namen als Marker anzeigen
            for feature in geojson_data['features']:
                country_name = feature['properties']['name']
                if country_name in df_filtered["Land"].values:
                    geom = shape(feature['geometry'])
                    centroid = geom.centroid
                    folium.map.Marker(
                        [centroid.y, centroid.x],
                        icon=DivIcon(
                            icon_size=(150, 36),
                            icon_anchor=(0, 0),
                            html=f'''
                            <div style="
                                background-color: rgba(255, 255, 255, 0.6);
                                padding: 2px 4px;
                                border-radius: 4px;
                                font-size: 10pt;
                                font-weight: bold;">
                                {country_name}
                            </div>''',
                        )
                    ).add_to(m)

            # Karte anzeigen
            st_folium(m, height=550, width=1000)

        with col2:
            st.subheader("Top Länder")
            for i, row in top3.iterrows():
                st.markdown(f"**{row['Land']}** – {row[wert_spalte]} %")
            

        #Entwicklung über die Jahre
        fig = px.line(
            df_geschlecht,
            x="Jahr",
            y="Beschäftigungsquote",
            color="Land",
            markers=True,
            title="Entwicklung der Beschäftigungsquote nach Herkunftsland"
        )
        fig.update_layout(hovermode="closest")

        st.plotly_chart(fig, use_container_width=True)
        # balkendiagram 
        st.subheader("Entwicklung der Beschäftigungsquote nach Geschlecht (2021–2023)")

        # Filter auf die Jahre 2021 bis 2023
        df_gender_filtered = df_geschlecht[(df_geschlecht["Jahr"] >= 2021) & (df_geschlecht["Jahr"] <= 2023)]

        # Länder-Auswahl als Multiselect
        laender_liste = sorted(df_gender_filtered["Land"].unique())
        ausgewaehlte_laender = st.multiselect("Wähle Länder aus", laender_liste)

        # Filter nach ausgewählten Ländern
        df_laender = df_gender_filtered[df_gender_filtered["Land"].isin(ausgewaehlte_laender)]

        if df_laender.empty:
            st.warning("Keine Daten für die ausgewählten Länder vorhanden.")
        else:
            # Durchschnitt pro Jahr und Geschlecht berechnen
            df_agg = df_laender.groupby(["Jahr"]).agg({
                "Frauen Beschäftigungsquote": "mean",
                "Männer Beschäftigungsquote": "mean"
            }).reset_index()

            # Long-Format für Plotly
            df_long = df_agg.melt(
                id_vars="Jahr",
                value_vars=["Frauen Beschäftigungsquote", "Männer Beschäftigungsquote"],
                var_name="Geschlecht",
                value_name="Beschäftigungsquote"
            )

            # Beschriftung vereinfachen
            df_long["Geschlecht"] = df_long["Geschlecht"].str.replace(" Beschäftigungsquote", "")

            # Balkendiagramm
            fig_bar = px.bar(
                df_long,
                x="Jahr",
                y="Beschäftigungsquote",
                color="Geschlecht",
                barmode="group",
                title=f"Beschäftigungsquote nach Geschlecht (2021–2023) für {', '.join(ausgewaehlte_laender)}",
                labels={"Beschäftigungsquote": "Beschäftigungsquote (%)"},
                text_auto=True
            )

            fig_bar.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
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