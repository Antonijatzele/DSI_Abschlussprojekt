import streamlit as st
from modules.plots import simple_timeline

def show():
    st.header("Migration - Wanderungsbewegungen")

    tab1, tab2, tab3 = st.tabs(["Übersicht", "Herkunftsländer", "Vergleich Deutsche"])

    with tab1:
        st.subheader("Migration ausländischer Staatbürger")
        default_groups = None
        simple_timeline("wander_gesamt.csv", "Art", default_groups, running_sum=True)

    with tab2:
        st.subheader("Wanderungsaldo nach Herkunftsländern")
        default_groups = ['Türkei', 'Italien', 'Ukraine', 'Syrien', 'Afghanistan']
        simple_timeline("wander_staaten.csv", "Herkunfts-/Zielländer", default_groups, running_sum=True)

    with tab3:
        st.subheader("Migration deutscher Staatbürger")
        default_groups = None
        simple_timeline("wander_gesamt_de.csv", "Art", default_groups, running_sum=True)

    st.markdown("Quelle: [Destatis - Wanderungsstatistik](https://www-genesis.destatis.de/datenbank/online/statistic/12711/details)")


if __name__ == "__main__":
    show()
