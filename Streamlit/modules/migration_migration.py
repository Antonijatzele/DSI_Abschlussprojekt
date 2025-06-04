import streamlit as st
from modules.plots import simple_timeline

def show():
    st.title("🛂 Migrgation: Wanderungbewegungen")

    st.header("Migration ausländischer Staatbürger")
    default_groups = None
    simple_timeline("wander_gesamt.csv", "Art", default_groups)

    st.header("Wanderungsaldo nach Herkunftsländern")
    default_groups = ['Türkei', 'Italien', 'Ukraine', 'Syrien', 'Afghanistan']
    simple_timeline("wander_staaten.csv", "Herkunfts-/Zielländer", default_groups)

    st.header("Migration deutscher Staatbürger")
    default_groups = None
    simple_timeline("wander_gesamt_de.csv", "Art", default_groups)


