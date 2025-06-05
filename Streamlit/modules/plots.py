import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def simple_timeline(file, group_col, default_groups=None):
    df = _read_csv(file)
    df["Value_Mio"] = df["Value"] / 1_000_000

    fig = go.Figure()

    # Auswahl treffen
    all_groups = df[group_col].unique()
    if default_groups:
        sel_groups = st.multiselect(
            label=f"{group_col} auswählen",
            options=all_groups,
            default=default_groups if default_groups else all_groups,
            key=file
        )
    else:
        sel_groups = all_groups

    #st.write(str(sel_groups))

    # Diagrame ersetllen
    for group in sel_groups:
        subset = df[df[group_col] == group]
        fig.add_trace(go.Scatter(
            x=subset["Jahr"],
            y=subset["Value_Mio"],
            mode="lines+markers",
            name=group,
            hovertemplate=f"<b>{group}</b><br>Bevölkerung: %{{y:.2f}} Mio<extra></extra>"
        ))

    fig.update_layout(
        title="",
        xaxis_title="Jahr",
        yaxis_title="Bevölkerung (in Mio)",
        hovermode="x unified",
        legend_title=group_col,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def simple_piechart(file, col, sum=False):
    df = _read_csv(file)


    # Jahr filtern bzw. Summe bilden
    selected_year = st.slider('Jahr auswählen', min_value=df['Jahr'].min(), max_value=df['Jahr'].max(), value=df['Jahr'].max())
    if sum:
        filtered_df = df[df['Jahr'] <= selected_year]
        filtered_df = filtered_df.groupby(col)["Value"].sum().reset_index()
    else:
        filtered_df = df[df['Jahr'] == selected_year]

    # Wenn es mehr als 10 Einträge gibt -> zusammenfassen
    if len(filtered_df) > 10:
        # Sortiere nach Value, und wähle die Top 10
        filtered_df_sorted = filtered_df.sort_values(by='Value', ascending=False)
        top_10_df = filtered_df_sorted.head(10)

        # Berechne den Rest (Andere)
        rest_value = filtered_df_sorted.iloc[10:]['Value'].sum()

        # Füge "Andere" hinzu
        other_df = pd.DataFrame({
            'Staatsangehörigkeit': ['Andere'],
            'Value': [rest_value],
            'Jahr': [selected_year]
        })
        final_df = pd.concat([top_10_df, other_df])
    else:
        final_df = filtered_df

    # Prozent berechnen
    total_value = final_df['Value'].sum()
    final_df['Prozent'] = (final_df['Value'] / total_value) * 100

    # Titel anpassen
    if sum:
        title = f"Summe von Jahr {df['Jahr'].min()} bis {selected_year}"
    else:
        title = f"Jahr {selected_year}"

    # Diagram erstellen und anzeigen
    fig = px.pie(
        final_df, 
        names=col, 
        values='Prozent', 
        title=title
    )
    st.plotly_chart(fig)


def _read_csv(file):
    csv_path = f"Streamlit/data/migration/{file}"
    df = pd.read_csv(csv_path, sep=None, engine='python')
    if 'STAG' in df.columns:
        df["Jahr"] = pd.to_datetime(df["STAG"]).dt.year
    return df
