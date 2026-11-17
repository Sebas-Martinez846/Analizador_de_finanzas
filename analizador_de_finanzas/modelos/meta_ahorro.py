class MetaAhorro:
    def __init__(self, nombre, monto_objetivo):
        self.nombre = nombre
        self.monto_objetivo = monto_objetivo
        self._monto_actual = 0.0

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nombre):
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacio")
        else:
            self._nombre = nombre

    @property
    def monto_objetivo(self):
        return self._monto_objetivo

    @monto_objetivo.setter
    def monto_objetivo(self, monto_objetivo):
        if monto_objetivo <= 0:
            raise ValueError("El monto debe ser positivo")
        else:
            self._monto_objetivo = monto_objetivo

    @property
    def monto_actual(self):
        return self._monto_actual

    def abonar(self, abono):
        if abono > 0 :
            self._monto_actual += abono
        else:
            raise ValueError("El monto debe ser positivo")

    @property
    def porcentaje_progreso(self):
        resultado = (self.monto_actual/self.monto_objetivo)*100
        return min(100.0, resultado)




