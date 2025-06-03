import streamlit as st
from modules.plots import simple_timeline

def show():
    st.title("🛂 Integration: Einbürgerung")
    st.markdown("""
    - Entwicklung der Einbürgerungszahlen über die Jahre  
    - Herkunftsländer mit hoher Einbürgerungsrate  
    - Einflussfaktoren: Aufenthaltsdauer, Alter, Bildungsstand  
    - Regionale Unterschiede  
    - Korrelation mit anderen Integrationsindikatoren  
    """)
    st.header("Ländergruppierungen")
    default_groups = ["Afrika", "Asien", "Europa", "Amerika"]
    simple_timeline("einbürg_ländergruppen.csv", "Ländergruppierungen", default_groups)

    st.header("Staatsangehörigkeit")
    default_groups = ['Türkei', 'Italien', 'Ukraine', 'Syrien', 'Afghanistan']
    simple_timeline("einbürg_staaten.csv", "Staatsangehörigkeit", default_groups)

    st.header("Rechtsgrundlagen")
    default_groups = None
    simple_timeline("einbürg_recht.csv", "Rechtsgrundlagen", default_groups)

