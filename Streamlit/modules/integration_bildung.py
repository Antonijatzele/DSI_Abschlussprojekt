
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


def show():
    st.title("🎓 Bildungs-Integration")

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

    tab1, tab2 = st.tabs(["Schulen", "Beruflicher Bildungsabschluss"])
    with tab1:

        tab3, tab4, tab5 = st.tabs(["Übersicht", "Herkunft", "Abschluss"])
        with tab3:


            # Daten einlesen: Destatis 21111-03
            # Schüler/-innen (Deutsche, Ausländer/-innen) nach Bildungsbereichen, rechtlichem Status der Schule, Schularten und Geschlecht
            url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/Daten/Integration/Bildungsintegration/Destatis_21111-03_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
            df = pd.read_csv(url, sep=',')

            # Vorverarbeitung
            df = df.drop(columns=['Staatsangehoerigkeit'])
            df = df.rename(columns={'Staatsangehoerigkeit_clean': 'Staatsangehoerigkeit'})
            df = df[df['Bildungsbereich'] != 'Bereich unbekannt']

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
                jahr = st.selectbox("📅 Schuljahr", schuljahre, index=default_index)

            with col2:
                # Nur relevante Daten
                df_filter_basis = df[
                    (df['Geschlecht'].isin(['männlich', 'weiblich'])) &
                    (df['Bundesland'] != 'Deutschland') &
                    (df['Schuljahr'] == jahr) &
                    (df['Staatsangehoerigkeit'].isin(['deutsche Schüler/innen', 'ausländische Schüler/innen']))
                    ]

                alle_bildungsbereiche = sorted(df_filter_basis["Bildungsbereich"].dropna().unique().tolist())
                ausgewaehlter_bildungsbereich = st.selectbox("🎓 Bildungsbereich", alle_bildungsbereiche)



            with col3:
                bundesland_options = df['Bundesland'].unique()
                selected_bundesland = st.selectbox(
                    "🗺️ Bundesland",
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
            m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles='CartoDB positron')

            def style_function(feature):
                anteil = feature['properties']['Anteil (%)']
                return {
                    'fillOpacity': 0.8,
                    'weight': 1,
                    'color': 'black',
                    'fillColor': colormap(anteil) if anteil is not None else 'lightgrey'
                }

            tooltip = folium.GeoJsonTooltip(
                fields=['name'],
                aliases=[''],
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

            # Prozentwerte als Text auf der Karte anzeigen
            for _, row in bundeslaender.iterrows():
                if pd.notna(row['Anteil (%)']):
                    folium.map.Marker(
                        [row['geometry'].centroid.y, row['geometry'].centroid.x],
                        icon=folium.DivIcon(
                            html=f"""
                            <div style="
                                font-size: 12px; 
                                color: white; 
                                font-weight: bold;
                                text-align: center;
                                background-color: rgba(0,0,0,0.5);
                                padding: 2px 4px;
                                border-radius: 4px;">
                                {row['Anteil (%)']}%
                            </div>
                            """
                        )
                    ).add_to(m)

            colormap.add_to(m)

            # In Streamlit anzeigen
            #st.subheader(f"Anteil ausländischer Schüler/innen nach Bundesland ({jahr})")
            #fig1 = st_folium(m, width=1000, height=700)

            #########################################################
            # Diagramm 2: Anteil ausländischer Schüler pro Schulart #
            #########################################################

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
            fig2.patch.set_facecolor('white')  # Figure-Hintergrund weiß
            fig2.patch.set_linewidth(0)
            ax.set_facecolor('white')  # Plot-Hintergrund weiß

            y = range(len(df_auslaendisch))
            werte = df_auslaendisch['Anteil'].values
            schularten = df_auslaendisch['Schulart'].values

            bars = ax.barh(y, werte, height=0.8, color=orange, label='ausländische Schüler/innen')

            # Prozentwerte rechts neben den Balken anzeigen
            for bar, wert in zip(bars, werte):
                ax.text(
                    bar.get_width() + 1,
                    bar.get_y() + bar.get_height() / 2,
                    f"{wert:.1f}%",
                    va='center',
                    ha='left',
                    color='black',  # Text schwarz
                    fontsize=10,
                    fontweight='bold'
                )

            # Achsen und Beschriftungen
            ax.set_yticks(y)
            ax.set_xticks([])
            ax.set_yticklabels(schularten, color='black', fontsize=10)
            ax.set_ylabel('')
            ax.set_xlabel('')
            # ax.set_title("Anteil ausländischer Schüler/innen pro Schulart", color='black')

            # Rahmen entfernen
            for spine in ax.spines.values():
                spine.set_visible(False)

            # Gitterlinien auf der x-Achse (optional)
            ax.grid(axis='x', linestyle='--', alpha=0.3, color='gray')  # hellgraue Gitterlinien

            # plt.tight_layout()
            #st.pyplot(fig2)

            # die Diagramme in 2x2 Columns anzeigen
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Anteil ausländischer Schüler nach Bundesland")
                fig1 = st_folium(m, width=500, height=600)

            with col2:
                st.subheader("Anteil ausländischer Schüler nach Schulart")
                # Diagramm 2 anzeigen
                st.pyplot(fig2)


        with tab4:
            ###############################################################################
            # Daten einlesen: Destatis 21111-08
            # Ausländische Schüler/-innen nach Schularten, Staatsangehörigkeit und Geschlecht
            url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/Destatis_21111-08_allgemeinbildende_schulen_2021_2024_zusammengefuegt.csv"
            df = pd.read_csv(url, sep=',')

            # Die ersten zwei Spalten löschen
            df = df.drop(df.columns[:2], axis=1)

            # 'Syrien, Arabische Republik' in 'Syrien' umbenennen
            df['Staatsangehoerigkeit'] = df['Staatsangehoerigkeit'].replace('Syrien, Arabische Republik', 'Syrien')

            with st.expander("DataFrame anzeigen"):
                st.dataframe(df)

            # Filter als Dropdowns (selectbox)

            col1, col2, col3 = st.columns(3)

            with col1:
                schuljahre = sorted(df["Schuljahr"].unique())
                default_index = schuljahre.index("2023/24") if "2023/24" in schuljahre else 0
                jahr = st.selectbox("Schuljahr", schuljahre, index=default_index)


            with col2:
                schulart_options_2 = df['Schulart'].unique()
                selected_schulart_2 = st.selectbox("Schulart",
                                                   ['Alle'] + list(schulart_options_2), index=0)


            with col3:
                bundesland_options_2 = df['Bundesland'].unique()
                selected_bundesland_2 = st.selectbox(
                    "Bundesland",
                    bundesland_options_2,
                    index=list(bundesland_options_2).index('Deutschland') if 'Deutschland' in bundesland_options_2 else 0
                )




            # Filter anwenden
            df_filtered = df[df['Bundesland'] == selected_bundesland_2]
            df_filtered = df[df['Schuljahr'] == jahr]

            if selected_schulart_2 != 'Alle':
                df_filtered = df_filtered[df_filtered['Schulart'] == selected_schulart_2]

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

            ########################################################
            # Diagramm 3: Kreisdiagramm Top 10 Staatsangehörigkeit #
            ########################################################

            # Basisfarbe
            base_color = mcolors.to_rgb('#fc8d62')

            # Normalisieren der Prozentwerte (0 bis 1)
            percent_values = df_top10['Prozent'].values
            norm = (percent_values - percent_values.min()) / (percent_values.max() - percent_values.min())
            inverted_norm = 1 - norm

            # Funktion zum Abdunkeln der Farbe
            def darken_color(color, factor):
                return tuple(np.clip(np.array(color) * factor, 0, 1))

            # Abgestufte Farben erzeugen
            colors = [darken_color(base_color, 0.5 + 0.5 * f) for f in inverted_norm]

            # Zeichne das Kreisdiagramm
            fig3, ax = plt.subplots(figsize=(8, 8))
            fig3.patch.set_facecolor('white')  # Figure-Hintergrund weiß
            ax.set_facecolor('white')  # Axes-Hintergrund weiß

            plt.pie(
                df_top10['Prozent'],
                labels=df_top10['Staatsangehoerigkeit'],
                autopct='%1.1f%%',
                startangle=140,
                colors=colors,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2},  # optional: weißer Rand
                textprops={'color': "black", 'fontsize': 12}  # schwarze Schrift
            )

            fig3.tight_layout()
            st.pyplot(fig3)

            ##########################################
            # Datensatz laden: Schüler, Staatsangehörigkeiten, Bundesländer, Jahre 1992-2000

            url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/auslaendische_Schueler_Staatsangehoerigkeit_1992_2020_aufbereitet.csv"
            df = pd.read_csv(url, sep=";")
            # Mapping anwenden
            df["Geschlecht"] = df["Geschlecht"].map({
                "z": "insgesamt",
                "m": "männlich",
                "w": "weiblich"
            })

            df = df[df['Geschlecht'] != 'insgesamt']
            df = df[df['Anzahl'] != 0]

            df = df[df["Kontinent"] != "Alle"]
            df = df[df["Kontinent"] != "Keine Angabe und ungeklärt"]

            # 🧾 Bundesland-Filter (Multiselect)
            bundeslaender = df["Bundesland"].unique().tolist()
            # 'Deutschland' als Default setzen, falls vorhanden
            default_value = ["Deutschland"] if "Deutschland" in bundeslaender else []
            selected_bundeslaender = st.multiselect("Bundesland auswählen", bundeslaender, default=default_value)

            # 🔍 Daten filtern
            filtered_df = df[df["Bundesland"].isin(selected_bundeslaender)]

            with st.expander("DataFrame anzeigen"):
                st.dataframe(df)

            # Gruppierung nach Jahr und Kontinent (du kannst hier auch nach Geschlecht oder Land filtern)
            grouped = filtered_df.groupby(["Jahr", "Kontinent"], as_index=False)["Anzahl"].sum()

            # Plot erstellen mit Plotly
            fig = px.line(
                grouped,
                x="Jahr",
                y="Anzahl",
                color="Kontinent",
                title="Anzahl ausländischer Schüler nach Kontinent",
            )

            # Weißer Hintergrund, schwarze Schrift
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(color="black"),
                xaxis=dict(title="Jahr", color="black"),
                yaxis=dict(title="Anzahl", color="black"),
            )

            # Streamlit Ausgabe
            # st.title("Anzahl ausländischer Schüler nach Kontinent")
            st.plotly_chart(fig)





        with tab5:
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
            df = df[df['Abschluss'] != 'ohne Hauptschulabschluss']
            df['Abschluss'] = df['Abschluss'].replace('mittlerer Abschluss', 'Mittlerer Abschluss')

            Abgangsjahr = df['Abgangsjahr'].unique()
            selected_Abgangsjahr = st.selectbox("Abgangsjahr", Abgangsjahr)
            df_filtered_12 = df[df['Abgangsjahr'] == selected_Abgangsjahr]

            # Deutsche Absolventen berechnen
            df_filtered_12['deutsche_Absolvierende'] = df_filtered_12['Absolvierende_und_Abgehende_Anzahl'] - df_filtered_12[
                'auslaendische_Absolvierende_und_Abgehende_Anzahl']

            # Gruppierung nach Abschluss
            df_grouped = df_filtered_12.groupby('Abschluss').agg({
                'deutsche_Absolvierende': 'sum',
                'auslaendische_Absolvierende_und_Abgehende_Anzahl': 'sum'
            }).reset_index()

            # Gesamtsummen für Prozentberechnung
            gesamt_auslaender = df_grouped['auslaendische_Absolvierende_und_Abgehende_Anzahl'].sum()
            gesamt_deutsche = df_grouped['deutsche_Absolvierende'].sum()

            # Prozentwerte berechnen
            df_grouped['Prozent_auslaender'] = (df_grouped[
                                                    'auslaendische_Absolvierende_und_Abgehende_Anzahl'] / gesamt_auslaender) * 100
            df_grouped['Prozent_deutsche'] = (df_grouped['deutsche_Absolvierende'] / gesamt_deutsche) * 100

            # Sortieren nach Anteil Ausländer absteigend
            grouped_sorted = df_grouped.sort_values(by='Prozent_auslaender', ascending=False).reset_index(drop=True)

            # Transponiertes (horizontal) Balkendiagramm mit Matplotlib
            fig4, ax = plt.subplots(figsize=(10, 8))

            # Weißer Hintergrund
            fig4.patch.set_facecolor('white')
            ax.set_facecolor('white')

            # Balken zeichnen
            bars_auslaender = ax.barh(
                grouped_sorted['Abschluss'],
                grouped_sorted['Prozent_auslaender'],
                label='Ausländisch',
                color='#fc8d62'
            )

            bars_deutsche = ax.barh(
                grouped_sorted['Abschluss'],
                grouped_sorted['Prozent_deutsche'],
                left=grouped_sorted['Prozent_auslaender'],
                label='Deutsch',
                color='#66c2a5'
            )

            # Prozentwerte in die Balken schreiben, nur wenn größer 5%
            for bar, wert in zip(bars_auslaender, grouped_sorted['Prozent_auslaender']):
                if wert > 5:
                    ax.text(
                        bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f'{wert:.1f}%',
                        va='center',
                        ha='center',
                        color='black',  # Schwarze Schrift
                        fontsize=13
                    )

            for bar, wert, left in zip(bars_deutsche, grouped_sorted['Prozent_deutsche'],
                                       grouped_sorted['Prozent_auslaender']):
                if wert > 5:
                    ax.text(
                        left + bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f'{wert:.1f}%',
                        va='center',
                        ha='center',
                        color='black',  # Schwarze Schrift
                        fontsize=13
                    )

            # Achsen und Stil anpassen
            ax.xaxis.set_visible(False)
            ax.set_yticklabels(grouped_sorted['Abschluss'], fontsize=15, color='black')  # Schwarze Y-Achsenbeschriftung
            ax.set_title('', color='black')
            ax.invert_yaxis()

            # Rahmen entfernen
            for spine in ax.spines.values():
                spine.set_visible(False)

            # Legende mit schwarzem Text
            ax.legend(facecolor='white', edgecolor='white', labelcolor='black')

            plt.tight_layout()
            #st.pyplot(fig4)

            # Diagramme in 2 Spalten
            col5, col6 = st.columns(2)

            with col5:
                st.subheader("Anteil Absolventen")
                st.pyplot(fig4)

            with col6:
                st.subheader("...")
                # st.pyplot(fig4)



            ###############################################################




    with tab2:
        # Daten einlesen aus Github
        # Destatis_Einbürgerungsstatistik_12511-0001

        url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Bildungsintegration/Destatis_12211-0206_Bildungsabschluss_Mikrozensus_aufbereitet.csv"
        df = pd.read_csv(url, sep=";")

        df['Anzahl'] = pd.to_numeric(df['Anzahl'], errors='coerce')
        print(df['Anzahl'].isna().sum())
        df = df.dropna(subset=['Anzahl'])

        with st.expander("DataFrame anzeigen"):
            st.dataframe(df)

        # Streamlit Filter
        jahre = df['Jahr'].unique()
        selected_jahr = st.selectbox("Wähle das Jahr", sorted(jahre))

        migrations_status = ['Mit Migrationshintergrund', 'Ohne Migrationshintergrund']
        selected_status = st.multiselect("Migrationsstatus", migrations_status, default=migrations_status)

        # Daten filtern
        df_filtered = df[(df['Jahr'] == selected_jahr) & (df['Migrationsstatus'].isin(selected_status))]

        # 'Insgesamt' aus 'Beruflicher Bildungsabschluss' entfernen
        df_filtered = df_filtered[df_filtered['Beruflicher Bildungsabschluss'] != 'Insgesamt']

        # Nur spezifische Abschlüsse (keine Oberkategorien)
        df_filtered = df_filtered[df_filtered['Beruflicher Bildungsabschluss'].isin([
            'Bachelor', 'Diplom', 'Master'
        ])]

        # Gesamtzahl aller Personen für das ausgewählte Jahr und beide Migrationsstatus
        gesamt = df_filtered['Anzahl'].sum()

        # Prozentwerte berechnen - Anteil jeder Gruppe (Bildungsabschluss + Migrationsstatus) am Gesamtwert
        grouped = df_filtered.groupby(['Beruflicher Bildungsabschluss', 'Migrationsstatus'])[
            'Anzahl'].sum().reset_index()
        grouped['Prozent'] = 100 * grouped['Anzahl'] / gesamt

        # Pivot für gestapeltes Balkendiagramm
        df_pivot = grouped.pivot(index='Beruflicher Bildungsabschluss', columns='Migrationsstatus',
                                 values='Prozent').fillna(0)

        # Plot horizontal
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
        ax.set_facecolor('white')

        left = pd.Series([0] * len(df_pivot), index=df_pivot.index)
        colors = ['#fc8d62', '#66c2a5']

        for i, status in enumerate(df_pivot.columns):
            bars = ax.barh(df_pivot.index, df_pivot[status], left=left, label=status, color=colors[i])
            # Prozentwerte auf die Balken schreiben – jetzt schwarz
            for bar, wert in zip(bars, df_pivot[status]):
                if wert > 3:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f'{wert:.1f}%',
                        ha='center',
                        va='center',
                        color='black',  # Schwarz statt weiß
                        fontsize=12
                    )
            left += df_pivot[status]

        # Achsenticks schwarz machen
        ax.tick_params(axis='y', colors='black', labelsize=12)

        # Achsentitel entfernen (oder falls vorhanden, schwarz setzen)
        ax.set_xlabel('')
        ax.set_ylabel('')

        # X-Achse ausblenden
        ax.xaxis.set_visible(False)

        # Titel schwarz
        # ax.set_title(f'Prozentuale Anteile nach Bildungsabschluss im Jahr {selected_jahr}', color='black')

        # Legende schwarz (Text & Titel)
        leg = ax.legend([])
        plt.setp(leg.get_texts(), color='black')
        leg.get_title().set_color('black')

        plt.tight_layout()
        st.pyplot(fig)