import streamlit as st
import folium
import branca.colormap as cm
import geopandas as gpd
import pandas as pd
from pathlib import Path
from streamlit_folium import st_folium
import plotly.express as px


# Geodaten laden
@st.cache_data
def lade_geodaten():
    gdf = gpd.read_file(Path("Streamlit/data/migration/kreise_mit_daten.geojson"))
    gdf = gdf.to_crs("EPSG:4326")

    # Farbskala erstellen
    min_value = gdf['Anteil_Zahl'].min()
    max_value = gdf['Anteil_Zahl'].max()
    colormap = cm.linear.YlGnBu_09.scale(min_value, max_value)
    colormap.caption = 'Ausländeranteil'  # Beschriftung der Legende

    # Farben auf Basis der Skala zuweisen
    gdf['color'] = gdf['Anteil_Zahl'].apply(colormap)
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001, preserve_topology=True)

    return gdf.to_json(), colormap


# Karte erstellen
def erstelle_karte(geojson_str):
    m = folium.Map(location=[51.0, 10.0], zoom_start=6)
    folium.GeoJson(
        geojson_str,
        style_function=lambda feature: {
            'fillColor': feature['properties']['color'],
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=['Kreise', 'Gesamt', 'Anteil', 'Top Herk.-Länder:' , '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.'],)
    ).add_to(m)
    return m


def show():
    tab1, tab2 = st.tabs(["Karte", "Plot"])

    with tab1:
        st.subheader('Kreise')
        geojson_str, colormap = lade_geodaten()
        m = erstelle_karte(geojson_str)
        
        # Farbskala (Legende) zur Karte hinzufügen
        colormap.add_to(m)

        # Karte anzeigen
        map_data = st_folium(m, width=700, height=700)
    
    with tab2:

        # Titel
        st.subheader("Bevölkerungsdichte vs. Ausländeranteil")

        # Fester Pfad zur CSV-Datei
        csv_path = "Streamlit/data/migration/scatter_plot_anteil_dichte.csv"

        # CSV einlesen
        df = pd.read_csv(csv_path)

        # Dropdown-Menü für Aufenthaltstitel
        titel_options = ["insgesamt"] + sorted(df["Ausgewählte Aufenthaltstitel"].dropna().unique().tolist())
        selected_titel = st.selectbox("Wähle einen Aufenthaltstitel", titel_options, index=0)

        # Daten filtern oder aggregieren
        if selected_titel == "insgesamt":
            df_filtered = (
                df.groupby("KREISE", as_index=False)
                .agg({
                    "Dichte": "mean",  # Durchschnitt der Dichte
                    "Anteil": "sum"    # Summe des Anteils
                })
            )
        else:
            df_filtered = df[df["Ausgewählte Aufenthaltstitel"] == selected_titel]

        # Erstellen des Plotly Scatterplots
        fig = px.scatter(
            df_filtered,
            x="Dichte",
            y="Anteil",
            color="KREISE",   # Für die Farbdifferenzierung nach Kreis
            title=f"Ausländeranteil ({selected_titel})",
            labels={
                "Dichte": "Bevölkerungsdichte (Einwohner pro km²)",
                "Anteil": "Ausländeranteil (%)"
            },
            color_continuous_scale='Viridis',  # Farbpalette

        )

        # Anzeige des Plots in Streamlit
        st.plotly_chart(fig)

if __name__ == "__main__":
    show()
