import streamlit as st

def show():
    st.title("📚 Glossar: Begriffe & Datenquellen")

    st.subheader("🔑 Wichtige Begriffe")
    st.markdown("""
    - **Migrant:in**: Person mit ausländischer Staatsangehörigkeit oder Migrationshintergrund  
    - **Einbürgerung**: Der formale Erwerb der deutschen Staatsangehörigkeit  
    - **Integration**: Teilhabe am gesellschaftlichen, wirtschaftlichen und politischen Leben  
    """)

    st.subheader("📊 Wichtige Datenquellen")
    st.markdown("""
    - Statistisches Bundesamt (Destatis)  
    - Bundesamt für Migration und Flüchtlinge (BAMF)  
    - Mikrozensus  
    """)