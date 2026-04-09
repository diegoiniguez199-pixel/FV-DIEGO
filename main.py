from fastapi import FastAPI
import flet as ft

from Appweb_web import main as flet_main
from api import app as api_app


flet_app = ft.app(
    target=flet_main,
    export_asgi_app=True,
    route_url_strategy="hash",
)

app = FastAPI(title="Prediccion Energia FV")
app.mount("/api", api_app)
app.mount("/", flet_app)
