import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Titel
st.title("Übersicht Kreise")
st.header("Bevölkerungsdichte vs. Ausländeranteil")

# Fester Pfad zur CSV-Datei
csv_path = "data/migration/scatter_plot_anteil_dichte.csv"

# CSV einlesen

df = pd.read_csv(csv_path, sep=None, engine='python')

# Dropdown-Menü für Aufenthaltstitel
titel_options = ["insgesamt"] + sorted(df["Ausgewählte Aufenthaltstitel"].dropna().unique().tolist())
selected_titel = st.selectbox("Wähle einen Aufenthaltstitel", titel_options, index=0)

# Daten filtern oder aggregieren
if selected_titel == "insgesamt":
    df_filtered = (
        df.groupby("KREISE", as_index=False)
        .agg({
            "Dichte": "mean",
            "Anteil": "sum"
        })
    )
else:
    df_filtered = df[df["Ausgewählte Aufenthaltstitel"] == selected_titel]


fig, ax = plt.subplots()
sns.scatterplot(data=df_filtered, x="Dichte", y="Anteil", ax=ax)
ax.set_title(f"Ausländeranteil ({selected_titel})")
ax.set_xlabel("Bevölkerungsdichte (Einwohner pro km²)")
ax.set_ylabel("Ausländeranteil (%)")
st.pyplot(fig)
