import streamlit as st
import folium
import branca.colormap as cm
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium

st.header('Kartentest')

# Geodaten laden
@st.cache_data
def lade_geodaten():
    gdf = gpd.read_file(Path(__file__).parent / "data/kreise_mit_daten.geojson")
    gdf = gdf.to_crs("EPSG:4326")

    # Farbskala erstellen
    colormap = cm.linear.YlGnBu_09.scale(7, gdf['Anteil_Zahl'].max())
    colormap.caption = 'Wert pro Region'  # Beschriftung der Legende

    # Farben auf Basis der Skala zuweisen
    gdf['color'] = gdf['Anteil_Zahl'].apply(colormap)

    return gdf.to_json()
geojson_str = lade_geodaten()


# Karte erstellen
@st.cache_resource
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
m = erstelle_karte(geojson_str)

# Farbskala (Legende) zur Karte hinzufügen
#colormap.add_to(m)

# Karte anzeigen
map_data = st_folium(m, width=700, height=700)

'''
# Wenn geklickt wurde
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.write(f"{lat} , {lon}")

    point = Point(lon, lat)

    # Zeile finden, die den Punkt enthält
    clicked_row = gdf[gdf.contains(point)]

    if not clicked_row.empty:
        st.write("Gefundenes Land:")
        st.dataframe(clicked_row[["Kreise"]])
    else:
        st.write("Kein Land gefunden.")
'''