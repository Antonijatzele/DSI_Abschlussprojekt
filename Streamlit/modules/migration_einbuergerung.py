import streamlit as st
from modules.plots import simple_timeline, simple_piechart

def show():
    tab1, tab2, tab3, tab4 = st.tabs([
        "Gesamt",
        "Ländergruppierungen",
        "Staatsangehörigkeit",
        "Rechtsgrundlagen",
    ])
    with tab1:
        pass
    
    with tab2:
        st.subheader("Ländergruppierungen")
        default_groups = ["Afrika", "Asien", "Europa", "Amerika"]
        simple_timeline("einbürg_ländergruppen.csv", "Ländergruppierungen", default_groups)

    with tab3:
        st.subheader("Staatsangehörigkeit")
        default_groups = ['Türkei', 'Italien', 'Ukraine', 'Syrien', 'Afghanistan']
        simple_timeline("einbürg_staaten.csv", "Staatsangehörigkeit", default_groups)
        simple_piechart("einbürg_staaten.csv", "Staatsangehörigkeit", True)

    with tab4:
        st.subheader("Rechtsgrundlagen")
        default_groups = None
        simple_timeline("einbürg_recht.csv", "Rechtsgrundlagen", default_groups)

