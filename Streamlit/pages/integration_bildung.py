import streamlit as st
from PIL import Image

def show():
    st.title("🎓 Integration: Bildung")
    st.markdown("""
    - Schulerfolg und Bildungsabschlüsse von Menschen mit Migrationshintergrund  
    - Unterschiede zwischen den Bundesländern  
    """)

    # Bild laden
    img = Image.open("C:/Users/alexa/Desktop/Antonija/DSI_Weiterbildung/Abschlussprojekt/Migration/01_Bildung/Allgemeinbildende Schulen/Tableau_Karte_Anteil_ausl_Schueler.png")
    
    # Bild anzeigen
    st.image(img, caption="Mein Bild", use_column_width=True)
