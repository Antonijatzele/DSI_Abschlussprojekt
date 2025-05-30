import streamlit as st
from PIL import Image

def show():
    st.title("🎓 Integration: Bildung")
    st.markdown("""
    - Schulerfolg und Bildungsabschlüsse von Menschen mit Migrationshintergrund  
    - Unterschiede zwischen den Bundesländern  
    """)

     # Bild über direkte URL laden
    image_url = "https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/images/Bildung_Tableau_Karte.png"
    st.image(image_url, caption="Anteil ausländischer Schüler:innen", use_column_width=True)

    if st.button("📊 Zum Tableau Dashboard"):
    st.markdown("[Hier klicken, um das Dashboard zu öffnen](https://public.tableau.com/views/Bildungsintegration/Blatt1)", unsafe_allow_html=True)
