import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

st.set_page_config(layout="wide")

def show():
    st.title("🎓 Integration: Bildung (Interaktive Karte)")

    # Daten laden
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
        pivot["ausländische Schüler/innen"] / (pivot["deutsche Schüler/innen"] + pivot["ausländische Schüler/innen"])
    ) * 100

    # GeoJSON laden
    url_geo = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json"
    geojson = gpd.read_file(url_geo)

    # Bundeslandnamen normalisieren
    geojson["id"] = geojson["name"]
    pivot["id"] = pivot["Bundesland"]

    # Interaktive Karte erstellen
    fig = px.choropleth(
        pivot,
        geojson=geojson,
        locations="id",
        featureidkey="properties.name",
        color="Anteil (%)",
        hover_name="Bundesland",
        hover_data={
            "Anteil (%)": True,
            "ausländische Schüler/innen": True,
            "deutsche Schüler/innen": True
        },
        color_continuous_scale="Blues",
        title=f"Anteil ausländischer Schüler/innen pro Bundesland ({jahr})"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    st.plotly_chart(fig, use_container_width=True)
