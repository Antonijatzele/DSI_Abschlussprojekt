import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def simple_timeline(file, group_col, default_groups=None, running_sum=False):
    df = _read_csv(file)

    fig = go.Figure()

    # Auswahl treffen
    all_groups = df[group_col].unique()
    if default_groups:
        sel_groups = st.multiselect(
            label=f"{group_col} auswählen",
            options=all_groups,
            default=default_groups if default_groups else all_groups,
            key=f"timeline_{file}_{group_col}"
        )
    else:
        df = _shorten_df(df, group_col)
        sel_groups = df[group_col].unique()

    # Laufende Summe
    if running_sum:
        if st.checkbox('Laufende Summe', key=f"cb_rs_timeline_{file}_{group_col}"):
            df['Value'] = df.groupby(group_col)['Value'].cumsum()

    # Einheit
    df_filtered = df[df[group_col].isin(sel_groups)]
    max_value = df_filtered["Value"].max()
    einheit = ""
    if max_value > 1_000_000:
        df["Value"] = df["Value"] / 1_000_000
        einheit = "Mio"
    elif max_value > 1_000:
        df["Value"] = df["Value"] / 1_000
        einheit = "Tsd."
    
    # Y-Achse
    yaxis_title="Bevölkerung"
    if einheit:
        yaxis_title += f" (in {einheit})"

    # Diagrame ersetllen
    for group in sel_groups:
        subset = df[df[group_col] == group]
        fig.add_trace(go.Scatter(
            x=subset["Jahr"],
            y=subset["Value"],
            mode="lines+markers",
            name=group,
            hovertemplate=f"<b>{group}</b><br>Bevölkerung: %{{y:.2f}} {einheit}<extra></extra>"
        ))

    fig.update_layout(
        title="",
        xaxis_title="Jahr",
        yaxis_title=yaxis_title,
        hovermode="x unified",
        legend_title=group_col,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def simple_piechart(file, col, sum=False):
    df = _read_csv(file)


    # Jahr filtern bzw. Summe bilden
    selected_year = st.slider(
        'Jahr auswählen', 
        min_value=df['Jahr'].min(), 
        max_value=df['Jahr'].max(), 
        value=df['Jahr'].max(),
        key=f"piechart_{file}_{col}"
    )

    if sum:
        filtered_df = df[df['Jahr'] <= selected_year]
        filtered_df = filtered_df.groupby(col)["Value"].sum().reset_index()
        filtered_df["Jahr"] =  selected_year
    else:
        filtered_df = df[df['Jahr'] == selected_year]

    final_df = _shorten_df(filtered_df, col)

    # Prozent berechnen
    total_value = final_df['Value'].sum()
    final_df['Prozent'] = (final_df['Value'] / total_value) * 100

    # Titel anpassen
    if sum:
        title = f"Summe Jahr {df['Jahr'].min()} bis {selected_year}"
    else:
        title = f"Jahr {selected_year}"

    # Diagram erstellen und anzeigen
    fig = px.pie(
        final_df, 
        names=col, 
        values='Prozent', 
        title=title,
    )
    fig.update_layout(
        legend_title_text=col,
    ) 
    st.plotly_chart(fig)


def _read_csv(file):
    csv_path = f"Streamlit/data/migration/{file}"
    df = pd.read_csv(csv_path, sep=None, engine='python')
    if 'STAG' in df.columns:
        df["Jahr"] = pd.to_datetime(df["STAG"]).dt.year
    return df

def _shorten_df(df, col):
    df_sum = df.groupby(col)["Value"].sum().reset_index()
    # Wenn es mehr als 10 Einträge gibt -> zusammenfassen
    if len(df_sum) > 10:
        # Sortiere nach Value, und wähle die Top 10
        df_sorted = df_sum.sort_values(by='Value', ascending=False)
        top10 = df_sorted.head(10)[col]

        # Filter die Top10
        df_top10 = df[df[col].isin(top10)]

        # Nicht top10 -> Andere
        df_not_top10 = df[~df[col].isin(top10)].groupby(["Jahr"])["Value"].sum().reset_index()
        df_not_top10[col] = "Andere"
 
        return pd.concat([df_top10, df_not_top10])
    else:
        return df

    