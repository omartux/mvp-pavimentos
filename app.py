import streamlit as st
import pandas as pd
import os

st.title("Calculadora de Pavimentos")

# 📁 archivo CSV
CSV_FILE = "historial.csv"

# 🔧 lógica de ingeniería
def calcular_espesor(trafico, resistencia):
    if resistencia <= 0:
        return 0

    espesor = (trafico ** 0.3) / (resistencia ** 0.5) * 0.1

    if espesor < 0.15:
        espesor = 0.15
    if espesor > 0.6:
        espesor = 0.6

    return round(espesor, 3)


def calcular_capas(espesor):
    carpeta = 0.05
    base = espesor * 0.4
    subbase = espesor * 0.6 - carpeta

    return {
        "carpeta": round(carpeta, 3),
        "base": round(base, 3),
        "subbase": round(subbase, 3)
    }


# 📥 cargar historial si existe
def cargar_historial():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=[
            "trafico", "resistencia", "espesor",
            "carpeta", "base", "subbase"
        ])


# 💾 guardar historial
def guardar_historial(data):
    df = cargar_historial()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# inputs
trafico = st.number_input("Tráfico", value=1000.0)
resistencia = st.number_input("Resistencia", value=5.0)

# botón calcular
if st.button("Calcular"):

    espesor = calcular_espesor(trafico, resistencia)
    capas = calcular_capas(espesor)

    # resultado
    st.success(f"Espesor total: {espesor} m (≈ {espesor*100:.1f} cm)")

    st.subheader("Capas del pavimento")

    st.write(f"Carpeta asfáltica: {capas['carpeta']} m")
    st.write(f"Base: {capas['base']} m")
    st.write(f"Subbase: {capas['subbase']} m")

    # tabla capas
    df_capas = pd.DataFrame({
        "Capa": ["Carpeta", "Base", "Subbase"],
        "Espesor (m)": [
            capas["carpeta"],
            capas["base"],
            capas["subbase"]
        ]
    })

    st.dataframe(df_capas)
    st.bar_chart(df_capas.set_index("Capa"))

    # 💾 guardar resultado
    guardar_historial({
        "trafico": trafico,
        "resistencia": resistencia,
        "espesor": espesor,
        "carpeta": capas["carpeta"],
        "base": capas["base"],
        "subbase": capas["subbase"]
    })


# 📊 historial
st.subheader("Historial")

historial = cargar_historial()

if not historial.empty:
    st.dataframe(historial)
else:
    st.info("Aún no hay cálculos guardados")
