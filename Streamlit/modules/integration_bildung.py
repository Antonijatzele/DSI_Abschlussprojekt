
import numpy as np
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go
import requests


def show():
    st.title("🎓 Integration: Bildung")

    st.markdown("""
        <style>
        /* Aktiver Tab: Orange Beschriftung */
        .stTabs [data-baseweb="tab"] button[aria-selected="true"] {
            color: orange;
        }

        /* Inaktive Tabs: Grau (optional) */
        .stTabs [data-baseweb="tab"] button[aria-selected="false"] {
            color: #888888;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
            Bildung ist einer der zentralen Faktoren für eine gelungene Integration.  
            Sie schafft Perspektiven, ermöglicht gesellschaftliche Teilhabe und trägt zur Chancengleichheit bei.  
            Besonders für Menschen mit Migrationsgeschichte ist der Zugang zu Bildung entscheidend.

            """)

    tab_kita, tab_schule, tab_abschluss = st.tabs(["Frühkindliche Bildung", "Schule", "Beruflicher Bildungsabschluss"])


    with tab_kita:

        #############################
        # Deutschlandkarte mit Anteilen pro Bundesland (Kinder mit Migrationshintergrund in Kitas)
        # CSV einlesen
        csv_url = "https://github.com/Antonijatzele/DSI_Abschlussprojekt/raw/refs/heads/main/Daten/Integration/Bildungsintegration/Kita_Migrationshintergrund_Laendermonitor_2020_2023.csv"
        df = pd.read_csv(csv_url, encoding="ISO-8859-1")
        df["Jahr"] = df["Jahr"].astype(str).str.strip().astype(int)

        # Prozentanteil berechnen
        df["Anteil (%) mit Migrationshintergrund"] = (
                df["Mit Migrationshintergrund"] / (
                    df["Mit Migrationshintergrund"] + df["Ohne Migrationshintergrund"]) * 100
        ).round(1)

        # Streamlit UI
        selected_year = st.selectbox("Jahr", sorted(df["Jahr"].unique(), reverse=True))
        filtered_df = df[df["Jahr"] == selected_year]

        st.write(f"### Anteil von Kindern mit Migrationshintergrund in Kitas ({selected_year})")

        # GeoJSON für Bundesländer (öffentlicher Link)
        geojson_url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json"
        geojson_data = requests.get(geojson_url).json()

        # Die Bundeslandnamen im GeoJSON (für matching)
        # In dem GeoJSON heißt das Bundesland-Feld 'name'
        # Prüfen, ob die Namen in df und GeoJSON übereinstimmen, evtl. anpassen
        # Beispiel: "Bayern" in df vs "Bayern" in GeoJSON, passt meistens

        # Karte initialisieren (Zentrum Deutschland)
        # Folium-Karte mit hellem Hintergrund (cartodbpositron)
        m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='cartodbpositron')

        # Choropleth-Map erstellen
        folium.Choropleth(
            geo_data=geojson_data,
            name="choropleth",
            data=filtered_df,
            columns=["Bundesland", "Anteil (%) mit Migrationshintergrund"],
            key_on="feature.properties.name",
            fill_color="OrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Anteil (%) mit Migrationshintergrund"
        ).add_to(m)

        # Optional: Tooltips mit Bundeslandnamen und Prozent anzeigen
        style_function = lambda x: {'fillColor': '#ffffff', 'color': '#000000', 'fillOpacity': 0, 'weight': 0.1}
        highlight_function = lambda x: {'fillColor': '#000000', 'color': '#000000', 'fillOpacity': 0.5, 'weight': 0.1}

        for feature in geojson_data['features']:
            bundesland_name = feature['properties']['name']
            # Anteil finden
            wert = filtered_df.loc[filtered_df["Bundesland"] == bundesland_name, "Anteil (%) mit Migrationshintergrund"]
            wert_text = f"{wert.values[0]} %" if not wert.empty else "Keine Daten"

            folium.GeoJson(
                feature,
                style_function=style_function,
                highlight_function=highlight_function,
                tooltip=folium.Tooltip(f"{bundesland_name}: {wert_text}")
            ).add_to(m)

        # Karte in Streamlit anzeigen
        st_folium(m, width=700, height=500)



        ### Linienplot
        # Bundesländer-Liste mit 'Alle' ganz vorne
        bundeslaender = sorted(df["Bundesland"].unique())
        options = ["Alle"] + bundeslaender

        # Multiselect mit Default "Alle"
        selected = st.multiselect(
            "Bundesland auswählen",
            options=options,
            default=["Alle"],
            key="Tab1_Bundesland"
        )

        # Filter-Logik: Wenn "Alle" gewählt, dann keine Filterung
        if "Alle" in selected or len(selected) == 0:
            filtered_df = df.copy()
        else:
            filtered_df = df[df["Bundesland"].isin(selected)]

        # Sortieren nach Jahr vor dem Plotten
        filtered_df = filtered_df.sort_values(by="Jahr")

        fig = px.line(
            filtered_df,
            x="Jahr",
            y="Anteil (%) mit Migrationshintergrund",
            color="Bundesland",
            markers=True,
            labels={
                "Jahr": "Jahr",
                "Anteil (%) mit Migrationshintergrund": "Anteil Kinder mit Migrationshintergrund (%)",
                "Bundesland": "Bundesland"
            },
            title="Anteil von Kindern mit Migrationshintergrund in Kitas (2020-2023)"
        )

        fig.update_layout(
            xaxis=dict(dtick=1),
            yaxis=dict(range=[0, filtered_df["Anteil (%) mit Migrationshintergrund"].max() + 5]),
            legend_title_text="Bundesland",
            plot_bgcolor="white",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)


    ##################################################################################################
    ##################################################################################################

    with tab_schule:

        # Daten einlesen: Destatis 21111-03
        # Schüler/-innen (Deutsche, Ausländer/-innen) nach Bildungsbereichen, rechtlichem Status der Schule, Schularten und Geschlecht
        url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
        df = pd.read_csv(url, sep=',')

        # Vorverarbeitung
        df = df.drop(columns=['Staatsangehoerigkeit'])
        df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})
        df = df[df['Bildungsbereich'] != 'Bereich unbekannt']
        df = df[~df['Bildungsbereich'].isin(['Ohne Zuordnung', 'Vorschulbereich'])]

        with st.expander("DataFrame anzeigen"):
            st.dataframe(df)

        ####################################
        # Diagramm 1: Karte Deutschlands   #
        ####################################
        # Wie verteilen sich die ausländischen Schüler auf die Bundesländer?

        col1, col2, col3 = st.columns(3)

        with col1:
            schuljahre = sorted(df["Schuljahr"].unique())
            default_index = schuljahre.index("2023/24") if "2023/24" in schuljahre else 0
            jahr = st.selectbox("Schuljahr", schuljahre, index=default_index)

        with col2:
            # Nur relevante Daten
            df_filter_basis = df[
                (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
                (df['Bundesland'] != 'Deutschland') &
                (df['Schuljahr'] == jahr) &
                (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
                ]

            alle_bildungsbereiche = sorted(df_filter_basis["Bildungsbereich"].dropna().unique().tolist())
            ausgewaehlter_bildungsbereich = st.selectbox("Bildungsbereich", alle_bildungsbereiche)

        with col3:
            bundesland_options = df['Bundesland'].unique()
            selected_bundesland = st.selectbox(
                "Bundesland",
                bundesland_options,
                index=list(bundesland_options).index('Deutschland') if 'Deutschland' in bundesland_options else 0
            )

        # Filter anwenden
        if selected_bundesland != 'Deutschland':
            df_filtered = df_filter_basis[
                (df_filter_basis["Bildungsbereich"] == ausgewaehlter_bildungsbereich) &
                (df_filter_basis["Bundesland"] == selected_bundesland)
                ]
        else:
            df_filtered = df_filter_basis[
                (df_filter_basis["Bildungsbereich"] == ausgewaehlter_bildungsbereich)
            ]

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

            pivot_schulart['gesamt'] = pivot_schulart['deutsche Schüler/innen'] + pivot_schulart[
                'ausländische Schüler/innen']
            pivot_schulart['anteil_auslaendisch'] = (pivot_schulart['ausländische Schüler/innen'] / pivot_schulart[
                'gesamt']) * 100
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

        colors = ['#fff7ec',  # sehr helles Orange
                  '#fee8c8',  # helles Orange
                  '#fdd49e',  # mittleres Orange
                  '#fdbb84',  # dunkleres Orange
                  '#fc8d59',  # Orange-Rot
                  '#e34a33',  # kräftiges Rot-Orange
                  '#b30000']  # dunkles Rot

        colormap = cm.LinearColormap(
            colors=colors,
            vmin=vmin,
            vmax=vmax
        )
        colormap.caption = 'Anteil ausländischer Schüler/innen (%)'

        # Karte erstellen
        # m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB positron')
        # Karte erstellen mit korrektem Tile-Namen für hellen Hintergrund
        m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='cartodbpositron')

        def style_function(feature):
            anteil = feature['properties']['Anteil (%)']
            return {
                'fillOpacity': 0.6,
                'weight': 1,
                'color': 'black',
                'fillColor': colormap(anteil) if anteil is not None else 'lightgrey'
            }

        # Neue Spalte mit Prozentzahl und Prozentzeichen als String
        bundeslaender['Anteil_text'] = bundeslaender['Anteil (%)'].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "n/a")

        # Tooltip anpassen: nur eine Zeile mit "Bundesland: XX.X%"
        tooltip = folium.GeoJsonTooltip(
            fields=['name', 'Anteil (%)'],
            aliases=['', ''],  # Leere Aliases, damit wir nur einen custom Text bauen
            localize=True,
            labels=False,  # Keine Labels, nur den Wert anzeigen
            sticky=False,
            style="""
                background-color: #F0EFEF;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px;
                color: black;
                font-weight: bold;
                text-align: center;
            """,
            # custom HTML-Formatierung über tooltip-Funktion
            # Alternativ einfacher: Tooltip über "tooltip" Parameter anpassen (weiter unten)
        )

        def tooltip_function(feature):
            name = feature['properties']['name']
            anteil = feature['properties']['Anteil (%)']
            if anteil is None:
                anteil_text = "keine Daten"
            else:
                anteil_text = f"{anteil:.1f}%"
            return f"{name}: {anteil_text}"

        folium.GeoJson(
            bundeslaender,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=[], labels=False, sticky=False, localize=True,
                                          toLocaleString=True,
                                          style="background-color:#F0EFEF; border:1px solid black; border-radius:3px; color:black; font-weight:bold; text-align:center;",
                                          ),
            highlight_function=lambda x: {'weight': 3, 'color': 'blue'},
            popup=None
        ).add_to(m)

        # Statt Tooltip über folium.GeoJsonTooltip einbauen, kannst du ein benutzerdefiniertes Tooltip mit Popup machen:
        geojson = folium.GeoJson(
            bundeslaender,
            style_function=style_function,
            highlight_function=lambda x: {'weight': 3, 'color': 'blue'}
        )

        geojson.add_child(folium.features.GeoJsonTooltip(
            fields=['name', 'Anteil (%)'],
            aliases=['', ''],
            labels=False,
            localize=True,
            sticky=False,
            style="""
                background-color: #F0EFEF;
                border: 1px solid black;
                border-radius: 3px;
                color: black;
                font-weight: bold;
                text-align: center;
            """,
            # custom formatieren: nutze formatters, wenn nötig (siehe unten)
        ))

        geojson.add_to(m)

        # Keine Prozentwerte als Marker hinzufügen - diesen Codeblock entfernen!
        # for _, row in bundeslaender.iterrows():
        #     if pd.notna(row['Anteil (%)']):
        #         folium.map.Marker(
        #             [row['geometry'].centroid.y, row['geometry'].centroid.x],
        #             icon=folium.DivIcon(
        #                 html=f"""
        #                     <div style="
        #                         font-size: 12px;
        #                         color: black;
        #                         font-weight: bold;
        #                         text-align: center;
        #                         background-color: transparent;
        #                         padding: 0;
        #                         border: none;
        #                     ">
        #                         {row['Anteil (%)']}%
        #                     </div>
        #                 """
        #             )
        #         ).add_to(m)
        # Colormap (Legende) hinzufügen
        colormap.add_to(m)

        # In Streamlit anzeigen
        st.subheader(f"Anteil ausländischer Schüler/innen nach Bundesland ({jahr})")
        fig1 = st_folium(m, width=1000, height=700)

        #########################################################
        # Diagramm 2: Anteil ausländischer Schüler pro Schulart #
        #                   getrennt nach Geschlecht            #
        #########################################################
        # Filter gültige Schularten
        df_filtered = df_filtered[df_filtered['Schulart'].notna()]
        df_filtered = df_filtered[
            ~df_filtered['Schulart'].isin(['Insgesamt', 'Keine Zuordnung zu einer Schulart möglich'])]

        # Gesamtzahl aller Schüler pro Schuljahr und Schulart
        df_gesamt = df_filtered.groupby(['Schuljahr', 'Schulart'])['Schueler_innen_Anzahl'].sum().reset_index()
        df_gesamt.rename(columns={'Schueler_innen_Anzahl': 'Gesamt'}, inplace=True)

        # Anzahl ausländischer Schüler pro Schuljahr und Schulart
        df_auslaender = df_filtered[df_filtered['Staatsangehoerigkeit'] == 'ausländische Schüler/innen'].copy()
        df_auslaender = df_auslaender.groupby(['Schuljahr', 'Schulart'])['Schueler_innen_Anzahl'].sum().reset_index()
        df_auslaender.rename(columns={'Schueler_innen_Anzahl': 'Auslaendisch'}, inplace=True)

        # Merge und Anteil berechnen
        df_plot = pd.merge(df_auslaender, df_gesamt, on=['Schuljahr', 'Schulart'])
        df_plot['Anteil'] = df_plot['Auslaendisch'] / df_plot['Gesamt'] * 100

        # Filter nach Jahr
        df_selected = df_plot[df_plot['Schuljahr'] == jahr].copy()

        # Sortierung: höchste Anteile oben
        df_selected = df_selected.sort_values('Anteil', ascending=False)
        sort_order = df_selected['Schulart'].tolist()
        df_selected['Schulart'] = pd.Categorical(df_selected['Schulart'], categories=sort_order, ordered=True)



        # Orange Farbe (Set2 Palette: #fc8d62)
        orange_color = '#fc8d62'

        fig = px.bar(
            df_selected,
            x='Anteil',
            y='Schulart',
            orientation='h',
            color_discrete_sequence=[orange_color],
            labels={'Anteil': '', 'Schulart': ''},
            title=f"Anteil ausländischer Schüler/innen nach Schulart ({jahr}, {selected_bundesland}, {ausgewaehlter_bildungsbereich})"
        )

        # Layout anpassen
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, autorange='reversed'),  # wichtig: um höchsten Anteil oben zu haben
            height=600,
            margin=dict(l=150, r=100, t=50, b=50),
            showlegend=False
        )

        # Anteil als Text rechts neben Balken anzeigen
        for _, row in df_selected.iterrows():
            fig.add_annotation(
                x=row['Anteil'] + 1,
                y=row['Schulart'],
                text=f"{row['Anteil']:.1f}%",
                showarrow=False,
                font=dict(size=14, color='black'),
                xanchor='left',
                yanchor='middle'
            )

        st.plotly_chart(fig, use_container_width=True)

        ######################################################
        # Nur ausländische Schüler nach Schulart und Geschlecht
        df_auslaender = df_filtered[df_filtered['Staatsangehoerigkeit'] == 'ausländische Schüler/innen']

        # Summe der ausländischen Schüler pro Schulart und Geschlecht
        df_grouped = df_auslaender.groupby(['Schulart', 'Geschlecht'])['Schueler_innen_Anzahl'].sum().reset_index()

        # Gesamt ausländische Schüler pro Schulart
        gesamt_auslaender = df_grouped.groupby('Schulart')['Schueler_innen_Anzahl'].sum().reset_index()
        gesamt_auslaender = gesamt_auslaender.rename(columns={'Schueler_innen_Anzahl': 'Gesamt_Auslaender'})

        # Merge Gesamt mit gruppierten Daten
        df_grouped = df_grouped.merge(gesamt_auslaender, on='Schulart')

        # Anteil pro Geschlecht an den ausländischen Schülern der Schulart (in %)
        df_grouped['Anteil'] = df_grouped['Schueler_innen_Anzahl'] / df_grouped['Gesamt_Auslaender'] * 100

        # Sortierung nach Gesamtzahl ausländischer Schüler pro Schulart (optional)
        sort_order = gesamt_auslaender.sort_values('Gesamt_Auslaender', ascending=True)['Schulart'].tolist()
        df_grouped['Schulart'] = pd.Categorical(df_grouped['Schulart'], categories=sort_order, ordered=True)
        df_grouped = df_grouped.sort_values(['Schulart', 'Geschlecht'])

        # Farben definieren
        color_map = {
            'weiblich': '#e76f51',
            'männlich': '#457b9d'
        }

        # Plotly Balkendiagramm (100% gestapelt)
        fig = px.bar(
            df_grouped,
            x='Anteil',
            y='Schulart',
            color='Geschlecht',
            color_discrete_map=color_map,
            orientation='h',
            barmode='stack',
            category_orders={'Schulart': sort_order},
            labels={'Anteil': 'Anteil (%)', 'Schulart': 'Schulart', 'Geschlecht': 'Geschlecht'},
            title=f"Geschlechter-Anteil an ausländischen Schüler/innen pro Schulart ({jahr})",
            text=df_grouped['Anteil'].apply(lambda x: f"{x:.1f}%")
        )

        fig.update_layout(
            xaxis=dict(
                title='Anteil (%)',
                range=[0, 100],
                ticksuffix='%'
            ),
            yaxis=dict(
                title='Schulart',
                autorange='reversed'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend_title='Geschlecht',
            height=600,
            margin=dict(l=150, r=50, t=80, b=50),
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )

        st.plotly_chart(fig, use_container_width=True)

        ###########################################
        st.subheader("Herkunftsländer")

        # Daten einlesen
        url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/Destatis_21111-08_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
        df = pd.read_csv(url, sep=',')

        # Nur gültige Einzelgeschlechter
        df = df[df["Geschlecht"] != "Insgesamt"]
        # Erste zwei Spalten löschen
        df = df.drop(df.columns[:2], axis=1)

        # 'Syrien, Arabische Republik' vereinfachen
        df['Staatsangehoerigkeit'] = df['Staatsangehoerigkeit'].replace('Syrien, Arabische Republik', 'Syrien')

        # Entferne 'Deutschland' aus Bundesland und 'Insgesamt' aus Schulart und Staatsangehörigkeit
        df = df[df['Bundesland'] != 'Deutschland']
        df = df[(df['Schulart'] != 'Insgesamt') & (df['Staatsangehoerigkeit'] != 'Insgesamt')]

        # Ursprünglichen (ungefilterten) DataFrame anzeigen
        with st.expander("DataFrame anzeigen"):
            st.dataframe(df)

        # Auswahloptionen vorbereiten
        #schuljahre = sorted(df["Schuljahr"].dropna().unique())
        schularten = sorted(df['Schulart'].dropna().unique())
        bundeslaender = sorted(df['Bundesland'].dropna().unique())

        # Filterauswahl

        col1, col2 = st.columns(2)

        with col1:
            selected_schularten = st.multiselect("Schulart wählen", options=["Alle"] + schularten, default=["Alle"], key="Herkunft_schulart")

        with col2:
            selected_bundeslaender = st.multiselect("Bundesland wählen", options=["Alle"] + bundeslaender, default=["Alle"], key="Herkunft_Bundesland")

        # Filter anwenden (falls nicht "Alle" gewählt)
        df_filtered = df.copy()
        if "Alle" not in selected_schularten:
            df_filtered = df_filtered[df_filtered['Schulart'].isin(selected_schularten)]
        if "Alle" not in selected_bundeslaender:
            df_filtered = df_filtered[df_filtered['Bundesland'].isin(selected_bundeslaender)]

        # Gruppieren und Prozentanteile berechnen
        df_grouped = (
            df_filtered
            .groupby('Staatsangehoerigkeit', as_index=False)['auslaendische_Schueler_innen_Anzahl']
            .sum()
        )

        gesamt_anzahl = df_grouped['auslaendische_Schueler_innen_Anzahl'].sum()
        if gesamt_anzahl > 0:
            df_grouped['Prozent'] = (df_grouped['auslaendische_Schueler_innen_Anzahl'] / gesamt_anzahl) * 100
        else:
            df_grouped['Prozent'] = 0

        # Top 10 anzeigen
        df_top10 = df_grouped.sort_values(by='Prozent', ascending=False).head(10)

        # Plot Anzahl ausländischer schüler (top 10 herkunftsländer)

        # Schuljahr zu Jahr umwandeln (z. B. "2021/22" → 2021)
        df['Jahr'] = df['Schuljahr'].str[:4].astype(int)

        # Grundfilter: Staatsangehörigkeit ≠ 'Insgesamt'
        df_plot_filtered = df[df['Staatsangehoerigkeit'] != "Insgesamt"]

        # Filter anwenden
        if "Alle" not in selected_schularten:
            df_plot_filtered = df_plot_filtered[df_plot_filtered['Schulart'].isin(selected_schularten)]
        if "Alle" not in selected_bundeslaender:
            df_plot_filtered = df_plot_filtered[df_plot_filtered['Bundesland'].isin(selected_bundeslaender)]

        # Gruppieren nach Jahr und Staatsangehörigkeit
        df_grouped_plot = df_plot_filtered.groupby(['Jahr', 'Staatsangehoerigkeit'], as_index=False)[
            'auslaendische_Schueler_innen_Anzahl'].sum()

        # Top 10 Herkunftsländer basierend auf gefilterten Daten
        top10_länder = (
            df_grouped_plot
            .groupby('Staatsangehoerigkeit')['auslaendische_Schueler_innen_Anzahl']
            .sum()
            .nlargest(10)
            .index
        )

        # Nur Top 10 für den Plot
        df_top10_plot = df_grouped_plot[df_grouped_plot['Staatsangehoerigkeit'].isin(top10_länder)]

        # Plot erstellen
        fig = px.line(
            df_top10_plot,
            x='Jahr',
            y='auslaendische_Schueler_innen_Anzahl',
            color='Staatsangehoerigkeit',
            markers=True,
            title='Anzahl ausländischer Schüler (Top 10 Herkunftsländer)',
            labels={
                'Jahr': 'Jahr',
                'auslaendische_Schueler_innen_Anzahl': 'Anzahl ausländischer Schüler',
                'Staatsangehoerigkeit': 'Herkunftsland'
            }
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black'),
            xaxis=dict(tickmode='linear')
        )

        # In Streamlit anzeigen
        st.plotly_chart(fig)


        ##########################################
        # Datensatz laden: Schüler, Staatsangehörigkeiten, Bundesländer, Jahre 1992-2000

        # Daten einlesen
        url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/auslaendische_Schueler_Staatsangehoerigkeit_1992_2020_aufbereitet.csv"
        df = pd.read_csv(url, sep=";")
        # Spalte umbenennen
        df.rename(columns={"Land der Staatsangehörigkeit": "Staatsangehörigkeit"}, inplace=True)

        # Datenbereinigung
        df = df[df["Staatsangehörigkeit"].notna()]
        df = df[~df["Staatsangehörigkeit"].isin(["insgesamt", "Keine Angabe und ungeklärt"])]
        df = df[df["Jahr"].notna()]
        df = df[df["Geschlecht"] == "z"]
        df = df[df["Anzahl"] != 0]
        df = df[~df["Kontinent"].isin(["Alle", "Keine Angabe und ungeklärt"])]

        # Bundesland "Deutschland" entfernen, falls vorhanden
        df = df[df["Bundesland"] != "Deutschland"]

        # Geschlecht umbenennen
        #df["Geschlecht"] = df["Geschlecht"].map({
         #   "m": "männlich",
          #  "w": "weiblich"
        #})

        # ----------------------------- #
        # Multiselect: Bundesland
        # ----------------------------- #
        bundeslaender = sorted(df["Bundesland"].unique().tolist())
        selected_bundeslaender = st.multiselect(
            "Bundesland auswählen",
            options=["Alle"] + bundeslaender,
            default=["Alle"],
            key="Tab_schule_Herkunft_Bundesland"
        )

        # Filter anwenden nur wenn nicht "Alle"
        if "Alle" in selected_bundeslaender or not selected_bundeslaender:
            filtered_df = df.copy()
        else:
            filtered_df = df[df["Bundesland"].isin(selected_bundeslaender)]

        # ----------------------------- #
        # DataFrame anzeigen
        # ----------------------------- #
        with st.expander("DataFrame anzeigen"):
            st.dataframe(filtered_df)

        # ----------------------------- #
        # Plot 1: Anzahl nach Kontinent
        # ----------------------------- #
        grouped = filtered_df.groupby(["Jahr", "Kontinent"], as_index=False)["Anzahl"].sum()

        fig = px.line(
            grouped,
            x="Jahr",
            y="Anzahl",
            color="Kontinent",
            title="Anzahl ausländischer Schüler nach Kontinent",
            markers=True
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black"),
            xaxis=dict(title="", color="black"),
            yaxis=dict(title="", color="black")
        )

        st.plotly_chart(fig)

        # ----------------------------- #
        # Plot 2: Top 10 Staatsangehörigkeiten
        # ----------------------------- #
        filtered_df = filtered_df[filtered_df["Staatsangehörigkeit"].notna()]
        filtered_df = filtered_df[filtered_df["Staatsangehörigkeit"] != "insgesamt"]
        filtered_df = filtered_df[filtered_df["Jahr"].notna()]

        top10 = (
            filtered_df.groupby("Staatsangehörigkeit")["Anzahl"]
            .sum()
            .nlargest(10)
            .index
        )

        df_agg = (
            filtered_df[filtered_df["Staatsangehörigkeit"].isin(top10)]
            .groupby(["Jahr", "Staatsangehörigkeit"], as_index=False)
            .agg({"Anzahl": "sum"})
        )

        fig = px.line(
            df_agg,
            x="Jahr",
            y="Anzahl",
            color="Staatsangehörigkeit",
            title="Anzahl ausländischer Schüler (Top 10 Staatsangehörigkeiten)",
            markers=True
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black"),
            xaxis_title="",
            yaxis_title=""
        )

        st.plotly_chart(fig)





        st.subheader("Schulabschlüsse")
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

        with st.expander("DataFrame anzeigen"):
            st.dataframe(df)

        #########################################################################################
        # Diagramm 4 Prozentualer Anteil der deutschen/ausländischen Absolventen nach Abschluss #
        #########################################################################################
        df['Abschluss'] = df['Abschluss'].replace('mittlerer Abschluss', 'Mittlerer Abschluss')
        df.loc[df[
                   'Abschluss2'] == 'dar.: mit schulischem Teil der Fachhochschulreife', 'Abschluss'] = 'Fachhochschulreife'

        jahre = sorted(df['Abgangsjahr'].unique())
        selected_jahr = st.selectbox(
            "Jahr",
            options=jahre,
            index=len(jahre) - 1,  # letztes Jahr vorausgewählt
            key="Tab_Abschluss_Jahr"
        )


        df_filtered_12 = df[df['Abgangsjahr'] == selected_jahr]

        df_filtered_12['deutsche_Absolvierende'] = df_filtered_12['Absolvierende_und_Abgehende_Anzahl'] - \
                                                   df_filtered_12[
                                                       'auslaendische_Absolvierende_und_Abgehende_Anzahl']

        grouped = df_filtered_12.groupby("Abschluss").agg({
            "Absolvierende_und_Abgehende_Anzahl": "sum",
            "auslaendische_Absolvierende_und_Abgehende_Anzahl": "sum"
        }).reset_index()

        sum_auslaender = grouped["auslaendische_Absolvierende_und_Abgehende_Anzahl"].sum()
        sum_deutsch = grouped["Absolvierende_und_Abgehende_Anzahl"].sum() - sum_auslaender

        grouped["auslaender_prozent_norm"] = grouped[
                                                 "auslaendische_Absolvierende_und_Abgehende_Anzahl"] / sum_auslaender * 100
        grouped["deutsch_anzahl"] = grouped["Absolvierende_und_Abgehende_Anzahl"] - grouped[
            "auslaendische_Absolvierende_und_Abgehende_Anzahl"]
        grouped["deutsch_prozent_norm"] = grouped["deutsch_anzahl"] / sum_deutsch * 100

        # *** Hier sortieren nach Ausländeranteil absteigend ***
        grouped = grouped.sort_values(by="auslaender_prozent_norm", ascending=False).reset_index(drop=True)

        #########################################################################################
        # Gruppiertes Balkendiagramm
        #########################################################################################

        labels = grouped["Abschluss"]
        x = np.arange(len(labels))  # Positionen auf der x-Achse für jeden Abschluss
        breite = 0.4  # Breite der Balken

        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        # Balken für Ausländer
        balken_auslaender = ax.bar(x - breite / 2, grouped["auslaender_prozent_norm"], breite,
                                   color='#fc8d62', label='Ausländisch')

        # Balken für Deutsche
        balken_deutsch = ax.bar(x + breite / 2, grouped["deutsch_prozent_norm"], breite,
                                color='#66c2a5', label='Deutsch')

        # Prozentwerte auf die Balken schreiben
        for i in range(len(labels)):
            # Ausländer-Wert
            ax.text(x=i - breite / 2, y=grouped["auslaender_prozent_norm"][i] + 1,
                    s=f"{grouped['auslaender_prozent_norm'][i]:.1f}%", ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color='black')
            # Deutsch-Wert
            ax.text(x=i + breite / 2, y=grouped["deutsch_prozent_norm"][i] + 1,
                    s=f"{grouped['deutsch_prozent_norm'][i]:.1f}%", ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color='black')


        # Achsenticks und -labels
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11, color='black')

        # Achsentitel entfernen

        ax.set_xlabel('')
        #ax.set_ylabel('')
        ax.set_ylabel('Anteil in Prozent (%)', fontsize=12)
        # y-Achse mit Prozent-Suffix
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y)}%'))

        # Legende rechts oben platzieren
        ax.legend(loc='upper right')


        # Entferne unnötige Rahmenlinien
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        st.pyplot(fig)


        ##################################################
        # Plot ohne Hauptschulabschluss deutsch/ ausländer
        import plotly.graph_objects as go

        # Filter: nur Abschluss2 mit "Förderschwerpunkt"
        df_foerderschwerpunkt = df_filtered_12[
            df_filtered_12['Abschluss2'].str.contains("Förderschwerpunkt", case=False, na=False)]

        if not df_foerderschwerpunkt.empty:
            # Deutsche berechnen
            df_foerderschwerpunkt['deutsch_anzahl'] = (
                    df_foerderschwerpunkt['Absolvierende_und_Abgehende_Anzahl'] -
                    df_foerderschwerpunkt['auslaendische_Absolvierende_und_Abgehende_Anzahl']
            )

            # Gruppieren
            grouped_f = df_foerderschwerpunkt.groupby('Abschluss2').agg({
                'Absolvierende_und_Abgehende_Anzahl': 'sum',
                'auslaendische_Absolvierende_und_Abgehende_Anzahl': 'sum',
                'deutsch_anzahl': 'sum'
            }).reset_index()

            # Summen berechnen für Prozentnormierung
            sum_ausl = grouped_f['auslaendische_Absolvierende_und_Abgehende_Anzahl'].sum()
            sum_deu = grouped_f['deutsch_anzahl'].sum()

            if sum_ausl > 0 and sum_deu > 0:
                grouped_f['auslaender_prozent'] = grouped_f[
                                                      'auslaendische_Absolvierende_und_Abgehende_Anzahl'] / sum_ausl * 100
                grouped_f['deutsch_prozent'] = grouped_f['deutsch_anzahl'] / sum_deu * 100

                # Plotly Balkendiagramm
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=grouped_f['Abschluss2'],
                    y=grouped_f['auslaender_prozent'],
                    name='Ausländisch',
                    marker_color='#fc8d62',
                    text=grouped_f['auslaender_prozent'].round(1).astype(str) + '%',
                    textposition='outside'
                ))

                fig.add_trace(go.Bar(
                    x=grouped_f['Abschluss2'],
                    y=grouped_f['deutsch_prozent'],
                    name='Deutsch',
                    marker_color='#66c2a5',
                    text=grouped_f['deutsch_prozent'].round(1).astype(str) + '%',
                    textposition='outside'
                ))

                fig.update_layout(
                    barmode='group',
                    title='Anteil bei Förderschwerpunkten (Ohne Hauptschulabschluss)',
                    xaxis_title='Abschluss2 (Förderschwerpunkt)',
                    yaxis_title='Anteil in Prozent (%)',
                    yaxis=dict(ticksuffix='%'),
                    legend=dict(x=0.85, y=1.0),
                    bargap=0.2,
                    plot_bgcolor='white',
                    height=600
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nicht genügend Daten für prozentuale Darstellung (nur Nullwerte).")
        else:
            st.info("Keine Daten mit 'Förderschwerpunkt' in Abschluss2 für das gewählte Jahr vorhanden.")










    with tab_abschluss:
        # Daten einlesen
        # CSS für vertikale Zentrierung der Legenden-Spalte
        st.markdown("""
            <style>
            div[data-testid="column"]:nth-child(2) {
                display: flex;
                align-items: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # Daten einlesen
        url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/Destatis_12211-0206_Bildungsabschluss_Mikrozensus_aufbereitet.csv"
        df = pd.read_csv(url, sep=";")

        df['Anzahl'] = pd.to_numeric(df['Anzahl'], errors='coerce')
        df = df.dropna(subset=['Anzahl'])
        df = df[df['Geschlecht'] != 'männlich']
        df = df[df['Geschlecht'] != 'weiblich']


        valid_entries = [
            "Lehre / Berufsausbildung",
            "Fachschulabschluss",
            "Bachelor",
            "Master",
            "Diplom",
            "Promotion",
            "In schulischer oder beruflicher Ausbildung",
            "Nicht in schulischer oder beruflicher Ausbildung"
        ]

        df = df[df["Beruflicher Bildungsabschluss"].isin(valid_entries)]
        df = df[df["Migrationsstatus"] != "Insgesamt"]
        with st.expander("DataFrame anzeigen"):
            st.dataframe(df)




        farben = px.colors.qualitative.Plotly
        farbe_map = {abschluss: farben[i % len(farben)] for i, abschluss in enumerate(valid_entries)}

        def create_plot_and_legend(status):
            df_filtered = df[
                (df["Migrationsstatus"] == status) &
                (df["Geschlecht"] == "Insgesamt")
                ].copy()

            df_grouped = (
                df_filtered
                .groupby(["Jahr", "Beruflicher Bildungsabschluss"])["Anzahl"]
                .sum()
                .reset_index()
            )

            df_grouped["Prozent"] = df_grouped.groupby("Jahr")["Anzahl"].transform(lambda x: 100 * x / x.sum())
            df_grouped["Prozent"] = df_grouped["Prozent"].round(1)

            fig = px.line(
                df_grouped,
                x="Jahr",
                y="Prozent",
                color="Beruflicher Bildungsabschluss",
                markers=True,
                title=status,
                labels={
                    "Prozent": "Prozent (%)",
                    "Jahr": "Jahr",
                    "Beruflicher Bildungsabschluss": "Bildungsabschluss"
                },
                color_discrete_map=farbe_map,
                category_orders={"Beruflicher Bildungsabschluss": valid_entries}
            )

            fig.update_traces(texttemplate='%{y}%', textposition='top center')
            fig.update_layout(
                hovermode="x unified",
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=40, r=40, t=60, b=40),
                yaxis=dict(range=[0, 55]),
                showlegend=False
            )

            fig_legend = go.Figure()
            for abschluss in valid_entries:
                fig_legend.add_trace(
                    go.Scatter(
                        x=[None],
                        y=[None],
                        mode='markers+lines',
                        name=abschluss,
                        marker=dict(color=farbe_map[abschluss]),
                        line=dict(color=farbe_map[abschluss])
                    )
                )

            fig_legend.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",  # Mittig
                    y=0.5,  # Mittig
                    xanchor="left",
                    x=0
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                height=300,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )

            return fig, fig_legend

        status_liste = ["Ohne Migrationshintergrund", "Mit Migrationshintergrund"]

        for status in status_liste:
            col1, col2 = st.columns([2, 1])
            plot, legend = create_plot_and_legend(status)
            col1.plotly_chart(plot, use_container_width=True, key=f"{status}_plot")
            col2.plotly_chart(legend, use_container_width=True, key=f"{status}_legend")

        ##########################################
        # Plot Anzahl der gewählten Bildungsabschlüsse nach Migrationsstatus
        df = df[df["Beruflicher Bildungsabschluss"].isin(valid_entries)]
        # Ausschluss bestimmter Migrationsstatus
        ausgeschlossene_status = ["Insgesamt", "Mit Migrationshintergrund", "Ohne Migrationshintergrund"]

        df = df[~df["Migrationsstatus"].isin(ausgeschlossene_status)]

        # "Insgesamt" bei Migrationsstatus rausfiltern
        df = df[df["Migrationsstatus"] != "Insgesamt"]

        # Bildungsabschluss Filter (Mehrfachauswahl)
        auswahl_abschluss = st.multiselect(
            "Bildungsabschluss auswählen:",
            options=sorted(df["Beruflicher Bildungsabschluss"].unique()),
            default=["Lehre / Berufsausbildung"],
            key="Tab_Abschluss"
        )

        if not auswahl_abschluss:
            st.warning("Bitte mindestens einen Bildungsabschluss auswählen.")
        else:
            # Daten filtern
            df_filtered = df[df["Beruflicher Bildungsabschluss"].isin(auswahl_abschluss)].copy()

            # Gruppieren nach Jahr, Migrationsstatus (summe Anzahl)
            df_grouped = df_filtered.groupby(['Jahr', 'Migrationsstatus'])['Anzahl'].sum().reset_index()

            # Plot erstellen
            # Bildungsabschlüsse als String, mit Kommas getrennt, ohne Hochzeichen
            abschluesse_str = ", ".join(auswahl_abschluss)

            fig = px.line(
                df_grouped,
                x='Jahr',
                y='Anzahl',
                color='Migrationsstatus',
                markers=True,
                title=f"Bildungsabschlüsse nach Migrationsstatus ({abschluesse_str})",
                labels={"Anzahl": "", "Jahr": "", "Migrationsstatus": "Migrationsstatus"}
            )

            # Hover-Template anpassen, um "k" hinter die Zahl zu setzen (im Tooltip)
            fig.update_traces(
                hovertemplate='%{y}k<br>%{x}<br>%{color}',
                texttemplate='%{y}k',
                textposition='top center'
            )

            fig.update_layout(
                hovermode='x unified',
                yaxis_title="Anzahl in 1000",
                xaxis_title=None
            )

            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show()