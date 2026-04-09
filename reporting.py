from __future__ import annotations

import csv
import re
from datetime import datetime
from io import StringIO


PERIOD_LABELS = (
    ("diaria", "Predicción diaria"),
    ("mensual", "Predicción mensual"),
    ("anual", "Predicción anual"),
)

MODEL_LABELS = (
    ("regresion", "Regresión"),
    ("bosque", "Bosque"),
    ("gbr", "Gradient Boosting"),
    ("promedio", "Promedio ponderado"),
)


def make_report_filename(generated_at: datetime | None = None) -> str:
    stamp = generated_at or datetime.now()
    return f"reporte_fv_{stamp:%Y%m%d_%H%M%S}.csv"


def normalize_report_filename(file_name: str | None, generated_at: datetime | None = None) -> str:
    candidate = (file_name or "").strip()
    if not candidate:
        return make_report_filename(generated_at)

    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", candidate).strip("._")
    if not safe_name:
        safe_name = make_report_filename(generated_at)
    if not safe_name.lower().endswith(".csv"):
        safe_name = f"{safe_name}.csv"
    return safe_name


def build_report_payload(
    irradiacion: float,
    temperatura: float,
    potencia_total_sf: float | None,
    data: dict,
    generated_at: datetime | None = None,
    file_name: str | None = None,
) -> dict:
    generated_at = generated_at or datetime.now()
    return {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "file_name": normalize_report_filename(file_name, generated_at),
        "inputs": {
            "irradiacion": irradiacion,
            "temperatura": temperatura,
            "potencia_total_sf": potencia_total_sf,
        },
        "results": data,
        "units": data.get("unidades"),
    }


def build_csv_content(payload: dict) -> str:
    inputs = payload["inputs"]
    results = payload["results"]
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")

    writer.writerow(["Reporte de predicción de energía fotovoltaica"])
    writer.writerow(["Generado en", payload["generated_at"]])
    writer.writerow(["Irradiación (kWh/m²)", _format_number(inputs["irradiacion"])])
    writer.writerow(["Temperatura (°C)", _format_number(inputs["temperatura"])])
    writer.writerow(
        [
            "Potencia total del SF (kWp)",
            _format_optional_number(inputs["potencia_total_sf"], "No especificada"),
        ]
    )
    writer.writerow(["Unidades", payload.get("units", "")])
    writer.writerow([])
    writer.writerow(["Período", "Concepto", "Valor", "Unidad"])

    for period_key, period_label in PERIOD_LABELS:
        period_values = results.get(period_key, {})
        for metric_key, metric_label in MODEL_LABELS:
            writer.writerow(
                [
                    period_label,
                    metric_label,
                    _format_number(period_values.get(metric_key)),
                    "kWh/kWp",
                ]
            )
        if period_values.get("total_sf") is not None:
            writer.writerow(
                [
                    period_label,
                    "Total SF estimado",
                    _format_number(period_values["total_sf"]),
                    "kWh",
                ]
            )

    return buffer.getvalue()


def _format_number(value: float | int | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.2f}"


def _format_optional_number(value: float | int | None, fallback: str) -> str:
    if value is None:
        return fallback
    return _format_number(value)
