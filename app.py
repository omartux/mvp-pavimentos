import streamlit as st
import pandas as pd


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

import sqlite3

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trafico REAL,
        resistencia REAL,
        espesor REAL,
        carpeta REAL,
        base REAL,
        subbase REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

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
    
    contenido.append(Spacer(1, 20))
    contenido.append(Paragraph("Generado por Suite Básica de Cálculo Civil", styles["Italic"]))

    doc.build(contenido)

    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Suite Cálculo Civil", layout="centered")

st.title("🏗 Suite Básica de Cálculo Civil")

tab1, tab2, tab3 = st.tabs(["🛣 Pavimentos", "🧱 Concreto", "📐 Metrados"])

 

# ==============================
# 🔧 FUNCIONES
# ==============================

def calcular_espesor(trafico, resistencia):
    espesor = (trafico ** 0.3) / (resistencia ** 0.5) * 0.1

    espesor = max(0.15, min(espesor, 0.6))

    return round(espesor, 3)


def calcular_capas(espesor):
    carpeta = 0.05
    restante = max(0.0, espesor - carpeta)

    base = restante * 0.5
    subbase = restante * 0.5

    return {
        "carpeta": round(carpeta, 3),
        "base": round(base, 3),
        "subbase": round(subbase, 3)
    }

    

#

#
def dosificacion_concreto(fc):
    # Relación aproximada (tipo ACI simplificado)
    if fc <= 210:
        w_c = 0.60
    elif fc <= 280:
        w_c = 0.55
    else:
        w_c = 0.50

    # cemento (kg/m3)
    cemento = 350 + (fc - 210) * 0.8
    cemento = max(300, min(cemento, 450))

    agua = cemento * w_c

    # proporciones típicas
    arena = cemento * 2.2
    piedra = cemento * 3.0

    return {
        "cemento": round(cemento, 1),
        "agua": round(agua, 1),
        "arena": round(arena, 1),
        "piedra": round(piedra, 1)
    }
#
# ==============================
# 📊 HISTORIAL
# ==============================

def cargar_historial():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("SELECT * FROM calculos ORDER BY id DESC", conn)

    conn.close()
    return df



def guardar_historial(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO calculos (trafico, resistencia, espesor, carpeta, base, subbase)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["trafico"],
        data["resistencia"],
        data["espesor"],
        data["carpeta"],
        data["base"],
        data["subbase"]
    ))

    conn.commit()
    conn.close()

###
def borrar_historial():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calculos")
    conn.commit()
    conn.close()

# ==============================
# 🛣 TAB 1: PAVIMENTOS
# ==============================

with tab1:
    st.header("Diseño de Pavimentos")
    st.warning("⚠️ Diseño preliminar. No reemplaza método AASHTO ni MTC.")

    trafico = st.number_input("Tráfico (veh/dia)", value=1000.0, min_value=1.0, step=100.0, key="trafico")
    st.metric("Tráfico ingresado", f"{trafico:,.0f} veh/día")
    resistencia = st.number_input("Resistencia", value=5.0, min_value=0.1, key="resistencia")

    if st.button("Calcular Pavimento", key="btn_pavimento"):

        
        # 🔒 validación
        if trafico <= 0 or resistencia <= 0:
            st.error("Valores deben ser mayores a 0")
            st.stop()

          
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
      
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑 Limpiar historial", key="btn_delete"):
            borrar_historial()
            st.success("Historial borrado")
            st.rerun()  # 🔥 recarga la app
    
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

    fc = st.number_input("Resistencia f'c (kg/cm²)", value=210.0, min_value=1.0, step=10.0, key="fc")

    if st.button("Calcular Concreto", key="btn_concreto"):
 
        if fc <= 0:
            st.error("f'c debe ser mayor a 0")
            st.stop()        
        

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

    largo = st.number_input("Largo (m)", value=5.0, min_value=0.1)
    ancho = st.number_input("Ancho (m)", value=3.0, min_value=0.1)
    altura = st.number_input("Espesor / Altura (m)", value=0.2, min_value=0.01)
    
    fc = st.number_input("f'c para dosificación (kg/cm²)", value=210.0, min_value=1.0, key="fc_vol")

    if st.button("Calcular Volumen", key="btn_volumen"):

        if largo <= 0 or ancho <= 0 or altura <= 0:
            st.error("Dimensiones deben ser mayores a 0")
            st.stop()

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
        
        bolsas = cemento_total / 42.5
        st.write(f"🧱 Cemento: {cemento_total:.1f} kg ({bolsas:.1f} bolsas de 42.5 kg)")
        
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
