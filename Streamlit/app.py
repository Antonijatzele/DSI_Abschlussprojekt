import streamlit as st

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
    
    .stLogo {
        height: auto!important;
    }

</style>""", unsafe_allow_html=True)


# st.logo("Streamlit/images/logo.svg")


# Hauptmenü-Struktur
hauptkategorien = {
    "Migration": [
        st.Page("modules/migration_anteile.py", title="Anteile"),
        st.Page("modules/migration_migration.py", title="Migration"),
        st.Page("modules/migration_alter.py", title="Alterstruktur"),
        st.Page("modules/migration_kreise.py", title="Geographie"),
        st.Page("modules/migration_einbuergerung.py", title="Einbürgerung"),
    ],
    "Integration": [
        st.Page("modules/integration_arbeitsmarkt.py", title="Arbeitsmarkt"),
        st.Page("modules/integration_sprache.py", title="Sprache"),
        st.Page("modules/integration_bildung.py", title="Bildung"),

    ],
    "Glossar": [
        st.Page("modules/glossar.py", title="Begriffe & Datenquellen"),
    ]
}

pg = st.navigation(hauptkategorien)
pg.run()