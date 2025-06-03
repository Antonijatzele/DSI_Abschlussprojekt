import streamlit as st
from modules import (
    start,
    integration_arbeitsmarkt,
    integration_sprache,
    integration_bildung,
    integration_einbuergerung,
    migration,
    migration_alter,
    migration_kreise,
    migration_kreise_scatter,
    glossar,
)

# Seiten-Layout
st.set_page_config(page_title="Migration & Integration in Deutschland", layout="wide")

# Hauptmenü-Struktur
hauptkategorien = {
    "Start": [],
    "Migration": [
        "Übersicht",
        "Alterstruktur",
        "Geographie1",
        "Geographie2",
    ],
    "Integration": [
        "Arbeitsmarkt",
        "Sprache",
        "Bildung",
        "Einbürgerung"
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

elif ausgewaehlte_seite == "Alterstruktur":
    migration_alter.show()

elif ausgewaehlte_seite == "Geographie1":
    migration_kreise.show()

elif ausgewaehlte_seite == "Geographie2":
    migration_kreise_scatter.show()


# Integration
elif ausgewaehlte_seite == "Arbeitsmarkt":
    integration_arbeitsmarkt.show()

elif ausgewaehlte_seite == "Sprache":
    integration_sprache.show()

elif ausgewaehlte_seite == "Bildung":
    integration_bildung.show()

elif ausgewaehlte_seite == "Einbürgerung":
    integration_einbuergerung.show()

elif ausgewaehlte_seite == "Begriffe & Datenquellen":
    glossar.show()
