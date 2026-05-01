import pandas as pd
from pathlib import Path
import pytest
import warnings

warnings.filterwarnings(
    "ignore",
    message=r".*`Number` field should not be instantiated.*",
)

import great_expectations as ge


pytestmark = [
    pytest.mark.filterwarnings("ignore:.*Number.*should not be instantiated.*"),
    pytest.mark.filterwarnings("ignore:.*result_format.*Validator-level.*"),
    pytest.mark.filterwarnings("ignore:.*result_format.*Expectation-level.*"),
]


# Paths
PROJECT_DIR = Path(".").resolve()
DATA_DIR = PROJECT_DIR / "data"


def test_great_expectations():
    """ Prueba para validar la calidad de los datos utilizando Great Expectations.
    """
    # Cargar los datos de créditos y tarjetas
    df_creditos = pd.read_csv(DATA_DIR / "raw/datos_creditos.csv", sep=";")
    # df_tarjetas = pd.read_csv(DATA_DIR / "raw/datos_tarjetas.csv", sep=";")

    results = {
        "success": True,
        "expectations": [],
        "statistics": {"success_count": 0, "total_count": 0}
    }

    def add_expectation(expectation_name, condition, message=""):
        results["statistics"]["total_count"] += 1
        if condition:
            results["statistics"]["success_count"] += 1
            results["expectations"].append({
                "expectation": expectation_name,
                "success": True
            })
        else:
            results["success"] = False
            results["expectations"].append({
                "expectation": expectation_name,
                "success": False,
                "message": message
            })

    
    # Atributo a analizar: Exactitud (rangos de valores en datos)
    # Validación 1: Rango de edad (18-100 años)
    edad_valida = df_creditos["edad"].between(18, 100).all()
    mensaje_edad = ""
    if not edad_valida:
        edades_fuera = df_creditos[(df_creditos["edad"] < 18) | (df_creditos["edad"] > 100)]["edad"].unique()
        mensaje_edad = f"Edades fuera de rango encontradas: {sorted(edades_fuera)}"
    add_expectation(
        "rango_edad",
        edad_valida,
        f"La edad debe estar entre 18 y 100 años. {mensaje_edad}"
    )
   
    # Validación 2: Rango de valores para situación de vivienda (ALQUILER, PROPIA, OTROS, HIPOTECA)
    vivienda_valida = df_creditos["situacion_vivienda"].isin(["ALQUILER", "PROPIA", "OTROS", "HIPOTECA"]).all()
    mensaje_vivienda = ""
    if not vivienda_valida:
        viviendas_fuera = df_creditos[~df_creditos["situacion_vivienda"].isin(["ALQUILER", "PROPIA", "OTROS", "HIPOTECA"])]["situacion_vivienda"].unique()
        mensaje_vivienda = f"Situaciones de vivienda no válidas encontradas: {sorted(viviendas_fuera)}" 
    add_expectation(
        "situacion_vivienda",
        vivienda_valida,
        f"La situación de vivienda no se encuentra en el rango válido. {mensaje_vivienda}"
    )

    # Resumen y validación final
    print("\n" + "="*70)
    print("RESUMEN DE VALIDACIONES")
    print("="*70)
    for exp in results["expectations"]:
        status = "✓ PASS" if exp["success"] else "✗ FAIL"
        print(f"{status}: {exp['expectation']}")
        if not exp["success"] and "message" in exp:
            print(f"       Detalle: {exp['message']}")
    print(f"\nTotal: {results['statistics']['success_count']}/{results['statistics']['total_count']} validaciones pasaron")
    print("="*70 + "\n")

    # El test falla si alguna validación no pasó
    assert results["success"], f"Se encontraron {results['statistics']['total_count'] - results['statistics']['success_count']} validaciones fallidas"



    #############################################################################
    # al menos dos (2) validaciones más para el dataset de tarjetas.
    # Por ejemplo: rangos de valores para el atrbuto de límite de crédito o el 
    #               estado_civil o nivel de estudios.
    ##############################################################################

      
    # 0. Cargar los datos de tarjetas (asegúrate de que esta línea esté activa)
    df_tarjetas = pd.read_csv(DATA_DIR / "raw/datos_tarjetas.csv", sep=";")

    # --- VALIDACIÓN 3: Rango de niveles de tarjeta ---
    # Según image_efc645.png, los valores son 'Blue', 'Gold', etc.
    niveles_validos = ["Blue", "Silver", "Gold", "Platinum"]
    nivel_valido = df_tarjetas["nivel_tarjeta"].isin(niveles_validos).all()
    mensaje_nivel = ""
    if not nivel_valido:
        niveles_fuera = df_tarjetas[~df_tarjetas["nivel_tarjeta"].isin(niveles_validos)]["nivel_tarjeta"].unique()
        mensaje_nivel = f"Niveles de tarjeta no reconocidos: {sorted(niveles_fuera)}"
    
    add_expectation(
        "nivel_tarjeta_rango",
        nivel_valido,
        f"El nivel de la tarjeta no pertenece a las categorías permitidas. {mensaje_nivel}"
    )

    # --- VALIDACIÓN 4: Límite de crédito positivo ---
    # Usamos el nombre 'limite_credit' tal como se ve en image_efc645.png
    limite_positivo = (df_tarjetas["limite_credit"] > 0).all()
    mensaje_limite = ""
    if not limite_positivo:
        conteo_negativos = df_tarjetas[df_tarjetas["limite_credit"] <= 0].shape[0]
        mensaje_limite = f"Se encontraron {conteo_negativos} registros con límite menor o igual a cero."

    add_expectation(
        "limite_credito_positivo",
        limite_positivo,
        f"El límite de crédito debe ser mayor a 0. {mensaje_limite}"
    )