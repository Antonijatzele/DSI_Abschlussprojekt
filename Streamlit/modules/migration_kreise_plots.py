import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px




def show():
    st.header("Geographische Verteilung")

    tab1, tab2 = st.tabs(["Scatterplot", "Korrelationkoeffizient"])

    with tab1:
        # Titel
        st.subheader("Bevölkerungsdichte vs. Ausländeranteil")

        csv_path = "Streamlit/data/migration/scatter_plot_anteil_dichte.csv"
        df = pd.read_csv(csv_path)

        # Dropdown-Menü für Aufenthaltstitel
        titel_options = ["insgesamt"] + sorted(df["Staatsangehörigkeit"].dropna().unique().tolist())
        selected_titel = st.selectbox("Staatsangehörigkeit", titel_options, index=0)

        # Daten filtern oder aggregieren
        if selected_titel == "insgesamt":
            df_filtered = (
                df.groupby("KREISE", as_index=False)
                .agg({
                    "Dichte": "mean",  # Durchschnitt der Dichte
                    "Anteil": "sum"    # Summe des Anteils
                })
            )
        else:
            df_filtered = df[df["Staatsangehörigkeit"] == selected_titel]

        # Erstellen des Plotly Scatterplots
        fig = px.scatter(
            df_filtered,
            x="Dichte",
            y="Anteil",
            title=f"Ausländeranteil ({selected_titel})",
            labels={
                "Dichte": "Bevölkerungsdichte (Einwohner pro km²)",
                "Anteil": "Ausländeranteil (%)"
            },
        )

        fig.update_layout(
            width=700,
            height=700,
        )

        st.plotly_chart(fig, use_container_width=False)

    with tab2:
        # Korrealtionsdisgram
        df_corr = pd.read_csv("Streamlit/data/migration/scatter_plot_anteil_dichte_corr.csv")
        
        fig = px.bar(
            df_corr.sort_values(by='Correlation'), 
            x='Correlation', 
            y='Staatsangehörigkeit', 
            title='Korrelationen zwischen Bevölkerungsdichte und -anteil nach Ländern',
            orientation='h'
            )
        fig.update_layout(
            height=1200
        )
        st.plotly_chart(fig)



    st.markdown("Quelle: [Destatis - Ausländerstatistik](https://www-genesis.destatis.de/datenbank/online/statistic/12521/details)")

if __name__ == "__main__":
    show()
