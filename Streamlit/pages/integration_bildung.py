import streamlit as st
from PIL import Image

def show():
    st.title("🎓 Integration: Bildung")
    st.markdown("""
    - Schulerfolg und Bildungsabschlüsse von Menschen mit Migrationshintergrund  
    - Unterschiede zwischen den Bundesländern  
    """)

    # Bild laden
    img = Image.open("images/Bildung_Tableau_Karte.png")
    
    # Bild anzeigen
    st.image(img, caption="Anteil ausländischer Schüler pro Bundesland", use_column_width=True)
