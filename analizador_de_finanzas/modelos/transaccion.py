import datetime
from abc import ABC, abstractmethod

class Transaccion(ABC):
    def __init__(self, descripcion, monto, fecha):
        self.descripcion = descripcion
        self.monto = monto
        self._fecha = datetime.date.today()

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, descripcion):
        if not descripcion or not descripcion.strip():
            raise ValueError("El descripcion debe contener información.")
        else:
            self._descripcion = descripcion

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, monto):
        if monto <= 0:
            raise ValueError("El monto debería ser positivo.")
        else:
            self._monto = monto

    @property
    def fecha(self):
        return self._fecha

    @abstractmethod
    def calcular_impacto_saldo(self):
        pass

class Ingreso(Transaccion):
    def __init__(self, descripcion, monto, fecha):
        super().__init__(descripcion,monto,fecha)

    def calcular_impacto_saldo(self):
        return self.monto

class Gasto(Transaccion):
    def __init__(self, descripcion, monto, fecha, categoria):
        super().__init__(descripcion, monto, fecha)
        self._categoria = categoria

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, categoria):
        if not categoria or not categoria.strip():
            raise ValueError("La categoria no puede estar vacia")
        else:
            self._categoria = categoria

    def calcular_impacto_saldo(self):
        return -self.monto





