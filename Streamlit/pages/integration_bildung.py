import streamlit as st
from PIL import Image

def show():
    st.title("🎓 Integration: Bildung")
    st.image("https://raw.githubusercontent.com/Antonijatzele/DSI_Abschlussprojekt/main/images/Bildung_Tableau_Karte.png")


    # Tableau Dashboard URL
    tableau_url = "https://public.tableau.com/views/DeinDashboardName/DeinSheetName"
    
    # Iframe mit Streamlit anzeigen
    st.components.v1.html(
        f"""
        <iframe src="{tableau_url}" width="1000" height="800" frameborder="0"></iframe>
        """,
        height=800,
    )


# Funktion aufrufen
show()
