# api.py
from fastapi import FastAPI, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from predictor import calcular
from reporting import build_csv_content, build_report_payload

app = FastAPI(title="API Prediccion Energia FV")


class PredIn(BaseModel):
    irradiacion: float = Field(..., description="kWh/m2 (promedio mensual diario)")
    temperatura: float = Field(..., description="C (promedio mensual)")
    potencia_total_sf: float | None = Field(None, description="kWp (opcional)")


@app.post("/predict")
def predict(data: PredIn):
    return calcular(
        irradiacion=data.irradiacion,
        temperatura=data.temperatura,
        potencia_total_sf=data.potencia_total_sf,
    )


@app.get("/download/report.csv")
def download_report(
    irradiacion: float = Query(..., description="kWh/m2 (promedio mensual diario)"),
    temperatura: float = Query(..., description="C (promedio mensual)"),
    potencia_total_sf: float | None = Query(None, description="kWp opcional"),
    file_name: str | None = Query(None, description="Nombre sugerido del archivo CSV"),
):
    prediction = calcular(
        irradiacion=irradiacion,
        temperatura=temperatura,
        potencia_total_sf=potencia_total_sf,
    )
    report = build_report_payload(
        irradiacion=irradiacion,
        temperatura=temperatura,
        potencia_total_sf=potencia_total_sf,
        data=prediction,
        file_name=file_name,
    )
    csv_content = build_csv_content(report)
    return Response(
        content=csv_content.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{report["file_name"]}"',
            "Cache-Control": "no-store",
        },
    )


@app.get("/health")
def health():
    return {"ok": True}
