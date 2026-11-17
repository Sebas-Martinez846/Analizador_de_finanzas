from matplotlib.figure import Figure


class GeneradorGraficos:
    """
    Servicio encargado de construir las figuras de Matplotlib listas para ser
    incrustadas en la interfaz gráfica (PySide6).
    """

    def __init__(self, color_fondo: str = "#1e1e2e", color_texto: str = "#cdd6f4"):
        self._color_fondo = color_fondo
        self._color_texto = color_texto
        self._paleta_categorias = [
            "#89b4fa",  # Azul
            "#f38ba8",  # Rosa/Rojo suave
            "#a6e3a1",  # Verde menta
            "#fab387",  # Naranja
            "#cba6f7",  # Lavanda
            "#94e2d5",  # Turquesa
            "#f9e2af",  # Amarillo pastel
        ]

    def generar_dashboard_financiero(
        self,
        gastos_por_categoria: dict[str, float],
        total_ingresos: float,
        total_gastos: float
    ) -> Figure:
        """
        Construye y retorna una figura de Matplotlib con dos gráficos:
        1. Gráfico de dona con la distribución de gastos por categoría.
        2. Gráfico de barras comparando Ingresos vs. Gastos.
        """
        figura = Figure(figsize=(9, 3.8), dpi=100)
        figura.patch.set_facecolor(self._color_fondo)

        # Subgráfico 1: Dona de gastos por categoría
        ax_dona = figura.add_subplot(121)
        self._dibujar_dona_gastos(ax_dona, gastos_por_categoria)

        # Subgráfico 2: Barras de Ingresos vs Gastos
        ax_barras = figura.add_subplot(122)
        self._dibujar_barras_balance(ax_barras, total_ingresos, total_gastos)

        figura.tight_layout(pad=2.0)
        return figura

    def _dibujar_dona_gastos(self, ax, gastos_por_categoria: dict[str, float]) -> None:
        ax.set_facecolor(self._color_fondo)
        ax.set_title(
            "Distribución de Gastos",
            color=self._color_texto,
            fontsize=11,
            fontweight="bold",
            pad=12
        )

        if not gastos_por_categoria or sum(gastos_por_categoria.values()) == 0:
            ax.text(
                0.5, 0.5,
                "Sin gastos registrados",
                ha="center", va="center",
                color="#7f849c",
                fontsize=10
            )
            ax.axis("off")
            return

        etiquetas = list(gastos_por_categoria.keys())
        valores = list(gastos_por_categoria.values())
        colores = self._paleta_categorias[:len(etiquetas)]

        wedges, texts, autotexts = ax.pie(
            valores,
            labels=etiquetas,
            autopct="%1.1f%%",
            startangle=140,
            colors=colores,
            pctdistance=0.78,
            wedgeprops={"width": 0.42, "edgecolor": self._color_fondo, "linewidth": 2},
            textprops={"color": self._color_texto, "fontsize": 8.5}
        )

        for autotext in autotexts:
            autotext.set_color("#11111b")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(8)

    def _dibujar_barras_balance(self, ax, total_ingresos: float, total_gastos: float) -> None:
        ax.set_facecolor(self._color_fondo)
        ax.set_title(
            "Ingresos vs. Gastos",
            color=self._color_texto,
            fontsize=11,
            fontweight="bold",
            pad=12
        )

        categorias = ["Ingresos", "Gastos"]
        valores = [total_ingresos, total_gastos]
        colores = ["#a6e3a1", "#f38ba8"]

        barras = ax.bar(categorias, valores, color=colores, width=0.45, zorder=3)

        # Estilizado de ejes y cuadrícula
        ax.tick_params(colors=self._color_texto, labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#45475a")
        ax.spines["bottom"].set_color("#45475a")
        ax.yaxis.grid(True, linestyle="--", alpha=0.25, color="#7f849c", zorder=0)

        # Margen superior extra para que quepa el texto encima de la barra
        max_valor = max(valores) if max(valores) > 0 else 100
        ax.set_ylim(0, max_valor * 1.22)

        # Etiquetas numéricas encima de cada barra
        for barra in barras:
            altura = barra.get_height()
            ax.annotate(
                f"${altura:,.0f}",
                xy=(barra.get_x() + barra.get_width() / 2, altura),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=self._color_texto,
                fontsize=8.5,
                fontweight="bold"
            )