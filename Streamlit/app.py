import streamlit as st
from modules import (
    start,
    integration_arbeitsmarkt,
    integration_sprache,
    integration_bildung,
    migration,
    glossar,
)

# Seiten-Layout
st.set_page_config(page_title="Migration & Integration in Deutschland", layout="wide")

st.markdown("""
<style>

	.stTabs [data-baseweb="tab-list"] {
    }

	.stTabs [data-baseweb="tab"] p {
        font-size: 20pt;
        font-weight: bold;
    }

	.stTabs [aria-selected="true"] {
	}

</style>""", unsafe_allow_html=True)

# Hauptmenü-Struktur
hauptkategorien = {
    "Start": [],
    "Migration": [
        "Übersicht"
    ],
    "Integration": [
        "Arbeitsmarkt",
        "Sprache",
        "Bildung"
    ],
    "Glossar": [
        "Begriffe & Datenquellen"
    ]
}

# Sidebar: Hauptmenü-Dropdown
gewaehlte_kategorie = st.sidebar.selectbox("Themenbereich auswählen", list(hauptkategorien.keys()))

# Sidebar: Untermenü falls vorhanden
unterseiten = hauptkategorien[gewaehlte_kategorie]
if unterseiten:
    ausgewaehlte_seite = st.sidebar.radio("Unterseite wählen", unterseiten)
else:
    ausgewaehlte_seite = None

# Seiten-Dispatcher: Inhalte laden
if gewaehlte_kategorie == "Start" or not ausgewaehlte_seite:
    start.show()

# Migration
elif ausgewaehlte_seite == "Übersicht":
    migration.show()


# Integration
elif ausgewaehlte_seite == "Arbeitsmarkt":
    integration_arbeitsmarkt.show()

elif ausgewaehlte_seite == "Sprache":
    integration_sprache.show()

elif ausgewaehlte_seite == "Bildung":
    integration_bildung.show()

elif ausgewaehlte_seite == "Begriffe & Datenquellen":
    glossar.show()