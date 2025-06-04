import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.plots import simple_timeline, simple_piechart


def show():
    csv_path = "Streamlit/data/migration/historisch_gesamt.csv"
    df = pd.read_csv(csv_path, sep=None, engine='python')
    df["STAG"] = pd.to_datetime(df["STAG"])

    # Umformen zu Wide-Format
    pivot_df = df.pivot(index="STAG", columns="Nationalität", values="Value").reset_index()

    # Ausländeranteil berechnen
    pivot_df["Ausländeranteil (%)"] = (pivot_df["Ausländer"] / pivot_df["Insgesamt"]) * 100

    # Bevölkerung in Millionen
    pivot_df["Deutsche (Mio)"] = pivot_df["Deutsche"] / 1_000_000
    pivot_df["Ausländer (Mio)"] = pivot_df["Ausländer"] / 1_000_000
    pivot_df["Insgesamt (Mio)"] = pivot_df["Insgesamt"] / 1_000_000

    # Streamlit App
    st.title("Bevölkerung und Ausländeranteil in Deutschland")

    # Plotly-Figur mit zwei Y-Achsen
    fig = go.Figure()

    # Linke Y-Achse: Bevölkerung
    fig.add_trace(go.Scatter(x=pivot_df["STAG"], y=pivot_df["Deutsche (Mio)"],
                            name="Deutsche", mode="lines+markers", yaxis="y1"))
    fig.add_trace(go.Scatter(x=pivot_df["STAG"], y=pivot_df["Ausländer (Mio)"],
                            name="Ausländer", mode="lines+markers", yaxis="y1"))
    fig.add_trace(go.Scatter(x=pivot_df["STAG"], y=pivot_df["Insgesamt (Mio)"],
                            name="Insgesamt", mode="lines+markers", yaxis="y1"))

    # Rechte Y-Achse: Ausländeranteil
    fig.add_trace(go.Scatter(x=pivot_df["STAG"], y=pivot_df["Ausländeranteil (%)"],
                            name="Ausländeranteil (%)", mode="lines+markers",
                            yaxis="y2", line=dict(color="black", dash="dot")))

    # Skalen synchronisieren (optional Beispiel: 0-100 Mio ↔ 0–20 %)
    fig.update_layout(
        title="Bevölkerung (in Mio) & Ausländeranteil (%)",
        xaxis=dict(title="Jahr"),
        yaxis=dict(
            title="Bevölkerung (in Mio)",
            range=[0, 100],
            side="left",
            showgrid=True,
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0", "25", "50", "75", "100"]
        ),
        yaxis2=dict(
            title="Ausländeranteil (%)",
            overlaying="y",
            side="right",
            range=[0, 20], 
            tickvals=[0, 5, 10, 15, 20],
            ticktext=["0%", "5%", "10%", "15%", "20%"]
        ),
        legend=dict(x=0.01, y=0.99),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.header("Staatsangehörigkeit")
    simple_piechart("historisch_staaten.csv", "Staatsangehörigkeit")


    st.header("Ländergruppierungen")
    default_groups = ["Afrika", "Asien", "Europa", "Amerika"]
    simple_timeline("historisch_ländergruppen.csv", "Ländergruppierungen", default_groups)

    st.header("Staatsangehörigkeit")
    default_groups = ['Türkei', 'Italien', 'Ukraine', 'Syrien', 'Afghanistan']
    simple_timeline("historisch_staaten.csv", "Staatsangehörigkeit", default_groups)

    st.header("Aufenthaltstitel")
    default_groups = ['Befristete AE, besondere Gründe und nationale Visa', 'Befristete AE, völkerrechtl., human., pol. Gründe', 'Befristete Aufenthaltserlaubnis, Erwerbstätigkeit', 'Aufenthaltsrecht nach FreizügG/EU', 'Unbefristete Niederlassungserlaubnis']
    simple_timeline("historisch_titel.csv", "Ausgewählte Aufenthaltstitel")



