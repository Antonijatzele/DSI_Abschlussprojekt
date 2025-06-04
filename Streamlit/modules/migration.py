import streamlit as st
from modules import (
    migration_anteile,
    migration_einbuergerung,
    migration_migration,
    migration_alter,
    migration_kreise,
)

def show():
    st.title("📈 Migration: Demografische & Geografische Analyse")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Anteile",
        "Migration",
        "Alterstruktur",
        "Geographie",
        "Einbürgerung"
    ])


    #"Migration":
    with tab1:
        migration_anteile.show()

    #"Migration":
    with tab2:
        migration_migration.show()

    # "Alterstruktur"
    with tab3:
        migration_alter.show()

    # "Geographie1"
    with tab4:
        migration_kreise.show()

    # "Einbürgerung"
    with tab5:
        migration_einbuergerung.show()