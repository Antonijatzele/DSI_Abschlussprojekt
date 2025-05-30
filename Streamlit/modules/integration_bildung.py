import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
import numpy as np
import geopandas as gpd

def show():
    st.title("🎓 Integration: Bildung")
    st.set_page_config(layout="wide")
    
    # Daten einlesen
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=',')
    
    # Vorverarbeitung
    df = df.drop(columns=['Staatsangehoerigkeit'])
    df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})
    
    # Auswahl für Schuljahr
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
    
    # GeoJSON laden
    url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json"
    bundeslaender = gpd.read_file(url)
    bundeslaender['Anteil (%)'] = bundeslaender['name'].map(anteile)
    
    # Plot vorbereiten
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    bundeslaender.plot(
        column='Anteil (%)',
        cmap='Blues',
        linewidth=0.8,
        edgecolor='0.8',
        legend=True,
        legend_kwds={'label': "Anteil ausländischer Schüler/innen (%)"},
        ax=ax
    )
    
    # Beschriftung
    for idx, row in bundeslaender.iterrows():
        if pd.notna(row['Anteil (%)']):
            x = row['geometry'].centroid.x
            y = row['geometry'].centroid.y
            ax.text(
                x, y, row['name'],
                horizontalalignment='center',
                fontsize=8,
                color='black',
                weight='bold'
            )
    
    ax.set_title(f"Anteil ausländischer Schüler/innen pro Bundesland ({jahr})", fontsize=14)
    ax.axis("off")
    plt.tight_layout()
    
    # In Streamlit anzeigen
    st.pyplot(fig)

