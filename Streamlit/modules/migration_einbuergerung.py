import streamlit as st
from modules.plots import simple_timeline, simple_piechart

def show():
    st.header("Einbürgerungen")

    tab1, tab2, tab3 = st.tabs([
        "Ländergruppierungen",
        "Staatsangehörigkeit",
        "Rechtsgrundlagen",
    ])
    with tab1:
        default_groups = ["Insgesamt", "Afrika", "Asien", "Europa", "Amerika"]
        simple_timeline("einbürg_ländergruppen.csv", "Ländergruppierungen", default_groups, running_sum=True)

    with tab2:
        default_groups = ['Türkei', 'Italien', 'Ukraine', 'Syrien', 'Afghanistan']
        simple_timeline("einbürg_staaten.csv", "Staatsangehörigkeit", default_groups, running_sum=True)
        simple_piechart("einbürg_staaten.csv", "Staatsangehörigkeit", True)

    with tab3:
        default_groups = None
        simple_timeline("einbürg_recht.csv", "Rechtsgrundlagen", default_groups, running_sum=True)
        simple_piechart("einbürg_recht.csv", "Rechtsgrundlagen", True)

    st.markdown("Quelle: [Destatis - Einbürgerungsstatistik](https://www-genesis.destatis.de/datenbank/online/statistic/12511/details)")

if __name__ == "__main__":
    show()