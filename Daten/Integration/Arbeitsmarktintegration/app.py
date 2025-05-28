import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Titel
st.title("Arbeitslose unter 25 Jahren – Zeitverlauf")

# Daten laden (ggf. sep=';' anpassen)
df = pd.read_csv('zusammengefuegt.csv', sep=";")

# Leere Zellen ersetzen (optional)
df = df.replace(r'^\s*$', pd.NA, regex=True)

# Spaltenname vereinfachen für Lesbarkeit (optional)
spalte = "insgesamt_arbeitslose_nachaltersgruppe_unter 25 Jahre"

# Filter für Jahre (sofern vorhanden)
if 'Jahr' in df.columns:
    jahre = sorted(df['Jahr'].dropna().unique())
    jahr_auswahl = st.multiselect("Jahre auswählen:", jahre, default=jahre)

    # Nach Auswahl filtern
    df = df[df['Jahr'].isin(jahr_auswahl)]

# Plot erstellen
fig, ax = plt.subplots()
ax.plot(df['Jahr'], df[spalte], marker='o', color='royalblue')
ax.set_title('Arbeitslose unter 25 Jahren über die Jahre')
ax.set_xlabel('Jahr')
ax.set_ylabel('Anzahl Arbeitslose')
ax.grid(True)

# Plot anzeigen
st.pyplot(fig)


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Titel
st.title("Arbeitslose unter 25 Jahren – Vergleich nach Berufsabschluss")

# CSV laden
df = pd.read_csv('zusammengefuegt.csv', sep=";")

# Leere Zellen ersetzen
df = df.replace(r'^\s*$', pd.NA, regex=True)

# Spalte
