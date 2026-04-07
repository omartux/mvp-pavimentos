from fastapi import FastAPI
from database import SessionLocal, Calculo

app = FastAPI(title="MVP Pavimentos")

@app.get("/")
def home():
    return {"msg": "API Pavimentos funcionando 🚀"}

# 🔧 cálculo de espesor (mejorado)
def calcular_espesor(trafico: float, resistencia: float):
    if resistencia <= 0:
        return 0

    espesor = (trafico ** 0.3) / (resistencia ** 0.5) * 0.1

    # límites reales
    if espesor < 0.15:
        espesor = 0.15
    if espesor > 0.6:
        espesor = 0.6

    return round(espesor, 3)


# 🧱 cálculo por capas (AQUÍ VA tu función)
def calcular_capas(espesor_total):
    carpeta = 0.05
    base = espesor_total * 0.4
    subbase = espesor_total * 0.6 - carpeta

    return {
        "carpeta": round(carpeta, 3),
        "base": round(base, 3),
        "subbase": round(subbase, 3)
    }


# 🔥 endpoint principal (ahora devuelve TODO)
@app.get("/calculate")
def calculate(trafico: float, resistencia: float):
    espesor = calcular_espesor(trafico, resistencia)
    capas = calcular_capas(espesor)

    # guardar en BD
    db = SessionLocal()
    nuevo = Calculo(
        trafico=trafico,
        resistencia=resistencia,
        espesor=espesor
    )
    db.add(nuevo)
    db.commit()
    db.close()

    return {
        "espesor_total": espesor,
        "capas": capas
    }


# 📊 historial
@app.get("/history")
def history():
    db = SessionLocal()
    data = db.query(Calculo).all()
    db.close()

    return data
