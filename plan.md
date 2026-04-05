# Plan del Proyecto

Ultima actualizacion: 2026-04-05

## Objetivo actual

Mantener una aplicacion de prediccion de energia fotovoltaica clara, estable y facil de ejecutar, con una UI en Flet y una API en FastAPI.

## Estado actual

- UI principal en `Appweb_web.py`
- API en `api.py`
- Logica de calculo en `predictor.py`
- Modelos `.pkl` ya disponibles en `models/`
- Inputs de irradiacion y temperatura ya muestran ejemplos y rangos sugeridos
- Alineacion de inputs ya corregida
- Ruta de despliegue simplificada en `Appweb_web.py` + `main.py`
- Configuracion de Render creada en `render.yaml`
- Version de Python fijada en `.python-version`
- Archivo `.gitignore` agregado para no subir basura de entorno

## Mejoras propuestas

### Alta prioridad

- Agregar validaciones de rango en la UI
  - Irradiacion sugerida: `1,5 a 8`
  - Temperatura sugerida: `15 a 24`
- Unificar oficialmente cual archivo queda como UI canonica del proyecto
- Confirmar despliegue real en Render con Python `3.11`

### Prioridad media

- Agregar texto de ayuda tambien al campo de potencia para mantener simetria visual
- Mejorar la presentacion de resultados con mas espaciado y mejor jerarquia visual
- Agregar una seccion informativa con unidades y explicacion de lo que significa `kWh/kWp`
- Mostrar el endpoint o estado de conexion de la API dentro de la UI cuando corra en modo desplegado

### Prioridad tecnica

- Crear pruebas basicas para `predictor.calcular(...)`
- Agregar README corto de despliegue para Render y GitHub
- Revisar codificacion de caracteres en archivos antiguos
- Limpiar scripts experimentales o moverlos a una carpeta `legacy/` o `experimentos/`

## Proximas tareas sugeridas

1. Validar rangos de entrada y mostrar mensajes amigables.
2. Probar el despliegue real en Render.
3. Agregar memoria visual consistente al campo de potencia.
4. Documentar cual archivo es la version oficial de la app.
5. Ordenar archivos antiguos para que el proyecto sea mas facil de mantener.

## Regla de mantenimiento

Cada vez que hagamos un cambio, este archivo se actualizara para reflejar:

- Que se hizo
- Que queda pendiente
- Cual es la siguiente mejora recomendada

## Historial breve

### 2026-04-05

- Se creo `code.md` para guardar contexto operativo del proyecto.
- Se creo `plan.md` para mantener mejoras y siguientes pasos.
- Se registraron los cambios recientes en `Appweb_web.py`:
  - ejemplos y rangos sugeridos en inputs
  - correccion de alineacion visual en la fila de campos
- Se adapto `Appweb_web.py` para despliegue sin dependencia de `127.0.0.1`.
- Se simplifico `main.py` para exportar directamente la app Flet como ASGI.
- Se cambio la estrategia de rutas web a `hash` para mitigar errores tipo 404 en despliegue.
- Se ajusto `render.yaml` para hacer health check sobre `/`.
- Se agrego `.python-version` con `3.11` para evitar fallos de build de `pandas` en Render.
- Se creo `.gitignore` basico para evitar subir el entorno virtual y caches.
