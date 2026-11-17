import datetime
from modelos.transaccion import Transaccion, Ingreso, Gasto
from modelos.meta_ahorro import MetaAhorro


class GestorFinanciero:
    """
    Servicio encargado de coordinar las transacciones, categorías y metas de ahorro.
    Aplica agregación sobre las entidades del dominio y polimorfismo para los cálculos.
    """

    def __init__(self):
        self._transacciones: list[Transaccion] = []
        self._categorias: list[str] = [
            "Alimentación",
            "Transporte",
            "Entretenimiento",
            "Servicios",
            "Educación",
            "Ahorro"
        ]
        self._meta: MetaAhorro | None = None

    # --- PROPIEDADES DE LECTURA (ENCAPSULAMIENTO) ---

    @property
    def transacciones(self) -> list[Transaccion]:
        return list(self._transacciones)

    @property
    def categorias(self) -> list[str]:
        return list(self._categorias)

    @property
    def meta(self) -> MetaAhorro | None:
        return self._meta

    # --- GESTIÓN DE CATEGORÍAS (CREAR Y ELIMINAR) ---

    def agregar_categoria(self, nombre_categoria: str) -> None:
        if not nombre_categoria or not nombre_categoria.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")

        categoria_limpia = nombre_categoria.strip().capitalize()

        if categoria_limpia in self._categorias:
            raise ValueError(f"La categoría '{categoria_limpia}' ya existe.")

        self._categorias.append(categoria_limpia)

    def eliminar_categoria(self, nombre_categoria: str) -> None:
        if nombre_categoria == "Ahorro":
            raise ValueError("La categoría 'Ahorro' es reservada del sistema y no puede eliminarse.")

        if nombre_categoria not in self._categorias:
            raise ValueError(f"La categoría '{nombre_categoria}' no existe.")

        # Evitar eliminar categorías que ya están asociadas a un gasto en el historial
        for t in self._transacciones:
            if isinstance(t, Gasto) and t.categoria == nombre_categoria:
                raise ValueError(
                    f"No se puede eliminar '{nombre_categoria}' porque tiene gastos asociados en el historial."
                )

        self._categorias.remove(nombre_categoria)

    # --- GESTIÓN DE TRANSACCIONES (CREAR Y ELIMINAR) ---

    def registrar_transaccion(self, transaccion: Transaccion) -> None:
        if not isinstance(transaccion, Transaccion):
            raise TypeError("El objeto debe ser una instancia válida de Transaccion.")

        if isinstance(transaccion, Gasto) and transaccion.categoria not in self._categorias:
            raise ValueError(f"La categoría '{transaccion.categoria}' no está registrada.")

        self._transacciones.append(transaccion)

    def eliminar_transaccion(self, indice: int) -> None:
        """Elimina una transacción del historial según su posición (útil para selección en QTableWidget)."""
        if indice < 0 or indice >= len(self._transacciones):
            raise IndexError("El índice de la transacción seleccionada no es válido.")

        self._transacciones.pop(indice)

    def limpiar_historial(self) -> None:
        """Reinicia todos los movimientos de la sesión."""
        self._transacciones.clear()

    # --- CÁLCULOS FINANCIEROS Y KPIs ---

    def calcular_balance(self) -> float:
        """Demostración de Polimorfismo: cada subclase calcula su propio impacto."""
        total = 0.0
        for t in self._transacciones:
            total += t.calcular_impacto_saldo()
        return total

    def calcular_total_ingresos(self) -> float:
        total = 0.0
        for t in self._transacciones:
            if isinstance(t, Ingreso):
                total += t.monto
        return total

    def calcular_total_gastos(self) -> float:
        total = 0.0
        for t in self._transacciones:
            if isinstance(t, Gasto):
                total += t.monto
        return total

    def obtener_gastos_por_categoria(self) -> dict[str, float]:
        """Agrupa los gastos por categoría para alimentar los gráficos de Matplotlib."""
        resumen: dict[str, float] = {}
        for t in self._transacciones:
            if isinstance(t, Gasto):
                resumen[t.categoria] = resumen.get(t.categoria, 0.0) + t.monto
        return resumen

    # --- GESTIÓN DE METAS DE AHORRO (CREAR, ABONAR Y ELIMINAR) ---

    def definir_meta(self, nombre: str, monto_objetivo: float) -> None:
        self._meta = MetaAhorro(nombre, monto_objetivo)

    def abonar_a_meta(self, cantidad: float) -> None:
        if self._meta is None:
            raise ValueError("Primero debes crear una meta de ahorro.")

        if cantidad <= 0:
            raise ValueError("El monto del abono debe ser mayor a cero.")

        if cantidad > self.calcular_balance():
            raise ValueError("Saldo disponible insuficiente para realizar este abono.")

        self._meta.abonar(cantidad)

        # Descuenta el ahorro del saldo libre registrando un gasto automático
        movimiento_ahorro = Gasto(
            descripcion=f"Abono a meta: {self._meta.nombre}",
            monto=cantidad,
            fecha=datetime.date.today(),
            categoria="Ahorro"
        )
        self.registrar_transaccion(movimiento_ahorro)

    def eliminar_meta(self) -> None:
        if self._meta is None:
            raise ValueError("No hay ninguna meta activa para eliminar.")
        self._meta = None
