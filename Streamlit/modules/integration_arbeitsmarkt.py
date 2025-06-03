import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/refs/heads/main/Daten/Integration/Arbeitsmarktintegration/zusammengefuegt.csv",
        sep=";"
    )
    return df

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

def show():
    st.title("💼 Integration: Arbeitsmarkt")
    st.markdown("""
    - Beschäftigungsquote im Vergleich zur Gesamtbevölkerung  
    - Typische Berufsfelder und Branchen  
    - Einflussfaktoren: Herkunftsregion, Aufenthaltsdauer, Bildungsniveau  
    """)

    df = load_data()
    st.title("Arbeitsmarktintegration von Migranten — Deutsch vs. Ausländer (visualisiert)")

    cols = df.columns[1:]
    parsed_cols = [parse_column(c) for c in cols]
    parsed_cols = [p for p in parsed_cols if p is not None]

    indikator_options = sorted(set(p['indikator'] for p in parsed_cols))
    merkmal_options = sorted(set(p['merkmal'] for p in parsed_cols))

    indikator = st.selectbox("Indikator", indikator_options)
    merkmal = st.selectbox("Merkmal", merkmal_options)

    jahr_col = df.columns[0]
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
