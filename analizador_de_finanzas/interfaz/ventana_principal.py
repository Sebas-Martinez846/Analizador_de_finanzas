import datetime
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QProgressBar,
    QAbstractItemView
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from modelos.transaccion import Ingreso, Gasto
from servicios.gestor_financiero import GestorFinanciero
from servicios.generador_grafico import GeneradorGraficos


ESTILOS_QSS = """
QMainWindow, QWidget#FondoPrincipal {
    background-color: #181825;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame.Tarjeta {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 10px;
}
QLabel.TituloSeccion {
    font-size: 14px;
    font-weight: bold;
    color: #89b4fa;
}
QLabel.KpiTitulo {
    font-size: 12px;
    color: #a6adc8;
}
QLabel.KpiValor {
    font-size: 20px;
    font-weight: bold;
}
QLineEdit, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QLineEdit:disabled, QComboBox:disabled {
    background-color: #181825;
    color: #6c7086;
}
QPushButton {
    background-color: #89b4fa;
    color: #11111b;
    font-weight: bold;
    border-radius: 6px;
    padding: 7px 14px;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton#BtnPeligro {
    background-color: #f38ba8;
    color: #11111b;
}
QPushButton#BtnPeligro:hover {
    background-color: #eba0ac;
}
QPushButton#BtnExito {
    background-color: #a6e3a1;
    color: #11111b;
}
QPushButton#BtnExito:hover {
    background-color: #94e2d5;
}
QTableWidget {
    background-color: #1e1e2e;
    alternate-background-color: #242436;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 8px;
    color: #cdd6f4;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    font-weight: bold;
    padding: 6px;
    border: none;
}
QProgressBar {
    background-color: #313244;
    border-radius: 6px;
    text-align: center;
    color: #11111b;
    font-weight: bold;
    height: 18px;
}
QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 6px;
}
"""


class VentanaPrincipal(QMainWindow):
    """
    Interfaz gráfica principal construida en PySide6.
    Actúa como capa de presentación: captura eventos y delega la lógica al GestorFinanciero.
    """

    def __init__(self):
        super().__init__()
        self._gestor = GestorFinanciero()
        self._generador_graficos = GeneradorGraficos()
        self._canvas_actual = None

        self.setWindowTitle("Finanzas Analyzer — Panel de Control POO")
        self.resize(1220, 760)
        self.setStyleSheet(ESTILOS_QSS)

        self._construir_ui()
        self._conectar_eventos()
        self._actualizar_toda_la_vista()

    def _construir_ui(self) -> None:
        contenedor_raiz = QWidget()
        contenedor_raiz.setObjectName("FondoPrincipal")
        self.setCentralWidget(contenedor_raiz)

        layout_principal = QVBoxLayout(contenedor_raiz)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        layout_principal.setSpacing(14)

        # 1. Fila Superior: Tarjetas KPI
        layout_kpis = QHBoxLayout()
        layout_kpis.setSpacing(14)

        self.lbl_balance = self._crear_tarjeta_kpi(layout_kpis, "BALANCE DISPONIBLE", "#89b4fa")
        self.lbl_ingresos = self._crear_tarjeta_kpi(layout_kpis, "TOTAL INGRESOS", "#a6e3a1")
        self.lbl_gastos = self._crear_tarjeta_kpi(layout_kpis, "TOTAL GASTOS", "#f38ba8")

        layout_principal.addLayout(layout_kpis)

        # 2. Cuerpo Central: Izquierda (Formularios) | Derecha (Gráficos + Tabla)
        layout_cuerpo = QHBoxLayout()
        layout_cuerpo.setSpacing(16)

        panel_izquierdo = self._construir_panel_izquierdo()
        panel_derecho = self._construir_panel_derecho()

        layout_cuerpo.addWidget(panel_izquierdo, stretch=35)
        layout_cuerpo.addWidget(panel_derecho, stretch=65)

        layout_principal.addLayout(layout_cuerpo)

    def _crear_tarjeta_kpi(self, layout_padre: QHBoxLayout, titulo: str, color_hex: str) -> QLabel:
        tarjeta = QFrame()
        tarjeta.setProperty("class", "Tarjeta")
        vbox = QVBoxLayout(tarjeta)
        vbox.setContentsMargins(16, 12, 16, 12)

        lbl_tit = QLabel(titulo)
        lbl_tit.setProperty("class", "KpiTitulo")

        lbl_val = QLabel("$0")
        lbl_val.setProperty("class", "KpiValor")
        lbl_val.setStyleSheet(f"color: {color_hex};")

        vbox.addWidget(lbl_tit)
        vbox.addWidget(lbl_val)
        layout_padre.addWidget(tarjeta)
        return lbl_val

    def _construir_panel_izquierdo(self) -> QWidget:
        contenedor = QWidget()
        vbox = QVBoxLayout(contenedor)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(14)

        # --- Tarjeta A: Nueva Transacción ---
        card_tx = QFrame()
        card_tx.setProperty("class", "Tarjeta")
        grid_tx = QGridLayout(card_tx)
        grid_tx.setContentsMargins(16, 14, 16, 14)
        grid_tx.setSpacing(10)

        tit_tx = QLabel("Registrar Movimiento")
        tit_tx.setProperty("class", "TituloSeccion")
        grid_tx.addWidget(tit_tx, 0, 0, 1, 2)

        grid_tx.addWidget(QLabel("Tipo:"), 1, 0)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Gasto", "Ingreso"])
        grid_tx.addWidget(self.cmb_tipo, 1, 1)

        grid_tx.addWidget(QLabel("Descripción:"), 2, 0)
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setPlaceholderText("Ej. Almuerzo, Pago proyecto...")
        grid_tx.addWidget(self.txt_descripcion, 2, 1)

        grid_tx.addWidget(QLabel("Monto ($):"), 3, 0)
        self.txt_monto = QLineEdit()
        self.txt_monto.setPlaceholderText("Ej. 25000")
        grid_tx.addWidget(self.txt_monto, 3, 1)

        grid_tx.addWidget(QLabel("Categoría:"), 4, 0)
        self.cmb_categoria = QComboBox()
        grid_tx.addWidget(self.cmb_categoria, 4, 1)

        self.btn_registrar = QPushButton("Agregar Movimiento")
        grid_tx.addWidget(self.btn_registrar, 5, 0, 1, 2)

        vbox.addWidget(card_tx)

        # --- Tarjeta B: Gestión de Bloques / Categorías ---
        card_cat = QFrame()
        card_cat.setProperty("class", "Tarjeta")
        vbox_cat = QVBoxLayout(card_cat)
        vbox_cat.setContentsMargins(16, 14, 16, 14)
        vbox_cat.setSpacing(10)

        tit_cat = QLabel("Bloques / Categorías de Gasto")
        tit_cat.setProperty("class", "TituloSeccion")
        vbox_cat.addWidget(tit_cat)

        fila_nueva_cat = QHBoxLayout()
        self.txt_nueva_categoria = QLineEdit()
        self.txt_nueva_categoria.setPlaceholderText("Nueva categoría (ej. Gym)...")
        self.btn_crear_cat = QPushButton("+ Crear")
        fila_nueva_cat.addWidget(self.txt_nueva_categoria)
        fila_nueva_cat.addWidget(self.btn_crear_cat)
        vbox_cat.addLayout(fila_nueva_cat)

        self.btn_eliminar_cat = QPushButton("Eliminar categoría seleccionada")
        self.btn_eliminar_cat.setObjectName("BtnPeligro")
        vbox_cat.addWidget(self.btn_eliminar_cat)

        vbox.addWidget(card_cat)

        # --- Tarjeta C: Meta de Ahorro ---
        card_meta = QFrame()
        card_meta.setProperty("class", "Tarjeta")
        vbox_meta = QVBoxLayout(card_meta)
        vbox_meta.setContentsMargins(16, 14, 16, 14)
        vbox_meta.setSpacing(10)

        tit_meta = QLabel("Meta de Ahorro")
        tit_meta.setProperty("class", "TituloSeccion")
        vbox_meta.addWidget(tit_meta)

        fila_def_meta = QHBoxLayout()
        self.txt_meta_nombre = QLineEdit()
        self.txt_meta_nombre.setPlaceholderText("Nombre meta...")
        self.txt_meta_objetivo = QLineEdit()
        self.txt_meta_objetivo.setPlaceholderText("Objetivo $")
        self.btn_definir_meta = QPushButton("Fijar")
        fila_def_meta.addWidget(self.txt_meta_nombre, stretch=2)
        fila_def_meta.addWidget(self.txt_meta_objetivo, stretch=2)
        fila_def_meta.addWidget(self.btn_definir_meta, stretch=1)
        vbox_meta.addLayout(fila_def_meta)

        self.lbl_estado_meta = QLabel("Sin meta activa definida")
        self.lbl_estado_meta.setStyleSheet("color: #a6adc8; font-size: 12px;")
        vbox_meta.addWidget(self.lbl_estado_meta)

        self.barra_meta = QProgressBar()
        self.barra_meta.setRange(0, 100)
        self.barra_meta.setValue(0)
        vbox_meta.addWidget(self.barra_meta)

        fila_abono = QHBoxLayout()
        self.txt_abono_meta = QLineEdit()
        self.txt_abono_meta.setPlaceholderText("Monto a abonar $...")
        self.btn_abonar_meta = QPushButton("Abonar")
        self.btn_abonar_meta.setObjectName("BtnExito")
        self.btn_eliminar_meta = QPushButton("X")
        self.btn_eliminar_meta.setObjectName("BtnPeligro")
        self.btn_eliminar_meta.setFixedWidth(36)
        fila_abono.addWidget(self.txt_abono_meta)
        fila_abono.addWidget(self.btn_abonar_meta)
        fila_abono.addWidget(self.btn_eliminar_meta)
        vbox_meta.addLayout(fila_abono)

        vbox.addWidget(card_meta)
        vbox.addStretch()
        return contenedor

    def _construir_panel_derecho(self) -> QWidget:
        contenedor = QWidget()
        vbox = QVBoxLayout(contenedor)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(14)

        # --- Tarjeta Superior: Gráficos de Matplotlib ---
        self.card_graficos = QFrame()
        self.card_graficos.setProperty("class", "Tarjeta")
        self.layout_graficos = QVBoxLayout(self.card_graficos)
        self.layout_graficos.setContentsMargins(10, 10, 10, 10)
        vbox.addWidget(self.card_graficos, stretch=50)

        # --- Tarjeta Inferior: Tabla de Historial ---
        card_tabla = QFrame()
        card_tabla.setProperty("class", "Tarjeta")
        vbox_tabla = QVBoxLayout(card_tabla)
        vbox_tabla.setContentsMargins(14, 12, 14, 12)
        vbox_tabla.setSpacing(8)

        cabecera_tabla = QHBoxLayout()
        tit_hist = QLabel("Historial de Transacciones")
        tit_hist.setProperty("class", "TituloSeccion")
        self.btn_eliminar_tx = QPushButton("Eliminar seleccionado")
        self.btn_eliminar_tx.setObjectName("BtnPeligro")
        cabecera_tabla.addWidget(tit_hist)
        cabecera_tabla.addStretch()
        cabecera_tabla.addWidget(self.btn_eliminar_tx)
        vbox_tabla.addLayout(cabecera_tabla)

        self.tabla_historial = QTableWidget(0, 5)
        self.tabla_historial.setHorizontalHeaderLabels(
            ["Fecha", "Tipo", "Categoría", "Descripción", "Impacto ($)"]
        )
        self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_historial.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_historial.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_historial.setAlternatingRowColors(True)
        vbox_tabla.addWidget(self.tabla_historial)

        vbox.addWidget(card_tabla, stretch=50)
        return contenedor

    # --- CONEXIÓN DE EVENTOS Y CALLBACKS ---

    def _conectar_eventos(self) -> None:
        self.cmb_tipo.currentTextChanged.connect(self._al_cambiar_tipo_transaccion)
        self.btn_registrar.clicked.connect(self._al_registrar_transaccion)
        self.txt_monto.returnPressed.connect(self._al_registrar_transaccion)

        self.btn_crear_cat.clicked.connect(self._al_crear_categoria)
        self.txt_nueva_categoria.returnPressed.connect(self._al_crear_categoria)
        self.btn_eliminar_cat.clicked.connect(self._al_eliminar_categoria)

        self.btn_definir_meta.clicked.connect(self._al_definir_meta)
        self.btn_abonar_meta.clicked.connect(self._al_abonar_meta)
        self.btn_eliminar_meta.clicked.connect(self._al_eliminar_meta)

        self.btn_eliminar_tx.clicked.connect(self._al_eliminar_transaccion)

    # --- MANEJADORES DE EVENTOS ---

    def _al_cambiar_tipo_transaccion(self, tipo: str) -> None:
        es_gasto = (tipo == "Gasto")
        self.cmb_categoria.setEnabled(es_gasto)

    def _al_registrar_transaccion(self) -> None:
        try:
            tipo = self.cmb_tipo.currentText()
            descripcion = self.txt_descripcion.text()
            texto_monto = self.txt_monto.text().strip()

            if not texto_monto:
                raise ValueError("Debes ingresar un valor numérico para el monto.")

            monto = float(texto_monto)
            fecha_hoy = datetime.date.today()

            if tipo == "Ingreso":
                movimiento = Ingreso(descripcion, monto, fecha_hoy)
            else:
                categoria = self.cmb_categoria.currentText()
                movimiento = Gasto(descripcion, monto, fecha_hoy, categoria)

            self._gestor.registrar_transaccion(movimiento)

            self.txt_descripcion.clear()
            self.txt_monto.clear()
            self.txt_descripcion.setFocus()
            self._actualizar_toda_la_vista()

        except ValueError as error:
            QMessageBox.warning(self, "Dato inválido", str(error))

    def _al_crear_categoria(self) -> None:
        try:
            nombre = self.txt_nueva_categoria.text()
            self._gestor.agregar_categoria(nombre)
            self.txt_nueva_categoria.clear()
            self._recargar_combo_categorias()
            self.cmb_categoria.setCurrentText(nombre.strip().capitalize())
        except ValueError as error:
            QMessageBox.warning(self, "Error en categoría", str(error))

    def _al_eliminar_categoria(self) -> None:
        try:
            categoria_actual = self.cmb_categoria.currentText()
            self._gestor.eliminar_categoria(categoria_actual)
            self._recargar_combo_categorias()
        except ValueError as error:
            QMessageBox.warning(self, "No se puede eliminar", str(error))

    def _al_definir_meta(self) -> None:
        try:
            nombre = self.txt_meta_nombre.text()
            texto_obj = self.txt_meta_objetivo.text().strip()
            if not texto_obj:
                raise ValueError("Ingresa un monto objetivo válido.")
            objetivo = float(texto_obj)

            self._gestor.definir_meta(nombre, objetivo)
            self.txt_meta_nombre.clear()
            self.txt_meta_objetivo.clear()
            self._actualizar_panel_meta()
        except ValueError as error:
            QMessageBox.warning(self, "Error en meta", str(error))

    def _al_abonar_meta(self) -> None:
        try:
            texto_abono = self.txt_abono_meta.text().strip()
            if not texto_abono:
                raise ValueError("Ingresa un valor para abonar.")
            cantidad = float(texto_abono)

            self._gestor.abonar_a_meta(cantidad)
            self.txt_abono_meta.clear()
            self._actualizar_toda_la_vista()
        except ValueError as error:
            QMessageBox.warning(self, "No se pudo abonar", str(error))

    def _al_eliminar_meta(self) -> None:
        try:
            self._gestor.eliminar_meta()
            self._actualizar_panel_meta()
        except ValueError as error:
            QMessageBox.warning(self, "Aviso", str(error))

    def _al_eliminar_transaccion(self) -> None:
        fila_seleccionada = self.tabla_historial.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.information(self, "Selección", "Selecciona una fila de la tabla para eliminar.")
            return

        try:
            self._gestor.eliminar_transaccion(fila_seleccionada)
            self._actualizar_toda_la_vista()
        except IndexError as error:
            QMessageBox.warning(self, "Error", str(error))

    # --- ACTUALIZACIÓN DE COMPONENTES VISUALES ---

    def _actualizar_toda_la_vista(self) -> None:
        self._recargar_combo_categorias()
        self._actualizar_kpis()
        self._actualizar_tabla()
        self._actualizar_panel_meta()
        self._actualizar_graficos()

    def _recargar_combo_categorias(self) -> None:
        seleccion_previa = self.cmb_categoria.currentText()
        self.cmb_categoria.clear()
        self.cmb_categoria.addItems(self._gestor.categorias)
        if seleccion_previa in self._gestor.categorias:
            self.cmb_categoria.setCurrentText(seleccion_previa)

    def _actualizar_kpis(self) -> None:
        balance = self._gestor.calcular_balance()
        ingresos = self._gestor.calcular_total_ingresos()
        gastos = self._gestor.calcular_total_gastos()

        self.lbl_balance.setText(f"${balance:,.0f}")
        self.lbl_ingresos.setText(f"${ingresos:,.0f}")
        self.lbl_gastos.setText(f"${gastos:,.0f}")

    def _actualizar_tabla(self) -> None:
        transacciones = self._gestor.transacciones
        self.tabla_historial.setRowCount(len(transacciones))

        for fila, tx in enumerate(transacciones):
            es_gasto = isinstance(tx, Gasto)
            tipo_str = "Gasto" if es_gasto else "Ingreso"
            categoria_str = tx.categoria if es_gasto else "General"
            impacto = tx.calcular_impacto_saldo()

            item_fecha = QTableWidgetItem(str(tx.fecha))
            item_tipo = QTableWidgetItem(tipo_str)
            item_cat = QTableWidgetItem(categoria_str)
            item_desc = QTableWidgetItem(tx.descripcion)
            item_monto = QTableWidgetItem(f"${impacto:+,.0f}")

            item_monto.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_monto.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            color_monto = QColor("#f38ba8") if es_gasto else QColor("#a6e3a1")
            item_monto.setForeground(color_monto)

            self.tabla_historial.setItem(fila, 0, item_fecha)
            self.tabla_historial.setItem(fila, 1, item_tipo)
            self.tabla_historial.setItem(fila, 2, item_cat)
            self.tabla_historial.setItem(fila, 3, item_desc)
            self.tabla_historial.setItem(fila, 4, item_monto)

    def _actualizar_panel_meta(self) -> None:
        meta = self._gestor.meta
        if meta is None:
            self.lbl_estado_meta.setText("Sin meta activa definida")
            self.barra_meta.setValue(0)
            return

        self.lbl_estado_meta.setText(
            f"{meta.nombre}: ${meta.monto_actual:,.0f} / ${meta.monto_objetivo:,.0f}"
        )
        self.barra_meta.setValue(int(meta.porcentaje_progreso))

    def _actualizar_graficos(self) -> None:
        if self._canvas_actual is not None:
            self.layout_graficos.removeWidget(self._canvas_actual)
            self._canvas_actual.deleteLater()

        figura = self._generador_graficos.generar_dashboard_financiero(
            gastos_por_categoria=self._gestor.obtener_gastos_por_categoria(),
            total_ingresos=self._gestor.calcular_total_ingresos(),
            total_gastos=self._gestor.calcular_total_gastos()
        )
        self._canvas_actual = FigureCanvas(figura)
        self.layout_graficos.addWidget(self._canvas_actual)