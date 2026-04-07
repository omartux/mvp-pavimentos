import streamlit as st
import pandas as pd
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generar_pdf(espesor, capas):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    contenido = []

    contenido.append(Paragraph("INFORME DE DISEÑO PRELIMINAR DE PAVIMENTO", styles["Title"]))
    contenido.append(Spacer(1, 12))

    contenido.append(Paragraph(f"Espesor total: {espesor} m", styles["Normal"]))
    contenido.append(Spacer(1, 12))

    contenido.append(Paragraph("Capas:", styles["Heading2"]))

    contenido.append(Paragraph(f"Carpeta: {capas['carpeta']} m", styles["Normal"]))
    contenido.append(Paragraph(f"Base: {capas['base']} m", styles["Normal"]))
    contenido.append(Paragraph(f"Subbase: {capas['subbase']} m", styles["Normal"]))

    doc.build(contenido)

    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Suite Cálculo Civil", layout="centered")

st.title("🏗 Suite Básica de Cálculo Civil")

tab1, tab2, tab3 = st.tabs(["🛣 Pavimentos", "🧱 Concreto", "📐 Metrados"])

# 📁 archivo CSV
CSV_FILE = "historial.csv"

# ==============================
# 🔧 FUNCIONES
# ==============================

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


def dosificacion_concreto(fc):
    if fc <= 210:
        cemento = 300
    elif fc <= 280:
        cemento = 350
    else:
        cemento = 400

    agua = cemento * 0.5
    arena = 700
    piedra = 1100

    return {
        "cemento": cemento,
        "agua": round(agua, 1),
        "arena": arena,
        "piedra": piedra
    }


# ==============================
# 📊 HISTORIAL
# ==============================

def cargar_historial():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=[
            "trafico", "resistencia", "espesor",
            "carpeta", "base", "subbase"
        ])


def guardar_historial(data):
    df = cargar_historial()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# ==============================
# 🛣 TAB 1: PAVIMENTOS
# ==============================

with tab1:
    st.header("Diseño de Pavimentos")

    trafico = st.number_input("Tráfico", value=1000.0, key="trafico")
    resistencia = st.number_input("Resistencia", value=5.0, key="resistencia")

    if st.button("Calcular Pavimento"):

        espesor = calcular_espesor(trafico, resistencia)
        capas = calcular_capas(espesor)

        st.markdown(f"""
        ### 🧱 Resultado

        - **Espesor total:** {espesor} m (**{espesor*100:.1f} cm**)
        """)

        st.subheader("Capas del pavimento")

        df_capas = pd.DataFrame({
            "Capa": ["Carpeta", "Base", "Subbase"],
            "Espesor (m)": [
                capas["carpeta"],
                capas["base"],
                capas["subbase"]
            ]
        })

        st.dataframe(df_capas, use_container_width=True)
        st.bar_chart(df_capas.set_index("Capa"))

        # guardar historial
        guardar_historial({
            "trafico": trafico,
            "resistencia": resistencia,
            "espesor": espesor,
            "carpeta": capas["carpeta"],
            "base": capas["base"],
            "subbase": capas["subbase"]
        })
        
        pdf = generar_pdf(espesor, capas)

        st.download_button(
        label="📄 Descargar informe PDF",
        data=pdf,
        file_name="informe_pavimento.pdf",
        mime="application/pdf"
)

    # historial
    st.subheader("Historial")

    historial = cargar_historial()

    if not historial.empty:
        st.dataframe(historial, use_container_width=True)
    else:
        st.info("Aún no hay cálculos guardados")


# ==============================
# 🧱 TAB 2: CONCRETO
# ==============================

with tab2:
    st.header("Dosificación de Concreto")

    fc = st.number_input("Resistencia f'c (kg/cm²)", value=210, key="fc")

    if st.button("Calcular Concreto"):

        mix = dosificacion_concreto(fc)

        st.subheader("Dosificación por m³")

        df_mix = pd.DataFrame({
            "Material": ["Cemento (kg)", "Agua (L)", "Arena (kg)", "Piedra (kg)"],
            "Cantidad": [
                mix["cemento"],
                mix["agua"],
                mix["arena"],
                mix["piedra"]
            ]
        })

        st.dataframe(df_mix, use_container_width=True)


with tab3:
    st.header("Cálculo de Volumen de Concreto")

    largo = st.number_input("Largo (m)", value=5.0)
    ancho = st.number_input("Ancho (m)", value=3.0)
    altura = st.number_input("Espesor / Altura (m)", value=0.2)

    fc = st.number_input("f'c para dosificación (kg/cm²)", value=210, key="fc_vol")

    if st.button("Calcular Volumen"):

        volumen = largo * ancho * altura

        st.markdown(f"""
        ### 📦 Resultado

        - **Volumen:** {volumen:.2f} m³
        """)

        # usar tu función existente
        mix = dosificacion_concreto(fc)

        st.subheader("Materiales totales")

        cemento_total = mix["cemento"] * volumen
        agua_total = mix["agua"] * volumen
        arena_total = mix["arena"] * volumen
        piedra_total = mix["piedra"] * volumen

        df_materiales = pd.DataFrame({
            "Material": ["Cemento (kg)", "Agua (L)", "Arena (kg)", "Piedra (kg)"],
            "Total": [
                round(cemento_total, 2),
                round(agua_total, 2),
                round(arena_total, 2),
                round(piedra_total, 2)
            ]
        })

        st.dataframe(df_materiales, use_container_width=True)
