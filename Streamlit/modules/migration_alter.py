import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def _stats(df):
    # Kumulierte Anzahl an Personen
    df_median = df.groupby("ALT")["Value"].sum().reset_index()
    df_median['Kumulierte_Anzahl'] = df_median['Value'].cumsum()

    # Gesamte Anzahl an Personen
    total_people = df_median['Value'].sum()

    # Medianalter = Punkt wo kumulierte Anzahl > Gesamte Anzahl / 2
    median_age_row = df_median[df_median['Kumulierte_Anzahl'] >= total_people / 2].iloc[0]
    median_age = median_age_row['ALT']

    #Verhältnis der Geschlechter
    men = df[df["GES"] == "GESM"]["Value"].sum()
    women = df[df["GES"] == "GESW"]["Value"].sum()

    if men > women:
        sex_ratio = f"{men/women:.2f} zu 1"
    else:
        sex_ratio = f"1 zu {women/men:.2f}"

    return median_age, sex_ratio




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

        return df_men, df_women, selected_group, df

    # Titel
    st.header("Alterverteilung im Vergleich")


    # Ausländer
    file_path_ausl = "Streamlit/data/migration/alterspyramide.csv"
    df_men_ausl, df_women_ausl, selected_group_ausl, df_ausl = load_and_prepare_data(file_path_ausl, True )

    # Deutsche
    file_path_de = "Streamlit/data/migration/alterspyramide_de.csv"
    df_men_de, df_women_de, selected_group_de, df_de = load_and_prepare_data(file_path_de, False)


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

    #Stats
    median_ausl, sex_ratio_ausl = _stats(df_ausl)
    median_de, sex_ratio_de = _stats(df_de)

    # Layout
    fig.update_layout(
        height=800,
        barmode='overlay',
        bargap=0.1,
        xaxis=dict(
            title=f'Medianalter: {median_ausl}, Verhältnis (M/W): {sex_ratio_ausl}',
            tickvals=[],
            ticktext=[]
        ),
        xaxis2=dict(
            title=f'Medianalter: {median_de}, Verhältnis (M/W): {sex_ratio_de}',
            tickvals=[],
            ticktext=[]
        ),
        yaxis=dict(title='Alter'),
        title="Alterspyramiden: Ausländer vs. Deutsche"
    )

    st.plotly_chart(fig, use_container_width=True)


    st.markdown("Quelle: [Destatis - Ausländerstatistik](https://www-genesis.destatis.de/datenbank/online/statistic/12521/details)")

if __name__ == "__main__":
    show()
