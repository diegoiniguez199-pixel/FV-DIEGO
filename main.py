from contextlib import asynccontextmanager

import flet.fastapi as flet_fastapi
from fastapi import FastAPI

from api import app as api_app
from Appweb_web import main as flet_main


@asynccontextmanager
async def lifespan(app: FastAPI):
    await flet_fastapi.app_manager.start()
    yield
    await flet_fastapi.app_manager.shutdown()


app = FastAPI(
    title="Predicción de Energía Fotovoltaica",
    lifespan=lifespan,
)
app.mount("/api", api_app)
app.mount("/", flet_fastapi.app(flet_main, route_url_strategy="hash"))
