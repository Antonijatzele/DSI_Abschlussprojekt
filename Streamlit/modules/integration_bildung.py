import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium


def show():
    st.title("🎓 Integration: Bildung")

    # Daten einlesen
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=',')

    # Vorverarbeitung
    df = df.drop(columns=['Staatsangehoerigkeit'])
    df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})

    # Auswahl für Schuljahr – Standard: 2023/24
    schuljahre = sorted(df["Schuljahr"].unique())
    default_index = schuljahre.index("2023/24") if "2023/24" in schuljahre else 0
    jahr = st.selectbox("Wähle ein Schuljahr", schuljahre, index=default_index)

    # Berechne sortierte Schularten basierend auf Anteil ausländischer Schüler/innen (für 2023/24)
    df_temp = df[
        (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
        (df['Bundesland'] != 'Deutschland') &
        (df['Schuljahr'] == "2023/24") &
        (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
    ]

    if "Schulart" in df_temp.columns:
        pivot_schulart = df_temp.pivot_table(
            index='Schulart',
            columns='Staatsangehoerigkeit',
            values='Schueler_innen_Anzahl',
            aggfunc='sum',
            fill_value=0
        )

        pivot_schulart['gesamt'] = pivot_schulart['deutsche Schüler/innen'] + pivot_schulart['ausländische Schüler/innen']
        pivot_schulart['anteil_auslaendisch'] = (pivot_schulart['ausländische Schüler/innen'] / pivot_schulart['gesamt']) * 100
        sortierte_schularten = pivot_schulart.sort_values(by='anteil_auslaendisch', ascending=False).index.tolist()
    else:
        sortierte_schularten = []

    schularten = ["Alle"] + sortierte_schularten
    ausgewaehlte_schulart = st.selectbox("Wähle eine Schulart", schularten)

    # Filter
    df_filtered = df[
        (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
        (df['Bundesland'] != 'Deutschland') &
        (df['Schuljahr'] == jahr) &
        (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
    ]

    if ausgewaehlte_schulart != "Alle":
        df_filtered = df_filtered[df_filtered['Schulart'] == ausgewaehlte_schulart]

    # Pivot-Tabelle gesamt
    pivot = df_filtered.pivot_table(
        index=['Bundesland', 'Geschlecht'],
        columns='Staatsangehoerigkeit',
        values='Schueler_innen_Anzahl',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Gesamtdaten je Bundesland
    gesamt_bundesland = pivot.groupby('Bundesland')[['deutsche Schüler/innen', 'ausländische Schüler/innen']].sum()
    gesamt_bundesland['gesamt_gesamt'] = (
        gesamt_bundesland['deutsche Schüler/innen'] + gesamt_bundesland['ausländische Schüler/innen']
    )
    anteile = (gesamt_bundesland['ausländische Schüler/innen'] / gesamt_bundesland['gesamt_gesamt']) * 100

    # Namensmapping
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

    # Geschlechterverteilung bei ausländischen Schüler/innen
    pivot_geschlecht = df_filtered.pivot_table(
        index=['Bundesland', 'Staatsangehoerigkeit'],
        columns='Geschlecht',
        values='Schueler_innen_Anzahl',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    ausl_pivot = pivot_geschlecht[pivot_geschlecht['Staatsangehoerigkeit'] == 'ausländische Schüler/innen']
    ausl_pivot['gesamt_ausl'] = ausl_pivot['männlich'] + ausl_pivot['weiblich']
    ausl_pivot['Anteil weiblich (%)'] = (ausl_pivot['weiblich'] / ausl_pivot['gesamt_ausl']) * 100
    ausl_pivot['Anteil männlich (%)'] = (ausl_pivot['männlich'] / ausl_pivot['gesamt_ausl']) * 100

    ausl_geschlecht = ausl_pivot.set_index('Bundesland')[['Anteil weiblich (%)', 'Anteil männlich (%)']]

    # GeoJSON laden
    url_geo = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json"
    bundeslaender = gpd.read_file(url_geo)

    # Spalten hinzufügen
    bundeslaender['Anteil (%)'] = bundeslaender['name'].map(anteile)
    bundeslaender['Anteil weiblich (%)'] = bundeslaender['name'].map(ausl_geschlecht['Anteil weiblich (%)'])
    bundeslaender['Anteil männlich (%)'] = bundeslaender['name'].map(ausl_geschlecht['Anteil männlich (%)'])

    # Rundung
    for col in ['Anteil (%)', 'Anteil weiblich (%)', 'Anteil männlich (%)']:
        bundeslaender[col] = bundeslaender[col].round(1)

    # Farbskala
    vmin = bundeslaender['Anteil (%)'].min()
    vmax = bundeslaender['Anteil (%)'].max()

    blue_colors = [
        '#b1bcfa',
        '#91a1fa',
        '#2b3fab',
        '#111e63',
        '#081661'
    ]

    colormap = cm.LinearColormap(
        colors=blue_colors,
        vmin=vmin,
        vmax=vmax
    )
    colormap.caption = 'Anteil ausländischer Schüler/innen (%)'

    # Karte erstellen
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB positron')

    def style_function(feature):
        anteil = feature['properties']['Anteil (%)']
        return {
            'fillOpacity': 0.7,  # Opazität auf 70%
            'weight': 1,
            'color': 'black',
            'fillColor': colormap(anteil) if anteil is not None else 'lightgray'
        }

    tooltip = folium.GeoJsonTooltip(
        fields=['name', 'Anteil (%)', 'Anteil weiblich (%)', 'Anteil männlich (%)'],
        aliases=[
            'Bundesland:',
            'Ausländische Schüler/innen (%):',
            'davon weiblich (%):',
            'davon männlich (%):'
        ],
        localize=True,
        labels=True,
        sticky=False,
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

    # Hinweis: Bundesland-Beschriftungen wurden entfernt

    colormap.add_to(m)

    # In Streamlit anzeigen
    st.subheader(f"Anteil ausländischer Schüler/innen nach Bundesland ({jahr})")
    st_data = st_folium(m, width=1000, height=700)