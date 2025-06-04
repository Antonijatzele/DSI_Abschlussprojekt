from io import StringIO
import folium
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium

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
    api_url = "https://api.github.com/repos/Antonijatzele/DSI_Abschlussprojekt/contents/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoten"
    res = requests.get(api_url)
    if res.status_code != 200:
        st.error("Konnte die Dateiliste nicht laden.")
        return []
    files = res.json()
    return [f["name"].replace(".csv", "") for f in files if f["name"].endswith(".csv")]

# Neuer Datensatz: nach Geschlecht
@st.cache_data
def load_data_geschlecht(): 
    laender = get_country_files()
    dfs = []
    for land in laender:
        url = f"https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoten/{land}.csv"
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

# Hauptfunktion
def show():
    st.title("Integration: Arbeitsmarkt")
    df = load_data()
    jahr_col = df.columns[0]

    tab1, tab2, tab3 = st.tabs(["Übersicht", "Nach Herkunftsland", "Beschreibung"])

    with tab3:
        st.markdown("""
        - **Beschäftigungsquote** im Vergleich zur Gesamtbevölkerung  
        - **Typische Berufsfelder** und Branchen  
        - **Einflussfaktoren**: Herkunftsregion, Aufenthaltsdauer, Bildungsniveau  
        """)

    with tab2:
        with st.expander("DataFrame anzeigen"):
            df_geschlecht = load_data_geschlecht()
            st.dataframe(df_geschlecht)

        st.header('Beschäftigungsquote (Top Herkunftsländer) nach Jahr')
        jahr = st.selectbox("Wähle ein Jahr", sorted(df_geschlecht["Jahr"].unique()))
        df_filtered = df_geschlecht[df_geschlecht["Jahr"] == jahr]
        wert_spalte = "Beschäftigungsquote"
        st.write(f"**Färbung basiert auf der Spalte:** {wert_spalte}")
        top3 = df_filtered.nlargest(3, wert_spalte)
        farben = ["#FFD700", "#C0C0C0", "#CD7F32"]
        col1, col2 = st.columns([2, 1])

        geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
        geojson_data = requests.get(geojson_url).json()

        with col1:
            m = folium.Map(zoom_start=5)
            threshold_scale = [0, 10, 20, 30, 40, 50, 60, 70]
            folium.Choropleth(
                geo_data=geojson_data,
                data=df_filtered,
                columns=["Land", "Beschäftigungsquote"],
                key_on="feature.properties.name",
                fill_color="YlOrRd",
                threshold_scale=threshold_scale,
                fill_opacity=1,
                line_opacity=0.3,
                legend_name="Beschäftigungsquote (%)",
                nan_fill_color="lightgray"
            ).add_to(m)

            from folium.features import DivIcon
            from shapely.geometry import shape
            for feature in geojson_data['features']:
                country_name = feature['properties']['name']
                if country_name in df_filtered["Land"].values:
                    geom = shape(feature['geometry'])
                    centroid = geom.centroid
                    folium.map.Marker(
                        [centroid.y, centroid.x],
                        icon=DivIcon(
                            icon_size=(150,36),
                            icon_anchor=(0,0),
                            html=f'<div style="font-size:10pt; font-weight:bold">{country_name}</div>',
                        )
                    ).add_to(m)

            st_folium(m, height=500, width=1200)

        with col2:
            df_sorted = df_filtered[["Land", wert_spalte]].sort_values(by=wert_spalte, ascending=False)
            st.dataframe(df_sorted.set_index("Land"), use_container_width=True)

    with tab1:
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

        diagramm_typ = st.selectbox("Diagrammtyp wählen", [
            "Liniendiagramm (wie bisher)",
            "Gestapeltes Balkendiagramm",
            "Vergleich nach Altersgruppen (Balken)"
        ])

        if diagramm_typ == "Liniendiagramm (wie bisher)":
            fig, ax = plt.subplots(figsize=(12, 7))
            colors = plt.cm.get_cmap('tab10', len(auspraegungen))
            linestyles = {'Ausländer': '-', 'Deutsch': '--'}
            for i, auspraegung in enumerate(auspraegungen):
                for gruppe in ['Ausländer', 'Deutsch']:
                    col_name = f"{gruppe}_{auspraegung}"
                    if col_name in data_plot.columns:
                        ax.plot(
                            data_plot[jahr_col], data_plot[col_name],
                            linestyle=linestyles[gruppe],
                            color=colors(i),
                            marker='o',
                            label=f"{gruppe} - {auspraegung}"
                        )
            ax.set_title(f"Vergleich Deutsch vs. Ausländer für {indikator} - {merkmal}")
            ax.set_xlabel("Jahr")
            ax.set_ylabel("Anzahl")
            ax.legend(title="Gruppe - Ausprägung", bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True)
            st.pyplot(fig)

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
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=row.reset_index(), x="Ausprägung", y="Wert", hue="Gruppe", ax=ax)
            plt.xticks(rotation=45)
            plt.title(f"Vergleich nach Altersgruppen für {jahr}")
            st.pyplot(fig)



show()