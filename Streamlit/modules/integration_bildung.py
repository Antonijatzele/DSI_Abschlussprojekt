
import numpy as np
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

    # Daten einlesen: Destatis 21111-03
    # Schüler/-innen (Deutsche, Ausländer/-innen) nach Bildungsbereichen, rechtlichem Status der Schule, Schularten und Geschlecht
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=',')

    # Vorverarbeitung
    df = df.drop(columns=['Staatsangehoerigkeit'])
    df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})



    ######################################################################################################
    # Viz 1: Karte Deutschlands
    # Wie verteilen sich die ausländischen Schüler auf die Bundesländer?

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        schuljahre = sorted(df["Schuljahr"].unique())
        default_index = schuljahre.index("2023/24") if "2023/24" in schuljahre else 0
        jahr = st.selectbox("Wähle ein Schuljahr", schuljahre, index=default_index)

    with col2:
        # Nur relevante Daten für Filterung vorbereiten
        df_filter_basis = df[
            (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
            (df['Bundesland'] != 'Deutschland') &
            (df['Schuljahr'] == jahr) &
            (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
            ]

        alle_bildungsbereiche = sorted(df_filter_basis["Bildungsbereich"].dropna().unique().tolist())
        ausgewaehlter_bildungsbereich = st.selectbox("Wähle einen Bildungsbereich", ["Alle"] + alle_bildungsbereiche)

    with col3:
        if ausgewaehlter_bildungsbereich == "Alle":
            verfuegbare_schularten = sorted(df_filter_basis["Schulart"].dropna().unique())
        else:
            verfuegbare_schularten = sorted(
                df_filter_basis[df_filter_basis["Bildungsbereich"] == ausgewaehlter_bildungsbereich][
                    "Schulart"].dropna().unique()
            )
        ausgewaehlte_schulart = st.selectbox("Wähle eine Schulart", ["Alle"] + verfuegbare_schularten)

        # Optional: Re-Filter Bildungsbereiche basierend auf Schulart
        if ausgewaehlte_schulart != "Alle":
            verfuegbare_bildungsbereiche = sorted(
                df_filter_basis[df_filter_basis["Schulart"] == ausgewaehlte_schulart][
                    "Bildungsbereich"].dropna().unique()
            )
            if ausgewaehlter_bildungsbereich != "Alle" and ausgewaehlter_bildungsbereich not in verfuegbare_bildungsbereiche:
                st.warning("Der ausgewählte Bildungsbereich passt nicht zur Schulart. Bitte anpassen.")

    with col4:
        # Filter als Dropdowns (selectbox) ohne Sidebar
        bundesland_options = df['Bundesland'].unique()
        selected_bundesland = st.selectbox(
            "Bundesland auswählen",
            bundesland_options,
            index=list(bundesland_options).index('Deutschland') if 'Deutschland' in bundesland_options else 0
        )



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
        '#FDD8C7',
        '#FDB79D',
        '#FC8D62',
        '#E67654',
        '#CC6140',  # dunkleres Rot
        '#A84B2E'
    ]

    colormap = cm.LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax
    )
    colormap.caption = 'Anteil ausländischer Schüler/innen (%)'

    # Karte erstellen
    # m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB positron')
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB dark_matter')

    def style_function(feature):
        anteil = feature['properties']['Anteil (%)']
        return {
            'fillOpacity': 0.8,
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
    #st.subheader(f"Anteil ausländischer Schüler/innen nach Bundesland ({jahr})")
    #fig1 = st_folium(m, width=1000, height=700)

    #############################################################################
    # Viz 2: Balkendiagramm: Anteil ausländischer Schüler pro Schulart (horizontal)
    #############################################################################

    # Daten vorbereiten (wie in deinem Originalcode)
    df_plot = df_filtered.groupby(['Schulart', 'Staatsangehoerigkeit'])['Schueler_innen_Anzahl'].sum().reset_index()
    df_plot = df_plot[(df_plot['Schulart'].notna()) & (df_plot['Schulart'] != 'Insgesamt')]
    df_plot = df_plot[df_plot['Schulart'] != 'Keine Zuordnung zu einer Schulart möglich']

    df_total = df_plot.groupby('Schulart')['Schueler_innen_Anzahl'].sum().reset_index().rename(
        columns={'Schueler_innen_Anzahl': 'Gesamt'})
    df_plot = df_plot.merge(df_total, on='Schulart')
    df_plot['Anteil'] = df_plot['Schueler_innen_Anzahl'] / df_plot['Gesamt'] * 100

    df_auslaendisch = df_plot[df_plot['Staatsangehoerigkeit'] == 'ausländische Schüler/innen']
    df_auslaendisch = df_auslaendisch.sort_values(by='Anteil', ascending=True)  # Für horizontalen Plot aufsteigend

    # Farben
    farben = sns.color_palette("Set2")
    orange = farben[1]

    # Horizontalen Balkendiagramm-Plot erstellen
    fig2, ax = plt.subplots(figsize=(8, 8), edgecolor='none')
    fig2.patch.set_facecolor('black')
    fig2.patch.set_linewidth(0)
    ax.set_facecolor('black')

    y = range(len(df_auslaendisch))
    werte = df_auslaendisch['Anteil'].values
    schularten = df_auslaendisch['Schulart'].values

    bars = ax.barh(y, werte, height=0.8, color=orange, label='ausländische Schüler/innen')  # breitere Balken

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

    # Achsen und Beschriftungen
    ax.set_yticks(y)
    ax.set_xticks([])
    ax.set_yticklabels(schularten, color='white', fontsize=10)
    ax.set_ylabel('')
    ax.set_xlabel('')
    #ax.set_title("Anteil ausländischer Schüler/innen pro Schulart", color='white')

    # Rahmen entfernen
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Gitterlinien auf der x-Achse (optional)
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='white')

    # Achsenticks und Rahmenfarbe anpassen
    # ax.tick_params(colors='white')

    plt.tight_layout()

    # st.pyplot(fig2)


    # st.pyplot(fig2)
    # die Diagramme in 2x2 Columns anzeigen
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Anteil ausländischer Schüler nach Bundesland")
        fig1 = st_folium(m, width=1000, height=700)

    with col2:
        st.subheader("Anteil ausländischer Schüler nach Schulart")
        # Diagramm 2 anzeigen
        st.pyplot(fig2)


    ###############################################################################
    # Daten einlesen: Destatis 21111-08
    # Ausländische Schüler/-innen nach Schularten, Staatsangehörigkeit und Geschlecht
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/Destatis_21111-08_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=',')

    # Die ersten zwei Spalten löschen
    df = df.drop(df.columns[:2], axis=1)

    # 'Syrien, Arabische Republik' in 'Syrien' umbenennen
    df['Staatsangehoerigkeit'] = df['Staatsangehoerigkeit'].replace('Syrien, Arabische Republik', 'Syrien')

    # Filter als Dropdowns (selectbox) ohne Sidebar
    bundesland_options_2 = df['Bundesland'].unique()
    selected_bundesland_2 = st.selectbox(
        "Bundesland auswählen 2",
        bundesland_options_2,
        index=list(bundesland_options_2).index('Deutschland') if 'Deutschland' in bundesland_options_2 else 0
    )

    # Staatsangehörigkeit Filter entfernt

    schulart_options_2 = df['Schulart'].unique()
    selected_schulart_2 = st.selectbox("Schulart auswählen 2",
                                     ['Alle'] + list(schulart_options_2), index=0)

    # Filter anwenden
    df_filtered = df[df['Bundesland'] == selected_bundesland_2]

    if selected_schulart_2 != 'Alle':
        df_filtered = df_filtered[df_filtered['Schulart'] == selected_schulart]

    # 'Insgesamt' rauslassen (falls noch drin)
    df_filtered = df_filtered[df_filtered['Staatsangehoerigkeit'] != 'Insgesamt']

    # Gruppieren und aufsummieren
    df_grouped = df_filtered.groupby('Staatsangehoerigkeit')['auslaendische_Schueler_innen_Anzahl'].sum().reset_index()

    # Gesamtanzahl für die Prozentrechnung
    gesamt_anzahl = df_grouped['auslaendische_Schueler_innen_Anzahl'].sum()

    # Prozentanteil berechnen
    df_grouped['Prozent'] = (df_grouped['auslaendische_Schueler_innen_Anzahl'] / gesamt_anzahl) * 100

    # Top 10 nach Prozentanteil auswählen
    df_top10 = df_grouped.sort_values(by='Prozent', ascending=False).head(10)

    ########################################################################
    # Viz 4: Kreisdiagramm
    plt.style.use('dark_background')
    fig3, ax = plt.subplots(figsize=(8, 8))

    plt.pie(
        df_top10['Prozent'],
        labels=df_top10['Staatsangehoerigkeit'],
        autopct='%1.1f%%',
        startangle=140,
        colors=['#fc8d62'] * len(df_top10),
        wedgeprops={'edgecolor': 'black', 'linewidth': 2},  # Schwarze Trennlinien mit Breite 2
        textprops={'color': "white", 'fontsize': 12}
    )
    # ax.set_title(f'Top 10 Staatsangehörigkeiten im Bundesland {selected_bundesland} (in %)', color='white')
    fig3.tight_layout()

    ##################################################################
    # Daten einlesen: Destatis 21111-12
    # Absolvierende / Abgehende (Deutsche, Ausländer/-innen) nach Abschluss-, Schularten, Klassen-/Jahrgangsstufen und Geschlecht (einschl. Externe)
    url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/Destatis_21111-12_allgemeinbildende_schulen_2021_2023_zusammengefuegt.csv"
    df = pd.read_csv(url, sep=';')

    # Die ersten zwei Spalten löschen
    df = df.drop(df.columns[:2], axis=1)

    # Spalte umbenennen, um das Leerzeichen loszuwerden
    df = df.rename(columns={
        'auslaendische_Absolvierende_und_Abgehende _Anzahl': 'auslaendische_Absolvierende_und_Abgehende_Anzahl'
    })

    # in Typ float umwandeln
    df['Absolvierende_und_Abgehende_Anzahl'] = pd.to_numeric(
        df['Absolvierende_und_Abgehende_Anzahl'], errors='coerce'
    )

    df['auslaendische_Absolvierende_und_Abgehende_Anzahl'] = pd.to_numeric(
        df['auslaendische_Absolvierende_und_Abgehende_Anzahl'], errors='coerce'
    )

    #####################################################
    # Balkendiagramm: Prozentualer Anteil der ausländischen Absolventen nach Abschluss
    df = df[df['Abschluss'] != 'ohne Hauptschulabschluss']
    df['Abschluss'] = df['Abschluss'].replace('mittlerer Abschluss', 'Mittlerer Abschluss')

    # Deutsche Absolventen berechnen
    df['deutsche_Absolvierende'] = df['Absolvierende_und_Abgehende_Anzahl'] - df[
        'auslaendische_Absolvierende_und_Abgehende_Anzahl']

    # Gruppierung nach Abschluss
    df_grouped = df.groupby('Abschluss').agg({
        'deutsche_Absolvierende': 'sum',
        'auslaendische_Absolvierende_und_Abgehende_Anzahl': 'sum'
    }).reset_index()

    # Gesamtsummen für Prozentberechnung
    gesamt_auslaender = df_grouped['auslaendische_Absolvierende_und_Abgehende_Anzahl'].sum()
    gesamt_deutsche = df_grouped['deutsche_Absolvierende'].sum()

    # Prozentwerte
    df_grouped['Prozent_auslaender'] = (df_grouped[
                                            'auslaendische_Absolvierende_und_Abgehende_Anzahl'] / gesamt_auslaender) * 100
    df_grouped['Prozent_deutsche'] = (df_grouped['deutsche_Absolvierende'] / gesamt_deutsche) * 100

    # Sortieren nach Anteil Ausländer absteigend
    grouped_sorted = df_grouped.sort_values(by='Prozent_auslaender', ascending=False).reset_index(drop=True)

    # Plot mit Matplotlib
    fig4, ax = plt.subplots(figsize=(8, 8))

    bars_auslaender = ax.bar(grouped_sorted['Abschluss'], grouped_sorted['Prozent_auslaender'],
                             label='Ausländisch', color='#fc8d62')
    bars_deutsche = ax.bar(grouped_sorted['Abschluss'], grouped_sorted['Prozent_deutsche'],
                           bottom=grouped_sorted['Prozent_auslaender'], label='Deutsch', color='#66c2a5')

    # Prozentwerte in die Balken schreiben, nur wenn größer 5% für bessere Lesbarkeit
    for bar, wert in zip(bars_auslaender, grouped_sorted['Prozent_auslaender']):
        if wert > 5:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                    f'{wert:.1f}%', ha='center', va='center', color='white', fontsize=9)

    for bar, wert, bottom in zip(bars_deutsche, grouped_sorted['Prozent_deutsche'],
                                 grouped_sorted['Prozent_auslaender']):
        if wert > 5:
            ax.text(bar.get_x() + bar.get_width() / 2, bottom + bar.get_height() / 2,
                    f'{wert:.1f}%', ha='center', va='center', color='black', fontsize=9)

    # Y-Achse und Titel entfernen
    ax.yaxis.set_visible(False)
    ax.set_title('')  # Leer, damit nichts angezeigt wird

    # X-Achsenbeschriftung drehen
    ax.set_xticks(range(len(grouped_sorted['Abschluss'])))
    ax.set_xticklabels(grouped_sorted['Abschluss'], rotation=45, ha='right')

    # Legende anzeigen
    ax.legend()
    # **Weißer Rahmen entfernen:**
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()

    # Streamlit Ausgabe
    #st.pyplot(fig4)
    ###############################################################

    # zweite Zeile (nochmal 2 Spalten)
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Top 10 Staatsangehörigkeiten")
        # Diagramm 3 anzeigen
        st.pyplot(fig3)

    with col4:
        st.subheader("Anteil Absolventen")
        # Diagramm 4 anzeigen
        st.pyplot(fig4)