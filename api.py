# api.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from predictor import calcular

app = FastAPI(title="API Predicción Energía FV")

class PredIn(BaseModel):
    irradiacion: float = Field(..., description="kWh/m² (promedio mensual diario)")
    temperatura: float = Field(..., description="°C (promedio mensual)")
    potencia_total_sf: float | None = Field(None, description="kWp (opcional)")

@app.post("/predict")
def predict(data: PredIn):
    return calcular(
        irradiacion=data.irradiacion,
        temperatura=data.temperatura,
        potencia_total_sf=data.potencia_total_sf
    )

@app.get("/health")
def health():
    return {"ok": True}