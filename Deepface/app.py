import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Funkcija duomenų nuskaitymui
def load_data():
    conn = sqlite3.connect("emotion_log.db")
    query = "SELECT * FROM log"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['time'] = df['timestamp'].dt.time
    return df

st.set_page_config("Emocijų stebėsena", layout="wide")
st.title("🎭 Emocijų analizė ir stebėjimas iš SQLite")

# Duomenų įkėlimas
df = load_data()

# 🔴 LIVE STEBĖJIMAS
st.subheader("🔴 Live stebėjimas (naujausi įrašai)")
latest = df.sort_values("timestamp", ascending=False).head(5)
st.dataframe(latest, use_container_width=True)

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
    st.dataframe(df_laikas, use_container_width=True)

    # 🎨 Emocijų diagrama (stulpelinė)
    st.markdown("### Emocijų pasiskirstymas")
    emociju_sk = df_laikas["emotion"].value_counts()
    if not emociju_sk.empty:
        fig, ax = plt.subplots()
        emociju_sk.plot(kind="bar", ax=ax)
        ax.set_ylabel("Kiekis")
        ax.set_xlabel("Emocija")
        ax.set_title("Emocijų pasiskirstymas")
        st.pyplot(fig)

    # 🥧 Skritulinė diagrama su emocijų spalvomis ir procentais
    st.markdown("### Emocijų pasiskirstymas (skritulinė diagrama su procentais)")

    emociju_spalvos = {
        'angry': 'red', 'disgust': 'green', 'fear': 'purple',
        'happy': 'gold', 'sad': 'blue', 'surprise': 'orange', 'neutral': 'gray'
    }

    emociju_sk = df_laikas["emotion"].value_counts()

    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax_pie.pie(
        emociju_sk,
        colors=[emociju_spalvos.get(e, "lightgray") for e in emociju_sk.index],
        labels=None,  # išjungiame pavadinimus šalia sektorių
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=1.15,          # procentai išorėje
        labeldistance=1.25,        # brūkšnelio ilgis iki procento
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
