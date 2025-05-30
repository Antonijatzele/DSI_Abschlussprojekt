import streamlit as st

def show():
    st.title("🎓 Integration: Bildung")
    st.markdown("""
    - Schulerfolg und Bildungsabschlüsse von Menschen mit Migrationshintergrund  
    - Unterschiede zwischen den Bundesländern  
    """)

    url = "https://public.tableau.com/static/images/Bi/Bildungsintegration/Blatt1/1.png"

    st.image(url, caption="Tableau Dashboard Vorschau", use_column_width=True)
