import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def simple_timeline(file, group_col, default_groups=None):
    csv_path = f"data/migration/{file}"
    df = pd.read_csv(csv_path, sep=None, engine='python')
    if 'STAG' in df.columns:
        df["Jahr"] = pd.to_datetime(df["STAG"])
    df["Value_Mio"] = df["Value"] / 1_000_000

    fig = go.Figure()

    # Auswahl treffen
    all_groups = df[group_col].unique()
    sel_groups = st.multiselect(
        label=f"Wählen Sie {group_col} aus",
        options=all_groups,
        default=default_groups if default_groups else all_groups[:2],
        key=file
    )

    st.write(str(sel_groups))

    # Diagrame erstllen
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