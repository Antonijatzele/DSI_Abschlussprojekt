import streamlit as st
import streamlit.components.v1 as components

def show():
    st.title("🎓 Integration: Bildung")

    st.markdown("Test")
    st.markdown("Test 3")



    # Beispiel-URL einer öffentlichen Tableau-Viz
    tableau_url = "https://public.tableau.com/app/profile/antonija.tzelepidis/viz/Bildungsintegration/Blatt1"
    
    # Iframe-Einbettung
    components.html(f"""
        <iframe src="{tableau_url}" width="1000" height="800" frameborder="0" allowfullscreen></iframe>
    """, height=800)
    
    

