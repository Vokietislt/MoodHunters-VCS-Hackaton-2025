import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from dbfunctions import EmotionLogDB  # Adjust the import based on file name
import time
# Funkcija duomenų nuskaitymui
# Initialize DB handler
db = EmotionLogDB()

# Load data using class method


st.set_page_config("Emocijų stebėsena", layout="wide")
st.title("🎭 Emocijų analizė ir stebėjimas iš SQLite")

placeholder = st.empty()  # Reserve space for the table
df = db.load_data()




# 📊 Analizė pagal pasirinktą laikotarpį
st.subheader("📊 Analizė pagal pasirinktą laikotarpį")

pasirinkta_data = st.selectbox("Pasirinkite datą:", sorted(df["date"].unique()))
df_data = df[df["date"] == pasirinkta_data]

if not df_data.empty:
    visi_laikai = sorted(df_data["time"].unique())
    nuo_laikas = st.selectbox("Pasirinkite laiką nuo:", visi_laikai)
    iki_laikas = st.selectbox("Pasirinkite laiką iki:", visi_laikai, index=len(visi_laikai)-1)

    df_laikas = df_data[(df_data["time"] >= nuo_laikas) & (df_data["time"] <= iki_laikas)]

    st.markdown("### Atrinkti duomenys")
    st.dataframe(df_laikas.iloc[::-1], use_container_width=True)

    # 🎨 Emocijų stulpelinė diagrama
    st.markdown("### Emocijų pasiskirstymas")
    emociju_sk = df_laikas["emotion"].value_counts()
    if not emociju_sk.empty:
        fig, ax = plt.subplots()
        emociju_sk.plot(kind="bar", ax=ax)
        ax.set_ylabel("Kiekis")
        ax.set_xlabel("Emocija")
        ax.set_title("Emocijų pasiskirstymas")
        st.pyplot(fig)

    # 🎯 Taškinė diagrama: X – emocijos, Y – laikas
    st.markdown("### Emocijos per laiką (taškinė diagrama)")

    emociju_spalvos = {
        'angry': 'red', 'disgust': 'green', 'fear': 'purple',
        'happy': 'gold', 'sad': 'blue', 'surprise': 'orange', 'neutral': 'gray'
    }

    df_laikas_sorted = df_laikas.sort_values("timestamp")
    df_laikas_sorted["color"] = df_laikas_sorted["emotion"].map(emociju_spalvos)

    fig_dot, ax_dot = plt.subplots(figsize=(8, 6))
    for emocija in df_laikas_sorted["emotion"].unique():
        df_emocija = df_laikas_sorted[df_laikas_sorted["emotion"] == emocija]
        ax_dot.scatter(
            df_emocija["emotion"],
            df_emocija["timestamp"],
            color=emociju_spalvos.get(emocija, "gray"),
            label=emocija,
            s=100
        )

    ax_dot.set_xlabel("Emocija")
    ax_dot.set_ylabel("Laikas")
    ax_dot.set_title("Emocijos per laiką (taškinis grafikas)")
    ax_dot.legend(title="Emocija", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig_dot)

    # 🥧 Skritulinė diagrama su emocijų spalvomis ir procentais
    st.markdown("### Emocijų pasiskirstymas (skritulinė diagrama su procentais)")

    emociju_sk = df_laikas["emotion"].value_counts()
    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax_pie.pie(
        emociju_sk,
        colors=[emociju_spalvos.get(e, "lightgray") for e in emociju_sk.index],
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=1.15,
        labeldistance=1.25,
        textprops=dict(color="black", fontsize=10)
    )

    ax_pie.legend(
        wedges,
        labels=emociju_sk.index,
        title="Emocija",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )
    ax_pie.set_title("Emocijų dalys procentais")
    plt.subplots_adjust(top=0.80)
    st.pyplot(fig_pie)

    # 📈 Confidence vidurkis
    df_laikas["confidence"] = pd.to_numeric(df_laikas["confidence"], errors="coerce")
    avg_conf = df_laikas["confidence"].mean()
    st.metric("Vidutinis confidence", f"{avg_conf:.2f}")

    # 🖥️ Aktyvios programėlės
    st.markdown("### Aktyvios programėlės")
    st.dataframe(df_laikas["foreground_app"].value_counts().reset_index().rename(
        columns={'index': 'Programėlė', 'foreground_app': 'Kiekis'}), use_container_width=True)

else:
    st.warning("Pasirinktai datai nėra duomenų.")


while True:
    df = db.load_data()
    
    # Example modification: filter, sort, etc.
    latest = df.sort_values("timestamp", ascending=False).head(5)
    
    with placeholder.container():
        st.subheader("🔴 Live stebėjimas (naujausi įrašai)")
        st.dataframe(latest, use_container_width=True)
    
    time.sleep(1)