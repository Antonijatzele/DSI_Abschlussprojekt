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
    st.title("Integration: Arbeitsmarkt nach Herkunft")
    

    tab = st.radio("Wähle eine Ansicht", ["Global nach Herkunftsland", "Regional nach Herkunftsland"])

    
    if tab == "Regional nach Herkunftsland":
    
        
        df_regional = load_data_quoteRegional()
        url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json"
        gdf = gpd.read_file(url)


        # GeoJSON hat Bundesländer als "name"
        # DataFrame hat "Region", deshalb anpassen (ggf. kleine Namensanpassungen nötig)
        # Beispiel: "Baden-Württemberg" ist so in GeoJSON, aber checken!

        # Merge DataFrame mit GeoDataFrame auf Bundeslandname
        merged = gdf.merge(df_regional, left_on="name", right_on="Region ")
        merged['geometry'] = merged['geometry'].simplify(tolerance=0.05, preserve_topology=True)

        fig, axes = plt.subplots(len(regio_jahre), len(regio_laender), figsize=(20, 10))

        if len(regio_jahre) == 1:
            axes = axes[np.newaxis, :]
        if len(regio_laender) == 1:
            axes = axes[:, np.newaxis]

        for i, jahr in enumerate(regio_jahre):
            for j, land in enumerate(regio_laender):
                ax = axes[i, j]
                printRegionaleKarte_matplotlib(merged, land, jahr, ax)

        # Überschriften über Spalten (Länder)
        for j, land in enumerate(regio_laender):
            axes[0, j].set_title(land, fontsize=12, pad=20)  # pad= Abstand nach oben

        # Beschriftung links neben Zeilen (Jahre)
        for i, jahr in enumerate(regio_jahre):
            axes[i, 0].annotate(
                str(jahr),
                xy=(0, 0.5),  # linke Mitte der Achse (y=0.5)
                xycoords='axes fraction',  # Achsenkoordinaten (0-1)
                xytext=(-30, 0),  # 30 Punkte links vom linken Rand der Achse
                textcoords='offset points',
                size='large',
                ha='right',  # rechtsbündig, damit der Text links vom Achsenrand sitzt
                va='center',
                rotation=0
            )

        # Colorbar oben
        cbar_ax = fig.add_axes([0.25, 0.95, 0.5, 0.03]) 
        cb = mpl.colorbar.ColorbarBase(cbar_ax, cmap=cmap, norm=norm, orientation='horizontal')
        cb.set_label('Beschäftigungsquote (%)')
        cb.set_ticks(np.linspace(vmin, vmax, 5))

        plt.tight_layout(rect=[0, 0, 1, 0.90])  
        st.pyplot(fig)

    
            

    if tab == "Global nach Herkunftsland":
        df_geschlecht = load_data_geschlecht()

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
            st_folium(m, height=500,width=800)

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

    


show()