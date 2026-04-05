import flet as ft

from predictor import calcular as calcular_prediccion


def main(page: ft.Page):
    page.title = "Predicción de Energía"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
    if not page.web:
        page.window.width = 1300
        page.window.height = 820
    page.padding = 18
    page.bgcolor = ft.colors.GREY_100
    page.scroll = ft.ScrollMode.AUTO

    def toast(msg: str, color=ft.colors.RED):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.colors.WHITE),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def parse_float(value: str):
        return float(value.strip().replace(",", "."))

    def make_result_text():
        return ft.Text("", size=14, spans=[])

    def set_bold_label(text_control: ft.Text, label: str, value: str):
        text_control.spans = [
            ft.TextSpan(label + value, ft.TextStyle(weight=ft.FontWeight.BOLD))
        ]

    irradiacion_input = ft.TextField(
        label="Irradiación (kWh/m²)",
        hint_text="Ej: 1,5 a 8",
        helper_text="Rango sugerido: 1,5 a 8 kWh/m²",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=420,
    )
    temperatura_input = ft.TextField(
        label="Temperatura (°C)",
        hint_text="Ej: 15 a 24",
        helper_text="Rango sugerido: 15 a 24 °C",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=320,
    )
    potencia_sf_input = ft.TextField(
        label="Potencia total del SF (kWp) - opcional",
        hint_text="Ej: 20",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=320,
    )

    d_reg = make_result_text()
    d_bos = make_result_text()
    d_gbr = make_result_text()
    d_prom = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
    d_total = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)

    m_reg = make_result_text()
    m_bos = make_result_text()
    m_gbr = make_result_text()
    m_prom = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
    m_total = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)

    a_reg = make_result_text()
    a_bos = make_result_text()
    a_gbr = make_result_text()
    a_prom = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
    a_total = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)

    def card(title, controls):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            title,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.GREEN_800,
                        ),
                        padding=8,
                        bgcolor=ft.colors.GREEN_50,
                        border_radius=8,
                    ),
                    ft.Divider(),
                    *controls,
                ]
            ),
            bgcolor=ft.colors.WHITE,
            padding=16,
            border_radius=14,
            width=390,
        )

    def limpiar(_):
        for t in [irradiacion_input, temperatura_input, potencia_sf_input]:
            t.value = ""
        for r in [d_reg, d_bos, d_gbr, m_reg, m_bos, m_gbr, a_reg, a_bos, a_gbr]:
            r.spans = []
        for r in [d_prom, d_total, m_prom, m_total, a_prom, a_total]:
            r.value = ""
        page.update()

    def calcular(_):
        try:
            irradiacion = parse_float(irradiacion_input.value)
            temperatura = parse_float(temperatura_input.value)
            potencia = parse_float(potencia_sf_input.value) if potencia_sf_input.value else None
        except (AttributeError, ValueError):
            return toast("Datos inválidos")

        try:
            data = calcular_prediccion(
                irradiacion=irradiacion,
                temperatura=temperatura,
                potencia_total_sf=potencia,
            )
        except Exception:
            return toast("Error calculando la predicción")

        diaria = data["diaria"]
        mensual = data["mensual"]
        anual = data["anual"]

        set_bold_label(d_reg, "Regresión: ", f"{diaria['regresion']:.2f} kWh/kWp")
        set_bold_label(d_bos, "Bosque: ", f"{diaria['bosque']:.2f} kWh/kWp")
        set_bold_label(d_gbr, "Gradient Boosting: ", f"{diaria['gbr']:.2f} kWh/kWp")
        d_prom.value = f"Promedio: {diaria['promedio']:.2f} kWh/kWp"
        d_total.value = f"Total SF: {diaria['total_sf']:.2f} kWh" if potencia else ""

        set_bold_label(m_reg, "Regresión: ", f"{mensual['regresion']:.2f} kWh/kWp")
        set_bold_label(m_bos, "Bosque: ", f"{mensual['bosque']:.2f} kWh/kWp")
        set_bold_label(m_gbr, "Gradient Boosting: ", f"{mensual['gbr']:.2f} kWh/kWp")
        m_prom.value = f"Promedio: {mensual['promedio']:.2f} kWh/kWp"
        m_total.value = f"Total SF: {mensual['total_sf']:.2f} kWh" if potencia else ""

        set_bold_label(a_reg, "Regresión: ", f"{anual['regresion']:.2f} kWh/kWp")
        set_bold_label(a_bos, "Bosque: ", f"{anual['bosque']:.2f} kWh/kWp")
        set_bold_label(a_gbr, "Gradient Boosting: ", f"{anual['gbr']:.2f} kWh/kWp")
        a_prom.value = f"Promedio: {anual['promedio']:.2f} kWh/kWp"
        a_total.value = f"Total SF: {anual['total_sf']:.2f} kWh" if potencia else ""

        toast("Cálculo listo", color=ft.colors.GREEN)
        page.update()

    header = ft.Container(
        content=ft.Text(
            "Predicción de Energía Fotovoltaica",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
        ),
        bgcolor=ft.colors.BLUE_600,
        padding=16,
        border_radius=12,
    )

    form = ft.Column(
        [
            header,
            ft.Row(
                [irradiacion_input, temperatura_input, potencia_sf_input],
                vertical_alignment=ft.CrossAxisAlignment.START,
                wrap=True,
            ),
            ft.Row(
                [
                    ft.ElevatedButton("Calcular", on_click=calcular),
                    ft.OutlinedButton("Limpiar", on_click=limpiar),
                ]
            ),
        ]
    )

    results = ft.Row(
        [
            card("Predicciones diarias", [d_reg, d_bos, d_gbr, d_prom, d_total]),
            card("Predicciones mensuales", [m_reg, m_bos, m_gbr, m_prom, m_total]),
            card("Predicciones anuales", [a_reg, a_bos, a_gbr, a_prom, a_total]),
        ],
        wrap=True,
    )

    page.add(form, results)


if __name__ == "__main__":
    ft.app(target=main)
