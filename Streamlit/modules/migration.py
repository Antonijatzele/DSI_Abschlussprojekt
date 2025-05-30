import streamlit as st
import leafmap.foliumap as leafmap
import geopandas as gpd
from pathlib import Path


def show():
    st.title("📈 Migration: Demografische & Geografische Analyse")
    st.header("👥 Entwicklung der Migrantenzahlen")
    st.markdown("""
    - Zeitliche Entwicklung und Anteil an der Gesamtbevölkerung  
    - Einfluss politischer und wirtschaftlicher Ereignisse  
    """)
    st.header("🌍 Herkunftsländer")
    st.markdown("""
    - Wichtigste Herkunftsländer und deren Entwicklung  
    - Veränderungen über die Zeit hinweg  
    """)
    st.header("🗺️ Regionale Verteilung")
    st.markdown("""
    - Verteilung auf Bundesländer und Landkreise  
    - Visualisierung mittels Karten  
    - Korrelation mit sozioökonomischen Faktoren wie Arbeitslosenquote oder Bevölkerungsdichte  
    """)

    st.header('Kartentest')
    m = leafmap.Map(center=[51.1657, 10.4515], zoom=6)
    m.add_basemap("CartoDB.DarkMatter")
    m.add_geojson(Path(__file__).parent / "data/kreise.geojson")
    m.to_streamlit(width=500, height=700, add_layer_control=True)
