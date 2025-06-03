import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def show():
    altersreihenfolge = list(range(85))

    def load_and_prepare_data(file_path, filter):
        df = pd.read_csv(file_path)

        if filter:
            gruppen = df["Ländergruppierungen"].unique()
            selected_group = st.selectbox(f"Wähle eine Ländergruppierung (Ausländer)", sorted(gruppen, key= lambda x: "$" if x=="Insgesamt" else x))
            df = df[df["Ländergruppierungen"] == selected_group]
        else:
            selected_group = "Deutsche"
            df = df
        
        # Alter nur bis 84 anzeigen
        df = df[df["ALT"].isin(altersreihenfolge)]

        #Männer und Frauen trennen
        df_men = df[df["GES"] == "GESM"].set_index("ALT")["Value"].reindex(altersreihenfolge).fillna(0)
        df_women = df[df["GES"] == "GESW"].set_index("ALT")["Value"].reindex(altersreihenfolge).fillna(0)

        return df_men, df_women, selected_group

    # Titel
    st.title("Alterverteilung im Vergleich")


    # Ausländer
    file_path_ausl = os.path.join("data", "migration", "alterspyramide.csv")
    df_men_ausl, df_women_ausl, selected_group_ausl = load_and_prepare_data(file_path_ausl, True )

    # Deutsche
    file_path_de = os.path.join("data", "migration", "alterspyramide_de.csv")
    df_men_de, df_women_de, selected_group_de = load_and_prepare_data(file_path_de, False)


    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.05,
        subplot_titles=(f"Ausländer ({selected_group_ausl})", "Deutsche")
    )

    # Ausländer
    fig.add_trace(go.Bar(
        y=altersreihenfolge,
        x=-df_men_ausl.values,
        name='Männer',
        orientation='h',
        marker=dict(color='steelblue'),
        showlegend=False
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=altersreihenfolge,
        x=df_women_ausl.values,
        name='Frauen',
        orientation='h',
        marker=dict(color='lightcoral'),
        showlegend=False
    ), row=1, col=1)

    # Deutsche
    fig.add_trace(go.Bar(
        y=altersreihenfolge,
        x=-df_men_de.values,
        name='Männer',
        orientation='h',
        marker=dict(color='steelblue'),
        showlegend=False
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        y=altersreihenfolge,
        x=df_women_de.values,
        name='Frauen',
        orientation='h',
        marker=dict(color='lightcoral'),
        showlegend=False
    ), row=1, col=2)

    # Layout
    fig.update_layout(
        height=800,
        barmode='overlay',
        bargap=0.1,
        xaxis=dict(
            title='',
            tickvals=[],
            ticktext=[]
        ),
        xaxis2=dict(
            title='',
            tickvals=[],
            ticktext=[]
        ),
        yaxis=dict(title='Alter'),
        title="Alterspyramiden: Ausländer vs. Deutsche"
    )

    st.plotly_chart(fig, use_container_width=True)
