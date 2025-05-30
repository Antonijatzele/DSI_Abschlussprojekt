import streamlit as st


def show():
    st.title("🎓 Integration: Bildung")
    st.markdown("""
    - Schulerfolg und Bildungsabschlüsse von Menschen mit Migrationshintergrund  
    - Unterschiede zwischen den Bundesländern  
    """)

    # URL deines Tableau-Dashboards (öffentliche Ansicht)
    tableau_url = "https://public.tableau.com/views/Bildungsintegration/Blatt1"
    
    # Einbetten via iframe
    iframe_code = f'''
    <iframe src="{tableau_url}" width="900" height="700" frameborder="0"></iframe>
    '''
    
    st.markdown(iframe_code, unsafe_allow_html=True)
