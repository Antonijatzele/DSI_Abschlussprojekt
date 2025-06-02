import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt


def show():
    st.title("🎓 Bildungs-Integration")

    # Daten einlesen
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=',')

    # Vorverarbeitung
    df = df.drop(columns=['Staatsangehoerigkeit'])
    df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})

    ######################################################################################################
    # Viz 1: Karte Deutschlands
    # Wie verteilen sich die ausländischen Schüler auf die Bundesländer?

    # Auswahl für Schuljahr – Standard: 2023/24
    schuljahre = sorted(df["Schuljahr"].unique())
    default_index = schuljahre.index("2023/24") if "2023/24" in schuljahre else 0
    jahr = st.selectbox("Wähle ein Schuljahr", schuljahre, index=default_index)

    # Nur relevante Daten für Filterung vorbereiten
    df_filter_basis = df[
        (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
        (df['Bundesland'] != 'Deutschland') &
        (df['Schuljahr'] == jahr) &
        (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
    ]

    # Dynamische Filterlogik
    alle_bildungsbereiche = sorted(df_filter_basis["Bildungsbereich"].dropna().unique().tolist())
    alle_schularten = sorted(df_filter_basis["Schulart"].dropna().unique().tolist())

    ausgewaehlter_bildungsbereich = st.selectbox("Wähle einen Bildungsbereich", ["Alle"] + alle_bildungsbereiche)

    # Schularten abhängig vom Bildungsbereich
    if ausgewaehlter_bildungsbereich == "Alle":
        verfuegbare_schularten = sorted(df_filter_basis["Schulart"].dropna().unique())
    else:
        verfuegbare_schularten = sorted(df_filter_basis[df_filter_basis["Bildungsbereich"] == ausgewaehlter_bildungsbereich]["Schulart"].dropna().unique())

    ausgewaehlte_schulart = st.selectbox("Wähle eine Schulart", ["Alle"] + verfuegbare_schularten)

    # Optional: Re-Filter Bildungsbereiche basierend auf Schulart
    if ausgewaehlte_schulart != "Alle":
        verfuegbare_bildungsbereiche = sorted(df_filter_basis[df_filter_basis["Schulart"] == ausgewaehlte_schulart]["Bildungsbereich"].dropna().unique())
        if ausgewaehlter_bildungsbereich != "Alle" and ausgewaehlter_bildungsbereich not in verfuegbare_bildungsbereiche:
            st.warning("Der ausgewählte Bildungsbereich passt nicht zur Schulart. Bitte anpassen.")

    # Filter anwenden
    df_filtered = df_filter_basis.copy()

    if ausgewaehlter_bildungsbereich != "Alle":
        df_filtered = df_filtered[df_filtered['Bildungsbereich'] == ausgewaehlter_bildungsbereich]

    if ausgewaehlte_schulart != "Alle":
        df_filtered = df_filtered[df_filtered['Schulart'] == ausgewaehlte_schulart]

    # Pivot-Tabelle für Schularten-Ranking (nur für 2023/24)
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

    # Pivot-Tabelle
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


    colors = [
       # '#fff5f0',  # sehr helles Rot
        '#fee0d2',
        '#fcbba1',
        #'#fc9272',
        '#fb6a4a',
        '#cb181d' ,  # dunkleres Rot
        '#2e2828'
    ]

    colormap = cm.LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax
    )
    colormap.caption = 'Anteil ausländischer Schüler/innen (%)'

    # Karte erstellen
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB positron')

    def style_function(feature):
        anteil = feature['properties']['Anteil (%)']
        return {
            'fillOpacity': 0.7,
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

    colormap.add_to(m)

    # In Streamlit anzeigen
    st.subheader(f"Anteil ausländischer Schüler/innen nach Bundesland ({jahr})")
    st_data = st_folium(m, width=1000, height=700)

    #############################################################################
    # Viz 2: Balkendiagramm: Anteil ausländischer Schüler pro Schulart (horizontal)
    #############################################################################

    # Daten vorbereiten
    df_plot = df_filtered.groupby(['Schulart', 'Staatsangehoerigkeit'])['Schueler_innen_Anzahl'].sum().reset_index()
    df_plot = df_plot[(df_plot['Schulart'].notna()) & (df_plot['Schulart'] != 'Insgesamt')]
    df_plot = df_plot[df_plot['Schulart'] != 'Keine Zuordnung zu einer Schulart möglich']

    # Gesamtanzahl pro Schulart berechnen
    df_total = df_plot.groupby('Schulart')['Schueler_innen_Anzahl'].sum().reset_index().rename(
        columns={'Schueler_innen_Anzahl': 'Gesamt'})

    # Mit den ursprünglichen Werten zusammenführen
    df_plot = df_plot.merge(df_total, on='Schulart')
    df_plot['Anteil'] = df_plot['Schueler_innen_Anzahl'] / df_plot['Gesamt'] * 100

    # Nur ausländische Schüler/innen behalten
    df_auslaendisch = df_plot[df_plot['Staatsangehoerigkeit'] == 'ausländische Schüler/innen']

    # Nach Anteil aufsteigend sortieren (für horizontalen Balken)
    df_auslaendisch = df_auslaendisch.sort_values(by='Anteil', ascending=True)

    # Farben definieren
    farben = sns.color_palette("Set2")
    orange = farben[1]  # Index 1 = Orange

    # Plot erstellen
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    y = range(len(df_auslaendisch))
    werte = df_auslaendisch['Anteil'].values
    schularten = df_auslaendisch['Schulart'].values

    # Horizontale Balken zeichnen
    bars = ax.barh(y, werte, height=0.6, label='ausländische Schüler/innen', color=orange)

    # Prozentwerte rechts neben den Balken anzeigen
    for bar, wert in zip(bars, werte):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{wert:.1f}%",
            va='center',
            ha='left',
            color='white',
            fontsize=10,
            fontweight='bold'
        )

    # Achsenbeschriftungen
    ax.set_yticks(y)
    ax.set_yticklabels(schularten, color='white', fontsize=10)
    ax.set_ylabel("")  # Y-Achsentitel entfernen
    ax.set_xlabel("")  # Optional: X-Achsentitel ebenfalls entfernen
    ax.set_title("Anteil ausländischer Schüler/innen pro Schulart", color='white')
    ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')

    # Gitterlinien
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='white')

    # X-Achse entfernen
    ax.xaxis.set_visible(False)

    # Plot anzeigen
    st.pyplot(fig)