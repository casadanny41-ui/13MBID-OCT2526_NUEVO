import pandas as pd
from pandera.pandas import DataFrameSchema, Column, Check
import pytest

@pytest.fixture
def datos_creditos():
    """ Función para cargar los datos de créditos desde un archivo CSV.
    Returns:
        pd.DataFrame: DataFrame con los datos de créditos.
    """
    df = pd.read_csv("data/raw/datos_creditos.csv", sep=";")
    return df


@pytest.fixture
def datos_tarjetas():
    """ Función para cargar los datos de tarjetas desde un archivo CSV.
    Returns:
        pd.DataFrame: DataFrame con los datos de tarjetas.
    """
    df = pd.read_csv("data/raw/datos_tarjetas.csv", sep=";")
    return df


def test_esquema_datos_creditos(datos_creditos):
    """ Prueba para validar el esquema de los datos de créditos.
    Args:
        datos_creditos (pd.DataFrame): DataFrame con los datos de créditos.
    """
    # Atributo a analizar: Exactitud (a nivel de estructura del dataset
    esquema = DataFrameSchema({
        "id_cliente": Column(float, nullable=False),
        "edad": Column(int, Check.greater_than_or_equal_to(18)),
        "importe_solicitado": Column(int, Check.greater_than(0)),
        "duracion_credito": Column(int, Check.greater_than(0)),
        "antiguedad_empleado": Column(float, Check.greater_than_or_equal_to(0), nullable=True),
        "situacion_vivienda": Column(str, nullable=False),
        "objetivo_credito": Column(str, nullable=False),
        "pct_ingreso": Column(float, Check.greater_than_or_equal_to(0)),
        "tasa_interes": Column(float, Check.greater_than_or_equal_to(0)),
        "estado_credito": Column(int, nullable=False),
        "ingresos": Column(float, Check.greater_than_or_equal_to(0)),
        "falta_pago": Column(int, nullable=False)
    })
    esquema.validate(datos_creditos)

def test_esquema_datos_tarjetas(datos_tarjetas):
    """ Prueba para validar el esquema de los datos de tarjetas.
    Args:
        datos_tarjetas (pd.DataFrame): DataFrame con los datos de tarjetas.
    """
    # Atributo a analizar: Exactitud (a nivel de estructura del dataset)
    esquema = DataFrameSchema({
        "id_cliente": Column(float, nullable=False),
        "antiguedad_c": Column(float, Check.greater_than_or_equal_to(0)),
        "estado_civil": Column(str, nullable=False),
        "estado_client": Column(str, nullable=False),
        "gastos_ult_12": Column(float, Check.greater_than_or_equal_to(0)),
        "genero": Column(str, Check.isin(["M", "F"]), nullable=False),
        "limite_credit": Column(float, Check.greater_than_or_equal_to(0)),
        "nivel_educati": Column(str, nullable=False),
        "nivel_tarjeta": Column(str, nullable=False),
        "operaciones_": Column(float, Check.greater_than_or_equal_to(0)),
        "personas_a_cargo": Column(float, Check.greater_than_or_equal_to(0))
    })
    esquema.validate(datos_tarjetas)


def test_basicos_creditos(datos_creditos):
    """ Prueba para validar aspectos básicos de los datos de créditos.
    Args:
        datos_creditos (pd.DataFrame): DataFrame con los datos de créditos.
    """
    # Atributo a analizar: Exactitud (a nivel de estructura del dataset)
    df = datos_creditos
    # Verificar que el dataset no sea nulo completamente
    assert not df.empty, "El dataset de créditos está vacío."
    # Verificar la cantidad de columnas para completar estructura del dataset
    assert df.shape[1] == 12, f"El dataset de créditos debería tener 12 columnas, pero tiene {df.shape[1]}."

    # Verificar que no haya valores nulos en general
    # Atributo a analizar: Completitud (a nivel general del dataset)
    assert df.isnull().sum().sum() == 0, "Existen valores nulos en el dataset de créditos."


def test_basicos_tarjetas(datos_tarjetas):
    """ Prueba para validar aspectos básicos de los datos de tarjetas.
    Args:
        datos_tarjetas (pd.DataFrame): DataFrame con los datos de tarjetas.
    """
    # Atributo a analizar: Exactitud (a nivel de estructura del dataset)
    df = datos_tarjetas
    # Verificar que el dataset no sea nulo completamente
    assert not df.empty, "El dataset de tarjetas está vacío."
    # Verificar la cantidad de columnas para completar estructura del dataset
    assert df.shape[1] == 11, f"El dataset de tarjetas debería tener 11 columnas, pero tiene {df.shape[1]}."

    # Verificar que no haya valores nulos en general
    # Atributo a analizar: Completitud (a nivel general del dataset)
    assert df.isnull().sum().sum() == 0, "Existen valores nulos en el dataset de tarjetas."


def test_integridad_referencial(datos_creditos, datos_tarjetas):
    """ Prueba para validar la integridad referencial entre los datasets de créditos y tarjetas.
    Args:
        datos_creditos (pd.DataFrame): DataFrame con los datos de créditos.
        datos_tarjetas (pd.DataFrame): DataFrame con los datos de tarjetas.
    """
    # Atributo a analizar: Consistencia (a nivel de relación entre datasets)

    df_ids = datos_creditos[["id_cliente"]].merge(
        datos_tarjetas[["id_cliente"]], 
        on="id_cliente", 
        how="outer",
        indicator=True
    )
    integridad_referencial = DataFrameSchema({
        "_merge": Column(
            str, 
            Check.isin(["both"]),
            nullable=False
        )
    })
    integridad_referencial.validate(df_ids)

####################################################################
# TODO: agregar al menos una función de test con una (1) 
# o más validaciones más allá de la estructura del dataset de tarjetas.
# Por ejemplo: unicidad de IDS en ambos datasets
####################################################################

def test_esquema_datos_tarjetas(datos_tarjetas):
    """ Prueba para validar el esquema de los datos de tarjetas. """
    # Atributo a analizar: Exactitud (a nivel de estructura del dataset)
    esquema = DataFrameSchema({
        "id_cliente": Column(float, nullable=False),
        "antiguedad_cliente": Column(float, Check.greater_than_or_equal_to(0)),
        "estado_civil": Column(str, nullable=False),
        "estado_client": Column(str, nullable=False), # Nota: aparece como 'estado_client' en la imagen
        "gastos_ult_12": Column(float, Check.greater_than_or_equal_to(0)),
        "genero": Column(str, Check.isin(["M", "F"]), nullable=False),
        "limite_credit": Column(float, Check.greater_than_or_equal_to(0)),
        "nivel_educati": Column(str, nullable=False),
        "nivel_tarjeta": Column(str, nullable=False),
        "operaciones_": Column(float, Check.greater_than_or_equal_to(0)),
        "personas_a_cargo": Column(float, Check.greater_than_or_equal_to(0))
    })
    esquema.validate(datos_tarjetas)

def test_unicidad_y_consistencia_negocio(datos_creditos, datos_tarjetas):
    """
    Validaciones adicionales: Unicidad de IDs y consistencia de datos.
    """
    # 1. Unicidad: Verificar que cada ID de cliente sea único en ambos archivos
    assert datos_creditos["id_cliente"].is_unique, "Error: Hay IDs duplicados en el archivo de créditos."
    assert datos_tarjetas["id_cliente"].is_unique, "Error: Hay IDs duplicados en el archivo de tarjetas."

    # 2. Consistencia: Verificar que la columna 'falta_pago' solo tenga valores esperados
    # Según tu imagen de créditos, los valores son 'Y' o 'N'
    valores_validos_pago = ["Y", "N"]
    assert datos_creditos["falta_pago"].isin(valores_validos_pago).all(), "Error: La columna 'falta_pago' contiene valores distintos a Y/N."

    # 3. Consistencia de Edad: Verificar que no haya clientes con edades irreales
    # (Ejemplo: mayores de 18 pero menores de 100 años)
    assert datos_creditos["edad"].between(18, 100).all(), "Error: Se detectaron edades fuera del rango permitido (18-100)."