# predictor.py
import joblib
import pandas as pd

# Cargar modelos UNA sola vez (importando este archivo)
modelo_regresion = joblib.load('models/model_regresion.pkl')
modelo_bosque = joblib.load('models/model_bosque.pkl')
modelo_gbr = joblib.load('models/model_gbr.pkl')

def predecir_energia(modelo, irradiacion, temperatura):
    X_nuevo = pd.DataFrame(
        [[irradiacion, temperatura]],
        columns=['Irradiación321', 'Temperatura ambiente']
    )
    energia_predicha = modelo.predict(X_nuevo)
    return float(energia_predicha[0])

def predecir_energia_ensamble(irradiacion, temperatura):
    modelos = [modelo_regresion, modelo_bosque, modelo_gbr]
    predicciones = [predecir_energia(m, irradiacion, temperatura) for m in modelos]
    pesos = [0.2, 0.4, 0.4]
    return float(sum(p * pred for p, pred in zip(pesos, predicciones)))

def calcular(irradiacion: float, temperatura: float, potencia_total_sf: float | None = None):
    # Diarias (tu mismo /4.85)
    diaria_reg = predecir_energia(modelo_regresion, irradiacion, temperatura) / 4.85
    diaria_bos = predecir_energia(modelo_bosque, irradiacion, temperatura) / 4.85
    diaria_gbr = predecir_energia(modelo_gbr, irradiacion, temperatura) / 4.85
    diaria_prom = predecir_energia_ensamble(irradiacion, temperatura) / 4.85

    # Mensuales
    mensual_reg = diaria_reg * 30
    mensual_bos = diaria_bos * 30
    mensual_gbr = diaria_gbr * 30
    mensual_prom = diaria_prom * 30

    # Anuales
    anual_reg = mensual_reg * 12
    anual_bos = mensual_bos * 12
    anual_gbr = mensual_gbr * 12
    anual_prom = mensual_prom * 12

    # Totales (si potencia viene)
    total_diaria = diaria_prom * potencia_total_sf if potencia_total_sf is not None else None
    total_mensual = mensual_prom * potencia_total_sf if potencia_total_sf is not None else None
    total_anual = anual_prom * potencia_total_sf if potencia_total_sf is not None else None

    return {
        "diaria": {
            "regresion": diaria_reg,
            "bosque": diaria_bos,
            "gbr": diaria_gbr,
            "promedio": diaria_prom,
            "total_sf": total_diaria,
        },
        "mensual": {
            "regresion": mensual_reg,
            "bosque": mensual_bos,
            "gbr": mensual_gbr,
            "promedio": mensual_prom,
            "total_sf": total_mensual,
        },
        "anual": {
            "regresion": anual_reg,
            "bosque": anual_bos,
            "gbr": anual_gbr,
            "promedio": anual_prom,
            "total_sf": total_anual,
        },
        "unidades": "kWh/kWp (predicciones) y kWh (total_sf)"
    }