from pathlib import Path
from urllib.parse import urlencode

import flet as ft

from predictor import calcular as calcular_prediccion
from reporting import build_csv_content, build_report_payload


PAGE_BACKGROUND = "#F3F7FB"
SURFACE = "#FFFFFF"
SURFACE_SUBTLE = "#F7FAFD"
PRIMARY = "#0B63CE"
PRIMARY_DARK = "#0A3D91"
ACCENT = "#18A999"
TEXT_PRIMARY = "#162033"
TEXT_MUTED = "#5D6B82"
BORDER = "#D8E1EC"
SUCCESS = "#1B8F63"
WARNING = "#E58A1F"
AVERAGE = "#F04E3E"
TOTAL = "#1768AC"
UNL_ICON_PATH = Path(__file__).with_name("UNL.ico")
UNL_LOGO_URL = "https://raw.githubusercontent.com/DiegolPRO/imagenes-fv/0ffcbcc44367796443d7cfddf0f2a5c4c478c55f/UNL.png"

CARD_SHADOW = [
    ft.BoxShadow(
        spread_radius=0,
        blur_radius=24,
        color=ft.colors.with_opacity(0.08, ft.colors.BLACK),
        offset=ft.Offset(0, 10),
    )
]


def main(page: ft.Page):
    page.title = "Predicción de Energía"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
    if not page.web:
        if UNL_ICON_PATH.exists():
            page.window.icon = str(UNL_ICON_PATH)
        page.window.maximized = True
        page.window.min_width = 420
        page.window.min_height = 760
    page.padding = 16
    page.bgcolor = PAGE_BACKGROUND
    page.scroll = ft.ScrollMode.AUTO
    ultimo_reporte = None

    def toast(msg: str, color=AVERAGE):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def parse_float(value: str):
        return float(value.strip().replace(",", "."))

    def set_export_state(payload: dict | None):
        nonlocal ultimo_reporte
        ultimo_reporte = payload
        if payload is None:
            download_button.disabled = True
            export_status.value = "Calcula una predicción para preparar un reporte descargable."
            export_status.color = TEXT_MUTED
        else:
            download_button.disabled = False
            export_status.value = f"Reporte listo para descargar: {payload['file_name']}"
            export_status.color = SUCCESS
        page.update()

    def save_report_to_disk(e: ft.FilePickerResultEvent):
        if not ultimo_reporte or not e.path:
            return

        target_path = Path(e.path)
        if target_path.suffix.lower() != ".csv":
            target_path = target_path.with_suffix(".csv")
        target_path.write_text(build_csv_content(ultimo_reporte), encoding="utf-8-sig")
        toast(f"Reporte guardado en {target_path.name}.", color=SUCCESS)

    def preparar_descarga(_):
        if not ultimo_reporte:
            return toast("Primero genera una predicción para preparar el reporte.")

        if page.web:
            inputs = ultimo_reporte["inputs"]
            params = {
                "irradiacion": inputs["irradiacion"],
                "temperatura": inputs["temperatura"],
                "file_name": ultimo_reporte["file_name"],
            }
            if inputs["potencia_total_sf"] is not None:
                params["potencia_total_sf"] = inputs["potencia_total_sf"]
            page.launch_url(f"/api/download/report.csv?{urlencode(params)}")
            return toast("Descarga CSV iniciada en el navegador.", color=SUCCESS)

        file_picker.save_file(
            dialog_title="Guardar reporte CSV",
            file_name=ultimo_reporte["file_name"],
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"],
        )

    def set_metric_line(control: ft.Text, label: str, value: str, value_color: str = TEXT_PRIMARY):
        control.spans = [
            ft.TextSpan(
                label,
                ft.TextStyle(size=14, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            ),
            ft.TextSpan(
                value,
                ft.TextStyle(size=17, color=value_color, weight=ft.FontWeight.W_700),
            ),
        ]

    def make_period_card(title: str, subtitle: str, accent_color: str, icon_name: str):
        avg_value = ft.Text(
            "Esperando cálculo",
            size=24,
            weight=ft.FontWeight.W_700,
            color=TEXT_PRIMARY,
        )
        avg_label = ft.Text(
            "Promedio ponderado del ensamble",
            size=12,
            color=TEXT_MUTED,
        )
        reg_line = ft.Text(spans=[])
        bos_line = ft.Text(spans=[])
        gbr_line = ft.Text(spans=[])
        total_text = ft.Text(
            "",
            size=14,
            color=TOTAL,
            weight=ft.FontWeight.W_700,
        )
        total_box = ft.Container(
            visible=False,
            bgcolor=ft.colors.with_opacity(0.08, TOTAL),
            border=ft.border.all(1, ft.colors.with_opacity(0.12, TOTAL)),
            border_radius=16,
            padding=14,
            content=ft.Row(
                [
                    ft.Icon(ft.icons.BOLT_OUTLINED, size=18, color=TOTAL),
                    total_text,
                ],
                spacing=10,
            ),
        )

        card = ft.Container(
            col={"xs": 12, "md": 6, "lg": 4},
            bgcolor=SURFACE,
            border_radius=24,
            padding=22,
            shadow=CARD_SHADOW,
            border=ft.border.all(1, BORDER),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=50,
                                height=50,
                                border_radius=16,
                                bgcolor=ft.colors.with_opacity(0.12, accent_color),
                                alignment=ft.alignment.center,
                                content=ft.Icon(icon_name, color=accent_color, size=26),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        title,
                                        size=20,
                                        weight=ft.FontWeight.W_700,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        subtitle,
                                        size=12,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        margin=ft.margin.only(top=16, bottom=16),
                        padding=18,
                        border_radius=20,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.center_left,
                            end=ft.alignment.center_right,
                            colors=[
                                ft.colors.with_opacity(0.14, accent_color),
                                ft.colors.with_opacity(0.04, accent_color),
                            ],
                        ),
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Promedio recomendado",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_MUTED,
                                ),
                                avg_value,
                                avg_label,
                            ],
                            spacing=6,
                        ),
                    ),
                    ft.Column(
                        [
                            reg_line,
                            ft.Divider(height=14, color=BORDER),
                            bos_line,
                            ft.Divider(height=14, color=BORDER),
                            gbr_line,
                            ft.Divider(height=18, color=BORDER),
                            total_box,
                        ],
                        spacing=0,
                    ),
                ],
                spacing=0,
            ),
        )

        return card, {
            "avg_value": avg_value,
            "avg_label": avg_label,
            "reg_line": reg_line,
            "bos_line": bos_line,
            "gbr_line": gbr_line,
            "total_box": total_box,
            "total_text": total_text,
        }

    def info_pill(label: str, value: str, detail: str, width: int | None = 290):
        return ft.Tooltip(
            message=detail,
            wait_duration=250,
            show_duration=7000,
            prefer_below=False,
            padding=14,
            margin=12,
            border_radius=16,
            bgcolor=ft.colors.with_opacity(0.96, PRIMARY_DARK),
            text_style=ft.TextStyle(size=12, color=ft.colors.WHITE, weight=ft.FontWeight.W_500),
            content=ft.Container(
                width=width,
                bgcolor=ft.colors.with_opacity(0.16, ft.colors.WHITE),
                border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.WHITE)),
                border_radius=18,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(label, size=11, color=ft.colors.WHITE70),
                                ft.Text(value, size=15, weight=ft.FontWeight.W_700, color=ft.colors.WHITE),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        ft.Container(
                            width=30,
                            height=30,
                            border_radius=999,
                            bgcolor=ft.colors.with_opacity(0.12, ft.colors.WHITE),
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=ft.colors.WHITE70),
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        )

    def styled_input(label: str, hint: str, helper: str | None, icon_name: str):
        return ft.TextField(
            label=label,
            hint_text=hint,
            helper_text=helper,
            filled=True,
            bgcolor=SURFACE_SUBTLE,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            border_radius=18,
            cursor_color=PRIMARY,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=icon_name,
            text_style=ft.TextStyle(size=16, color=TEXT_PRIMARY, weight=ft.FontWeight.W_500),
            label_style=ft.TextStyle(color=TEXT_MUTED, size=14),
            hint_style=ft.TextStyle(color=ft.colors.with_opacity(0.55, TEXT_MUTED)),
            expand=True,
        )

    irradiacion_input = styled_input(
        "Irradiación (kWh/m²)",
        "Ej: 1,5 a 8",
        "Rango sugerido: 1,5 a 8 kWh/m²",
        ft.icons.WB_SUNNY_OUTLINED,
    )
    temperatura_input = styled_input(
        "Temperatura (°C)",
        "Ej: 15 a 24",
        "Rango sugerido: 15 a 24 °C",
        ft.icons.DEVICE_THERMOSTAT,
    )
    potencia_sf_input = styled_input(
        "Potencia total del SF (kWp) - opcional",
        "Ej: 20",
        "Se usa para estimar la energía total del sistema",
        ft.icons.BOLT_OUTLINED,
    )
    file_picker = ft.FilePicker(on_result=save_report_to_disk)
    page.overlay.append(file_picker)

    diaria_card, diaria_refs = make_period_card(
        "Predicción diaria",
        "Rendimiento específico por día",
        SUCCESS,
        ft.icons.CALENDAR_VIEW_DAY_OUTLINED,
    )
    mensual_card, mensual_refs = make_period_card(
        "Predicción mensual",
        "Proyección a 30 días",
        WARNING,
        ft.icons.DATE_RANGE_OUTLINED,
    )
    anual_card, anual_refs = make_period_card(
        "Predicción anual",
        "Escenario estimado a 12 meses",
        PRIMARY,
        ft.icons.INSIGHTS_OUTLINED,
    )
    download_button = ft.OutlinedButton(
        "Descargar reporte",
        icon=ft.icons.DOWNLOAD_OUTLINED,
        disabled=True,
        on_click=preparar_descarga,
        style=ft.ButtonStyle(
            color=PRIMARY,
            side=ft.BorderSide(1, ft.colors.with_opacity(0.25, PRIMARY)),
            padding=ft.padding.symmetric(horizontal=18, vertical=16),
            shape=ft.RoundedRectangleBorder(radius=16),
        ),
    )
    export_status = ft.Text(
        "Calcula una predicción para preparar un reporte descargable.",
        size=12,
        color=TEXT_MUTED,
    )
    hero_badge = ft.Container(
        bgcolor=ft.colors.with_opacity(0.14, ft.colors.WHITE),
        border_radius=999,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        content=ft.Row(
            [
                ft.Icon(ft.icons.AUTO_GRAPH, color=ft.colors.WHITE, size=16),
                ft.Text(
                    "Predicción inteligente para sistemas fotovoltaicos",
                    color=ft.colors.WHITE,
                    size=12,
                    weight=ft.FontWeight.W_600,
                ),
            ],
            spacing=8,
            tight=True,
        ),
    )
    hero_title = ft.Text(
        "Predicción de Energía Fotovoltaica",
        size=36,
        weight=ft.FontWeight.W_700,
        color=ft.colors.WHITE,
    )
    hero_description = ft.Text(
        "Ingresa irradiación, temperatura y la potencia del sistema para obtener una estimación diaria, mensual y anual con tres modelos y un promedio ponderado.",
        size=15,
        color=ft.colors.WHITE70,
    )
    hero_logo = ft.Image(
        src=UNL_LOGO_URL,
        width=132,
        height=132,
        fit=ft.ImageFit.CONTAIN,
    )
    hero_logo_shell = ft.Container(
        border_radius=24,
        padding=16,
        bgcolor=ft.colors.with_opacity(0.12, ft.colors.WHITE),
        content=hero_logo,
    )
    models_pill = info_pill(
        "Modelos activos",
        "3 predictores",
        "Tipos de modelos de predicción utilizados:\n\n"
        "Regresión: Modelo estadístico que estima la relación entre variables para predecir valores continuos de forma simple y rápida.\n"
        "Bosque (Random Forest): Conjunto de múltiples árboles de decisión que mejora la precisión y reduce errores mediante el promedio de resultados.\n"
        "Gradient Boosting: Modelo avanzado que combina árboles de forma secuencial, corrigiendo errores previos para lograr predicciones más precisas.",
    )
    outputs_pill = info_pill(
        "Salidas",
        "Diaria, mensual y anual",
        "La app entrega una estimación diaria, una proyección mensual a 30 días y un escenario anual a 12 meses.",
    )
    unit_pill = info_pill(
        "Unidad base",
        "kWh/kWp",
        "La predicción base se expresa en kWh/kWp.\nSi ingresas la potencia del sistema, también se estima la energía total en kWh.",
    )
    hero_stats_column = ft.Column(
        [
            models_pill,
            outputs_pill,
            unit_pill,
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )

    def clear_period(refs):
        refs["avg_value"].value = "Esperando cálculo"
        refs["avg_label"].value = "Promedio ponderado del ensamble"
        refs["reg_line"].spans = []
        refs["bos_line"].spans = []
        refs["gbr_line"].spans = []
        refs["total_text"].value = ""
        refs["total_box"].visible = False

    def fill_period(refs, data, total_suffix: str):
        refs["avg_value"].value = f"{data['promedio']:.2f} kWh/kWp"
        refs["avg_label"].value = "Promedio ponderado recomendado"
        set_metric_line(refs["reg_line"], "Regresión: ", f"{data['regresion']:.2f} kWh/kWp")
        set_metric_line(refs["bos_line"], "Bosque: ", f"{data['bosque']:.2f} kWh/kWp")
        set_metric_line(refs["gbr_line"], "Gradient Boosting: ", f"{data['gbr']:.2f} kWh/kWp")
        if data["total_sf"] is not None:
            refs["total_text"].value = f"Total SF estimado: *{data['total_sf']:.2f} {total_suffix}"
            refs["total_box"].visible = True
        else:
            refs["total_text"].value = ""
            refs["total_box"].visible = False

    def limpiar(_):
        for text_field in [irradiacion_input, temperatura_input, potencia_sf_input]:
            text_field.value = ""
        for refs in [diaria_refs, mensual_refs, anual_refs]:
            clear_period(refs)
        set_export_state(None)

    def calcular(_):
        try:
            irradiacion = parse_float(irradiacion_input.value)
            temperatura = parse_float(temperatura_input.value)
            potencia = parse_float(potencia_sf_input.value) if potencia_sf_input.value else None
        except (AttributeError, ValueError):
            return toast("Ingresa valores numéricos válidos en los campos requeridos.")

        try:
            data = calcular_prediccion(
                irradiacion=irradiacion,
                temperatura=temperatura,
                potencia_total_sf=potencia,
            )
            fill_period(diaria_refs, data["diaria"], "kWh")
            fill_period(mensual_refs, data["mensual"], "kWh")
            fill_period(anual_refs, data["anual"], "kWh")
            set_export_state(build_report_payload(irradiacion, temperatura, potencia, data))
            toast("Predicción actualizada correctamente.", color=SUCCESS)
        except Exception as exc:
            print(f"[calcular] Error: {exc}")
            return toast("No se pudo generar la predicción en este momento.")

    hero = ft.Container(
        border_radius=28,
        padding=26,
        shadow=CARD_SHADOW,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[PRIMARY_DARK, PRIMARY, ACCENT],
        ),
        content=ft.ResponsiveRow(
            [
                ft.Container(
                    col={"xs": 12, "lg": 8},
                    content=ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"xs": 12, "sm": 4, "md": 3},
                                alignment=ft.alignment.center_left,
                                content=hero_logo_shell,
                            ),
                            ft.Container(
                                col={"xs": 12, "sm": 8, "md": 9},
                                content=ft.Column(
                                    [
                                        hero_badge,
                                        hero_title,
                                        hero_description,
                                    ],
                                    spacing=14,
                                ),
                            ),
                        ],
                        spacing=18,
                        run_spacing=18,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.Container(
                    col={"xs": 12, "lg": 4},
                    content=hero_stats_column,
                ),
            ],
            spacing=20,
            run_spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    form_section = ft.Container(
        bgcolor=SURFACE,
        border_radius=24,
        padding=24,
        shadow=CARD_SHADOW,
        border=ft.border.all(1, BORDER),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=46,
                            height=46,
                            border_radius=14,
                            bgcolor=ft.colors.with_opacity(0.12, PRIMARY),
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.icons.TUNE, color=PRIMARY, size=24),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Parámetros de entrada",
                                    size=22,
                                    weight=ft.FontWeight.W_700,
                                    color=TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "Usa valores promedio del sitio para obtener una proyección consistente.",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=14,
                ),
                ft.ResponsiveRow(
                    [
                        ft.Container(col={"xs": 12, "sm": 6, "lg": 4}, content=irradiacion_input),
                        ft.Container(col={"xs": 12, "sm": 6, "lg": 4}, content=temperatura_input),
                        ft.Container(col={"xs": 12, "sm": 6, "lg": 4}, content=potencia_sf_input),
                    ],
                    spacing=18,
                    run_spacing=10,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Calcular predicción",
                            icon=ft.icons.AUTO_GRAPH,
                            on_click=calcular,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY,
                                color=ft.colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=22, vertical=18),
                                shape=ft.RoundedRectangleBorder(radius=16),
                            ),
                        ),
                        ft.OutlinedButton(
                            "Limpiar",
                            icon=ft.icons.CLEANING_SERVICES_OUTLINED,
                            on_click=limpiar,
                            style=ft.ButtonStyle(
                                color=TEXT_PRIMARY,
                                side=ft.BorderSide(1, BORDER),
                                padding=ft.padding.symmetric(horizontal=20, vertical=18),
                                shape=ft.RoundedRectangleBorder(radius=16),
                            ),
                        ),
                    ],
                    spacing=12,
                    wrap=True,
                ),
            ],
            spacing=22,
        ),
    )

    results_actions = ft.Column(
        [
            download_button,
            export_status,
        ],
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )
    results_actions_container = ft.Container(
        col={"xs": 12, "lg": 4},
        alignment=ft.alignment.center_right,
        content=results_actions,
    )
    results_header = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "lg": 8},
                content=ft.Column(
                    [
                        ft.Text(
                            "Resumen de resultados",
                            size=24,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        ft.Text(
                            "Las tarjetas destacan el promedio del ensamble y el detalle por modelo.",
                            size=13,
                            color=TEXT_MUTED,
                        ),
                    ],
                    spacing=4,
                ),
            ),
            results_actions_container,
        ],
        spacing=18,
        run_spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    info_banner = ft.Container(
        bgcolor=ft.colors.with_opacity(0.08, ACCENT),
        border_radius=18,
        border=ft.border.all(1, ft.colors.with_opacity(0.12, ACCENT)),
        padding=16,
        content=ft.Row(
            [
                ft.Icon(ft.icons.INFO_OUTLINE, color=ACCENT, size=20),
                ft.Text(
                    "*Suponiendo que el comportamiento es igual en todos los modelos.",
                    size=13,
                    color=TEXT_PRIMARY,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    results_grid = ft.ResponsiveRow(
        [diaria_card, mensual_card, anual_card],
        spacing=18,
        run_spacing=18,
    )

    results_section = ft.Container(
        bgcolor=SURFACE,
        border_radius=24,
        padding=24,
        shadow=CARD_SHADOW,
        border=ft.border.all(1, BORDER),
        content=ft.Column(
            [
                results_header,
                results_grid,
                info_banner,
            ],
            spacing=22,
        ),
    )

    content = ft.ResponsiveRow(
        [
            ft.Container(col=12, content=hero),
            ft.Container(col=12, content=form_section),
            ft.Container(col=12, content=results_section),
        ],
        spacing=22,
        run_spacing=22,
    )

    page.add(content)
    set_export_state(None)


if __name__ == "__main__":
    ft.app(target=main)
