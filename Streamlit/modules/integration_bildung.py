import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")

def show():
    st.title("🎓 Integration: Bildung – Interaktive Karte mit Prozentwerten")

    # CSV-Daten einlesen
    url_csv = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url_csv, sep=",")

    df = df.drop(columns=["Staatsangehoerigkeit"])
    df = df.rename(columns={"Staatsangehoerigkeit_clean": "Staatsangehoerigkeit"})

    jahr = st.selectbox("Wähle ein Schuljahr", sorted(df["Schuljahr"].unique()), index=0)

    df_filtered = df[
        (df["Geschlecht"].isin(["männlich", "weiblich"])) &
        (df["Bundesland"] != "Deutschland") &
        (df["Schuljahr"] == jahr) &
        (df["Staatsangehoerigkeit"].isin(["deutsche Schüler/innen", "ausländische Schüler/innen"]))
    ]

    pivot = df_filtered.pivot_table(
        index=["Bundesland"],
        columns="Staatsangehoerigkeit",
        values="Schueler_innen_Anzahl",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    pivot["Anteil (%)"] = (
        pivot["ausländische Schüler/innen"] /
        (pivot["deutsche Schüler/innen"] + pivot["ausländische Schüler/innen"])
    ) * 100

    # GeoJSON laden
    url_geo = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json"
    geojson = gpd.read_file(url_geo)

    # Merge vorbereiten
    pivot = pivot.rename(columns={"Bundesland": "name"})
    merged = geojson.merge(pivot, on="name")

    # Viridis colormap (kein Legendenobjekt nötig)
    import branca.colormap as cm
    colormap = cm.linear.Viridis_09.scale(merged["Anteil (%)"].min(), merged["Anteil (%)"].max())

    # Karte erstellen
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles="CartoDB Positron")

    # GeoJSON mit Styling
    folium.GeoJson(
        data=merged,
        style_function=lambda feature: {
            'fillColor': colormap(feature["properties"]["Anteil (%)"]),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.8,
        },
        highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.9},
    ).add_to(m)

    # Prozentwerte als Label direkt in der Karte anzeigen
    for _, row in merged.iterrows():
        if row['geometry'].centroid.is_empty:
            continue
        lat = row['geometry'].centroid.y
        lon = row['geometry'].centroid.x
        value = round(row['Anteil (%)'], 1)
        folium.map.Marker(
            [lat, lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:10pt; color:black; font-weight:bold; text-align:center;">{value:.1f}%</div>'
            )
        ).add_to(m)

    # Karte anzeigen
    folium_static(m, width=1200, height=700)

show()
