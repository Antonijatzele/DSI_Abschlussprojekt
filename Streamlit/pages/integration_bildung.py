import streamlit as st
import streamlit.components.v1 as components

def show():
    st.title("🎓 Integration: Bildung")
    st.markdown("""
    - Schulerfolg und Bildungsabschlüsse von Menschen mit Migrationshintergrund  
    - Unterschiede zwischen den Bundesländern  
    """)

    # Tableau Public Dashboard anzeigen
    tableau_html = """
    <iframe src="https://public.tableau.com/views/Bildungsintegration/Blatt1?:embed=y&:showVizHome=no"
    width="1000" height="800" frameborder="0"></iframe>
    """
    
    components.html(tableau_html, height=800)
