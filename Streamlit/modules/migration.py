import streamlit as st
from modules import (
    migration_anteile,
    migration_einbuergerung,
    migration_migration,
    migration_alter,
    migration_kreise,
    migration_kreise_scatter,
)

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Anteile",
        "Migration",
        "Alterstruktur",
        "Geographie1",
        "Geographie2",
        "Einbürgerung"
    ])


    #"Migration":
    with tab1:
        migration_anteile.show()

    #"Migration":
    with tab2:
        migration_migration.show()

    # "Alterstruktur"
    with tab3:
        migration_alter.show()

    # "Geographie1"
    with tab4:
        migration_kreise.show()

    # "Geographie2"
    with tab5:
        migration_kreise_scatter.show()

    # "Einbürgerung"
    with tab6:
        migration_einbuergerung.show()