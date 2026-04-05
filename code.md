# Contexto del Proyecto

Ultima actualizacion: 2026-04-05

## Resumen

Este proyecto predice energia fotovoltaica a partir de:

- Irradiacion
- Temperatura ambiente
- Potencia total del sistema fotovoltaico (opcional)

La aplicacion principal actual combina:

- Un backend con FastAPI
- Una interfaz de usuario con Flet
- Modelos de machine learning entrenados previamente y guardados en `models/`

Desde 2026-04-05 existe una ruta de despliegue web lista para Render con una sola aplicacion ASGI en `main.py`.

## Flujo principal

### Flujo historico

1. El usuario ingresa irradiacion, temperatura y opcionalmente la potencia total del sistema.
2. La interfaz Flet envia esos datos al endpoint `POST /predict`.
3. La API llama a `predictor.calcular(...)`.
4. `predictor.py` carga los modelos y devuelve predicciones:
   - Diarias
   - Mensuales
   - Anuales
5. La UI muestra resultados por modelo y un promedio ponderado.

### Flujo recomendado actual

1. `main.py` exporta directamente la app Flet como ASGI.
2. `Appweb_web.py` ejecuta el calculo directamente con `predictor.calcular(...)`.
3. Render solo necesita ejecutar `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. El health check de Render puede hacerse sobre `/`.

## Archivos importantes

### `Appweb_web.py`

Interfaz Flet principal actual del proyecto.

Responsabilidades:

- Construir la ventana principal
- Recibir los datos del usuario
- Ejecutar el calculo directamente con `predictor.calcular(...)`
- Mostrar resultados diarios, mensuales y anuales

Cambios recientes:

- Se agregaron ayudas visuales en los inputs:
  - Irradiacion: ejemplo y rango sugerido `1,5 a 8`
  - Temperatura: ejemplo y rango sugerido `15 a 24`
  - Potencia total: ejemplo `20`
- Se ajusto la alineacion vertical de la fila de inputs para evitar que el tercer campo quede descuadrado cuando otros tienen `helper_text`.
- Se adapto para despliegue web:
  - ya no depende de `127.0.0.1`
  - puede ejecutarse localmente o montarse desde `main.py`
  - soporta mejor layout responsivo con `wrap=True`

### `api.py`

Backend FastAPI.

Endpoints actuales:

- `POST /predict`: recibe irradiacion, temperatura y potencia opcional
- `GET /health`: verifica que la API este activa

Cuando se monta desde `main.py`, esos endpoints quedan publicados bajo:

- `/api/predict`
- `/api/health`

### `main.py`

Punto de entrada recomendado para produccion.

Responsabilidades:

- Exportar la app Flet como ASGI usando `Appweb_web.py`
- Servir como entrypoint de Render
- Usar estrategia de rutas `hash` para evitar problemas de 404 en despliegue web

### `render.yaml`

Archivo de configuracion para Render.

Configuracion actual:

- `runtime: python`
- `plan: free`
- `buildCommand: pip install -r requirements.txt`
- `startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT`
- `healthCheckPath: /`

### `.python-version`

Fija la version de Python recomendada para despliegue en Render.

Valor actual:

- `3.11`

Motivo:

- `pandas 2.2.2` soporta Python `3.9`, `3.10`, `3.11` y `3.12`
- Render usa versiones de Python muy nuevas por defecto si no se fija una version
- Esto puede provocar que `pip` intente compilar `pandas` desde fuente y falle durante el build

### `predictor.py`

Logica central de prediccion.

Responsabilidades:

- Cargar modelos una sola vez:
  - `models/model_regresion.pkl`
  - `models/model_bosque.pkl`
  - `models/model_gbr.pkl`
- Predecir energia con cada modelo
- Calcular un ensamble ponderado con pesos:
  - Regresion: `0.2`
  - Bosque: `0.4`
  - Gradient Boosting: `0.4`
- Convertir resultados a:
  - Diario
  - Mensual
  - Anual
- Calcular energia total del sistema si se entrega `potencia_total_sf`

## Modelos y datos

Los modelos actuales vienen de scripts de entrenamiento como:

- `FMAMentrenamiento.py`
- `nuevoentrenamiento.py`
- `pruebaconmodelos.py`

Los datos historicos parecen venir principalmente de archivos Excel como:

- `FMAM.xlsx`
- `bandaFV.xlsx`
- `datos_fotovoltaicos.xlsx`

Variables principales usadas en entrenamiento:

- `Irradiacion321`
- `Temperatura ambiente`
- `Energia321`

## Como ejecutar el proyecto

Desde la raiz `D:\Diego Tesis\FV`:

### Opcion recomendada para despliegue local similar a produccion

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Luego abrir:

- `http://127.0.0.1:8000/` para la UI

### Opcion local de UI solamente

```powershell
.\.venv\Scripts\python.exe Appweb_web.py
```

### Opcion heredada

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

```powershell
.\.venv\Scripts\python.exe Appweb_web.py
```

## Dependencias clave

- `flet`
- `fastapi`
- `uvicorn`
- `requests`
- `pandas`
- `joblib`
- `scikit-learn`

## Observaciones del estado actual

- El repositorio tiene varios archivos de pruebas, borradores y versiones antiguas.
- `Appweb.py` y `Appweb_web.py` resuelven problemas parecidos, pero con enfoques distintos.
- `Appweb_web.py` es la UI principal.
- `main.py` es el entrypoint de produccion para Render.
- El despliegue en Render debe usar Python `3.11` para compatibilidad con dependencias fijadas.
- Hay algunos textos con problemas de codificacion en ciertos archivos antiguos.
- El backend y los modelos responden correctamente en el entorno actual.

## Convencion de mantenimiento de este archivo

Este archivo se actualizara cada vez que hagamos cambios relevantes en:

- Arquitectura
- Flujo de ejecucion
- Archivos principales
- UI o API
- Modelos o datos
