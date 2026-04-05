import flet as ft

from Appweb_web import main as flet_main


app = ft.app(
    target=flet_main,
    export_asgi_app=True,
    route_url_strategy="hash",
)
