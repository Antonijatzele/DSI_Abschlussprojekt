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
    st.header("Geographische Verteilung")


    st.subheader('Kreise')
    geojson_str, colormap = lade_geodaten()
    m = erstelle_karte(geojson_str)
    
    # Farbskala (Legende) zur Karte hinzufügen
    colormap.add_to(m)

    # Karte anzeigen
    map_data = st_folium(m, width=700, height=700)


    st.markdown("Quelle: [Destatis - Ausländerstatistik](https://www-genesis.destatis.de/datenbank/online/statistic/12521/details)")

if __name__ == "__main__":
    show()
