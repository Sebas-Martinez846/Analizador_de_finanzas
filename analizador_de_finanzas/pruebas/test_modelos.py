import datetime
import pytest
from modelos.transaccion import Transaccion, Ingreso, Gasto
from modelos.meta_ahorro import MetaAhorro
from servicios.gestor_financiero import GestorFinanciero


# --- PRUEBAS DE ABSTRACCIÓN, HERENCIA Y ENCAPSULAMIENTO ---

def test_no_se_puede_instanciar_clase_abstracta():
    """Verifica que Transaccion sea realmente abstracta."""
    with pytest.raises(TypeError):
        Transaccion("Prueba", 1000, datetime.date.today())


def test_encapsulamiento_valida_monto_invalido():
    """Verifica que no se permitan montos negativos o en cero."""
    with pytest.raises(ValueError, match="positivo"):
        Ingreso("Pago inválido", -5000, datetime.date.today())

    with pytest.raises(ValueError, match="positivo"):
        Gasto("Café", 0, datetime.date.today(), "Alimentación")


def test_encapsulamiento_valida_descripcion_vacia():
    """Verifica que los setters rechacen cadenas vacías o solo espacios."""
    with pytest.raises(ValueError):
        Ingreso("   ", 20000, datetime.date.today())


# --- PRUEBAS DE POLIMORFISMO ---

def test_polimorfismo_calcular_impacto_saldo():
    """Verifica que Ingreso y Gasto respondan distinto al mismo método."""
    ingreso = Ingreso("Salario", 1000000, datetime.date.today())
    gasto = Gasto("Mercado", 250000, datetime.date.today(), "Alimentación")

    assert ingreso.calcular_impacto_saldo() == 1000000
    assert gasto.calcular_impacto_saldo() == -250000


# --- PRUEBAS DE REGLAS DE NEGOCIO EN GESTOR FINANCIERO ---

def test_calculo_balance_y_agrupacion_categorias():
    """Verifica el balance polimórfico y el diccionario de gastos para Matplotlib."""
    gestor = GestorFinanciero()
    hoy = datetime.date.today()

    gestor.registrar_transaccion(Ingreso("Freelance", 500000, hoy))
    gestor.registrar_transaccion(Gasto("Almuerzo", 25000, hoy, "Alimentación"))
    gestor.registrar_transaccion(Gasto("Cena", 35000, hoy, "Alimentación"))
    gestor.registrar_transaccion(Gasto("Bus", 10000, hoy, "Transporte"))

    assert gestor.calcular_total_ingresos() == 500000
    assert gestor.calcular_total_gastos() == 70000
    assert gestor.calcular_balance() == 430000

    resumen = gestor.obtener_gastos_por_categoria()
    assert resumen == {"Alimentación": 60000, "Transporte": 10000}


def test_gestion_categorias_personalizadas():
    """Verifica creación, bloqueo de duplicados y protección al eliminar."""
    gestor = GestorFinanciero()
    gestor.agregar_categoria("  gimnasio ")
    assert "Gimnasio" in gestor.categorias

    # Bloqueo de duplicados
    with pytest.raises(ValueError, match="ya existe"):
        gestor.agregar_categoria("Gimnasio")

    # Bloqueo de eliminación si hay gastos asociados
    gestor.registrar_transaccion(Gasto("Mensualidad", 80000, datetime.date.today(), "Gimnasio"))
    with pytest.raises(ValueError, match="gastos asociados"):
        gestor.eliminar_categoria("Gimnasio")


def test_meta_ahorro_abonos_y_saldo_insuficiente():
    """Verifica el flujo completo de metas de ahorro y su impacto en el saldo."""
    gestor = GestorFinanciero()
    gestor.definir_meta("PC Gamer", 2000000)
    gestor.registrar_transaccion(Ingreso("Bono", 500000, datetime.date.today()))

    # Intentar abonar más del saldo disponible debe fallar
    with pytest.raises(ValueError, match="Saldo disponible insuficiente"):
        gestor.abonar_a_meta(600000)

    # Abono válido descuenta del balance y aumenta progreso de la meta
    gestor.abonar_a_meta(400000)
    assert gestor.meta.monto_actual == 400000
    assert gestor.meta.porcentaje_progreso == 20.0
    assert gestor.calcular_balance() == 100000