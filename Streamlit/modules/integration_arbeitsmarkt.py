from io import StringIO
import folium
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

# Original-Datensatz laden
@st.cache_data
def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Arbeitsmarktintegration/zusammengefuegt.csv",
        sep=";",
        decimal=",",
        encoding="utf-8"
    )
    return df

@st.cache_data
def get_country_files():
    api_url = "https://api.github.com/repos/Antonijatzele/DSI_Abschlussprojekt/contents/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoten"
    res = requests.get(api_url)
    if res.status_code != 200:
        st.error("Konnte die Dateiliste nicht laden.")
        return []
    files = res.json()
    return [f["name"].replace(".csv", "") for f in files if f["name"].endswith(".csv")]

# Neuer Datensatz: nach Geschlecht
@st.cache_data
def load_data_geschlecht(): 
       # Liste der Ländernamen, die in den Dateinamen verwendet werden
    laender = get_country_files()
    

    dfs = []  # Liste zum Sammeln der DataFrames

    for land in laender:
        url = f"https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Arbeitsmarktintegration/beschaeftigungsquoten/{land}.csv"
        
        # CSV-Datei als Text laden
        csv_data = requests.get(url).text
        
        # CSV einlesen mit Behandlung von Dezimalen, Quotes, und "x" als NaN
        df = pd.read_csv(
            StringIO(csv_data),
            sep=";",
            decimal=",",
            quotechar='"',
            na_values=["x"],
            skipinitialspace=True,
            encoding="utf-8"
        )
        
        # Spaltennamen säubern (Anführungszeichen und Leerzeichen entfernen)
        df.columns = df.columns.str.strip().str.replace('"', '')
        
        # Leere "Jahr"-Zeilen entfernen
        df = df.dropna(subset=["Jahr"])
        
        # "Jahr" als Integer
        df["Jahr"] = df["Jahr"].astype(int)
        
        # Herkunftsspalte
        df["Land"] = land
        # Koordinaten ergänzen


        
        dfs.append(df)

    # Alle DataFrames zusammenfügen
    gesamt_df = pd.concat(dfs, ignore_index=True)


    return gesamt_df


# Spaltennamen zerlegen
def parse_column(col):
    parts = col.split("_")
    if len(parts) == 4:
        return {
            "staat": parts[0],
            "indikator": parts[1],
            "merkmal": parts[2],
            "auspraegung": parts[3],
            "full": col
        }
    else:
        return None

# Hauptfunktion
def show():
    st.title("💼 Integration: Arbeitsmarkt")

    df = load_data()
    jahr_col = df.columns[0]

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Übersicht", "Nach Herkunftsland", "Beschreibung"])

    # Beschreibung (Tab 3)
    with tab3:
        st.markdown("""
        - **Beschäftigungsquote** im Vergleich zur Gesamtbevölkerung  
        - **Typische Berufsfelder** und Branchen  
        - **Einflussfaktoren**: Herkunftsregion, Aufenthaltsdauer, Bildungsniveau  
        """)

    # Neuer Tab: nach Geschlecht (nicht Staatsangehörigkeit!)
    with tab2:
        st.subheader("Beschäftigungsquote nach Herkunftsland")

        df_geschlecht = load_data_geschlecht()
        st.dataframe(df_geschlecht)

        indikator_options = []
        selected = st.multiselect("Indikatoren wählen", indikator_options, default=indikator_options)

        fig, ax = plt.subplots(figsize=(12, 6))
        for indikator in selected:
            ax.plot(df_geschlecht["Jahr"], df_geschlecht[indikator], label=indikator, marker='o')

        ax.set_title("Beschäftigungsquoten nach Geschlecht")
        ax.set_xlabel("Jahr")
        ax.set_ylabel("Quote (%)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        ##############################################################
        #
        # Weltkarte
        # Karte erstellen, zentriert irgendwo
        # Filtere nach Jahr
        jahr = st.selectbox("Wähle ein Jahr", sorted(df_geschlecht["Jahr"].unique()))
        df_filtered = df_geschlecht[df_geschlecht["Jahr"] == jahr]


        wert_spalte = "Beschäftigungsquote"

        st.write(f"**Färbung basiert auf der Spalte:** {wert_spalte}")

        # Top 3 Länder nach Wert bestimmen
        top3 = df_filtered.nlargest(3, wert_spalte)

        # Farben für Top 3 (Gold, Silber, Bronze)
        farben = ["#FFD700", "#C0C0C0", "#CD7F32"]

        col1, col2 = st.columns([2, 1])

        geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
        geojson_data = requests.get(geojson_url).json()
    
        with col1:
            m = folium.Map(zoom_start=5)
            
            st.dataframe(df_filtered)

            # Länder einfärben
            folium.Choropleth(
                geo_data=geojson_data,
                data=df_filtered,
                columns=["Land", "Beschäftigungsquote"],
                key_on="feature.properties.name",
                fill_color="YlOrRd",
                fill_opacity=0.8,
                line_opacity=0.3,
                legend_name="Beschäftigungsquote (%)",
                nan_fill_color="lightgray"
            ).add_to(m)

            for _, row in df_filtered.iterrows():
                popup_text = f"""
                <b>Land:</b> {row['Land']}<br>
                <b>Jahr:</b> {row['Jahr']}<br>
                <b>Beschäftigungsquote:</b> {row['Beschäftigungsquote']}%
                """
                folium.GeoJsonPopup(
                    fields=[],
                    labels=False,
                    html=popup_text
                )



            st_folium(m, width=768, height=1024)

        with col2:
            st.markdown("### 📋 Länder nach Beschäftigungsquote")
            df_sorted = df_filtered[["Land", wert_spalte]].sort_values(by=wert_spalte, ascending=False)
            st.dataframe(df_sorted.set_index("Land"), use_container_width=True)

    # Übersicht (Tab 1)
    with tab1:
        st.subheader("📊 Arbeitsmarktintegration — Deutsch vs. Ausländer")

        cols = df.columns[1:]
        parsed_cols = [parse_column(c) for c in cols]
        parsed_cols = [p for p in parsed_cols if p is not None]

        indikator_options = sorted(set(p['indikator'] for p in parsed_cols))
        merkmal_options = sorted(set(p['merkmal'] for p in parsed_cols))

        indikator = st.selectbox("Indikator", indikator_options)
        merkmal = st.selectbox("Merkmal", merkmal_options)

        relevante_spalten = [p for p in parsed_cols if p['indikator'] == indikator and p['merkmal'] == merkmal]

        if not relevante_spalten:
            st.warning("Keine Daten für diese Kombination gefunden.")
            return

        auspraegungen = sorted(set(p['auspraegung'] for p in relevante_spalten))
        data_plot = pd.DataFrame()
        data_plot[jahr_col] = df[jahr_col]

        for auspraegung in auspraegungen:
            sp_insgesamt = None
            sp_auslaender = None

            for p in relevante_spalten:
                if p['auspraegung'] == auspraegung:
                    if p['staat'].lower() == 'insgesamt':
                        sp_insgesamt = p['full']
                    elif p['staat'].lower() in ['ausländer', 'auslaender']:
                        sp_auslaender = p['full']

            if sp_insgesamt and sp_auslaender:
                data_plot[f"Ausländer_{auspraegung}"] = df[sp_auslaender]
                data_plot[f"Deutsch_{auspraegung}"] = df[sp_insgesamt] - df[sp_auslaender]
            elif sp_auslaender:
                data_plot[f"Ausländer_{auspraegung}"] = df[sp_auslaender]
            elif sp_insgesamt:
                data_plot[f"Deutsch_{auspraegung}"] = df[sp_insgesamt]

        fig, ax = plt.subplots(figsize=(12, 7))
        colors = plt.cm.get_cmap('tab10', len(auspraegungen))
        linestyles = {'Ausländer': '-', 'Deutsch': '--'}

        for i, auspraegung in enumerate(auspraegungen):
            for gruppe in ['Ausländer', 'Deutsch']:
                col_name = f"{gruppe}_{auspraegung}"
                if col_name in data_plot.columns:
                    ax.plot(
                        data_plot[jahr_col], data_plot[col_name],
                        linestyle=linestyles[gruppe],
                        color=colors(i),
                        marker='o',
                        label=f"{gruppe} - {auspraegung}"
                    )

        ax.set_title(f"Vergleich Deutsch vs. Ausländer für {indikator} - {merkmal}")
        ax.set_xlabel("Jahr")
        ax.set_ylabel("Anzahl")
        ax.legend(title="Gruppe - Ausprägung", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True)
        st.pyplot(fig)

# Starten
if __name__ == "__main__":
    show()
