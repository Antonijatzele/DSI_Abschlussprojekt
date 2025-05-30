import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cm
from streamlit_folium import folium_static

st.set_page_config(layout="wide")  

def show():
    st.title("🎓 Integration: Bildung")
    st.header("Anteil ausländischer Schüler pro Bundesland")

    
    # Daten einlesen
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=',')
    
    # Vorverarbeitung
    df = df.drop(columns=['Staatsangehoerigkeit'])
    df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})
    
    # Auswahl Schuljahr
    jahr = st.selectbox("Wähle ein Schuljahr", sorted(df["Schuljahr"].unique()), index=0)
    
    # Filter
    df_filtered = df[
        (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
        (df['Bundesland'] != 'Deutschland') &
        (df['Schuljahr'] == jahr) &
        (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
    ]
    
    # Pivot
    pivot = df_filtered.pivot_table(
        index=['Bundesland', 'Geschlecht'],
        columns='Staatsangehoerigkeit',
        values='Schueler_innen_Anzahl',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    gesamt_bundesland = pivot.groupby('Bundesland')[['deutsche Schüler/innen', 'ausländische Schüler/innen']].sum()
    gesamt_bundesland['gesamt_gesamt'] = (
        gesamt_bundesland['deutsche Schüler/innen'] + gesamt_bundesland['ausländische Schüler/innen']
    )
    anteile = (gesamt_bundesland['ausländische Schüler/innen'] / gesamt_bundesland['gesamt_gesamt']) * 100
    
    # Namensmapping (falls notwendig)
    name_mapping = {
        'Baden-Württemberg': 'Baden-Württemberg',
        'Bayern': 'Bayern',
        'Berlin': 'Berlin',
        'Brandenburg': 'Brandenburg',
        'Bremen': 'Bremen',
        'Hamburg': 'Hamburg',
        'Hessen': 'Hessen',
        'Mecklenburg-Vorpommern': 'Mecklenburg-Vorpommern',
        'Niedersachsen': 'Niedersachsen',
        'Nordrhein-Westfalen': 'Nordrhein-Westfalen',
        'Rheinland-Pfalz': 'Rheinland-Pfalz',
        'Saarland': 'Saarland',
        'Sachsen': 'Sachsen',
        'Sachsen-Anhalt': 'Sachsen-Anhalt',
        'Schleswig-Holstein': 'Schleswig-Holstein',
        'Thüringen': 'Thüringen'
    }
    anteile.index = anteile.index.map(name_mapping)
    
    # GeoJSON Bundesländer laden
    url_geojson = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json"
    bundeslaender = gpd.read_file(url_geojson)
    bundeslaender['Anteil (%)'] = bundeslaender['name'].map(anteile)
    
    # Werte für Farbskala
    vmin = bundeslaender['Anteil (%)'].min()
    vmax = bundeslaender['Anteil (%)'].max()
    
    # Navy-Farbskala (hell nach dunkel)
    blue_colors = ['#cbcef5', '#9fa4e0', '#494e91', '#111654', '#000430']
    colormap = cm.LinearColormap(
        colors=blue_colors,
        vmin=vmin,
        vmax=vmax,
        caption='Anteil ausländischer Schüler/innen (%)'
    )
    
    # Folium-Karte erstellen
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB positron')
    
    def style_function(feature):
        anteil = feature['properties']['Anteil (%)']
        return {
            'fillOpacity': 0.7,
            'weight': 1,
            'color': 'black',
            'fillColor': colormap(anteil) if anteil is not None else 'gray'
        }

    # Neuer Tooltip mit einem Template-String (custom)
    tooltip = folium.GeoJsonTooltip(
        fields=['name', 'Anteil (%)'],
        aliases=['', ''],
        labels=False,
        sticky=False,
        localize=True,
        style="""
            background-color: #F0EFEF;
            border: 1px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """
    )
    
    folium.GeoJson(
        bundeslaender,
        style_function=style_function,
        tooltip=tooltip
    ).add_to(m)
    
    # Mit etwas JS im Tooltip (optional), kannst du den Text formatieren,
    # aber Folium Tooltip nimmt keine Kombi von Feldern als 1 String,
    # deshalb etwas tricksen oder Tooltip weglassen und stattdessen Popup benutzen.
    
    # Karte anzeigen
    folium_static(m)
