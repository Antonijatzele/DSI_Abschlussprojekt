import streamlit as st

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