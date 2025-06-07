import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time

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

# Automatinis atnaujinimas (pvz. kas 10 s)
refresher = st.empty()
refresher.caption(f"Paskutinį kartą atnaujinta: {time.strftime('%H:%M:%S')}")
time.sleep(1)

df = load_data()

# 🔴 LIVE STEBĖJIMAS
st.subheader("🔴 Live stebėjimas (naujausi įrašai)")
latest = df.sort_values("timestamp", ascending=False).head(5)
st.dataframe(latest, use_container_width=True)

# 📆 Analizė pagal pasirinktą datą ir laiką
st.subheader("📊 Analizė pagal pasirinktą datą ir laiką")

# Dropdown filtrai
pasirinkta_data = st.selectbox("Pasirinkite datą:", sorted(df["date"].unique()))
df_data = df[df["date"] == pasirinkta_data]

if not df_data.empty:
    pasirinktas_laikas = st.selectbox("Pasirinkite laiką:", sorted(df_data["time"].unique()))
    df_laikas = df_data[df_data["time"] == pasirinktas_laikas]

    st.markdown("### Atrinkti duomenys")
    st.dataframe(df_laikas, use_container_width=True)

    # 🎨 Emocijų diagrama
    st.markdown("### Emocijų pasiskirstymas")
    emociju_sk = df_laikas["emotion"].value_counts()
    if not emociju_sk.empty:
        fig, ax = plt.subplots()
        emociju_sk.plot(kind="bar", ax=ax)
        ax.set_ylabel("Kiekis")
        ax.set_xlabel("Emocija")
        ax.set_title("Emocijų pasiskirstymas")
        st.pyplot(fig)

    # 📈 Confidence vidurkis
    avg_conf = df_laikas["confidence"].mean()
    st.metric("Vidutinis confidence", f"{avg_conf:.2f}")

    # 🖥️ Aktyvios programėlės
    st.markdown("### Aktyvios programėlės")
    st.dataframe(df_laikas["foreground_app"].value_counts().reset_index().rename(
        columns={'index': 'Programėlė', 'foreground_app': 'Kiekis'}), use_container_width=True)
else:
    st.warning("Pasirinktai datai nėra duomenų.")
