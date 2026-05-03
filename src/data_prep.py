# Se importan las librerías necesarias y se suprimen las advertencias
import pandas as pd
# import numpy as np


def process_data(datos_creditos: str = "data/raw/datos_creditos.csv",
                    datos_tarjetas: str = "data/raw/datos_tarjetas.csv",
                    output_dir: str = "data/processed/") -> None:
    """Lee los datos de créditos y tarjetas, realiza el procesamiento necesario

    Args:
        datos_creditos (str, optional): _description_. Defaults to "data/raw/datos_creditos.csv".
        datos_tarjetas (str, optional): _description_. Defaults to "data/raw/datos_tarjetas.csv".
        output_dir (str, optional): _description_. Defaults to "data/processed/".
    """
    df_creditos = pd.read_csv(datos_creditos, sep=";")
    df_tarjetas = pd.read_csv(datos_tarjetas, sep=";")
   
    ####################################################################
    # Se filtran los datos para eliminar registros con edades superiores a 90 años
    ####################################################################

    df_creditos_filtrado = df_creditos.copy()
    df_creditos_filtrado = df_creditos_filtrado[df_creditos_filtrado['edad'] < 90]

    ####################################################################
    # Tratamiento de valores nulos para tasa_interes y antiguedad_empleado utilizando la mediana por grupo
    ####################################################################

    df_creditos_filtrado['tasa_interes'] = df_creditos_filtrado.groupby("objetivo_credito")["tasa_interes"]\
                        .transform(lambda x: x.fillna(x.median()))
    df_creditos_filtrado['antiguedad_empleado'] = df_creditos_filtrado.groupby("edad")["antiguedad_empleado"]\
                        .transform(lambda x: x.fillna(x.median()))

    ####################################################################
    # Se integran los datos de créditos y tarjetas utilizando el id_cliente como clave
    ####################################################################

    df_integrado = pd.merge(df_creditos_filtrado, df_tarjetas, on='id_cliente', how='inner')

    ####################################################################
    # Se crean nuevos atributos a partir de los datos originales
    ####################################################################

    # Capacidad de pago del cliente
    df_integrado["capacidad_pago"] = df_integrado["importe_solicitado"] / df_integrado["ingresos"]
    # El número de operaciones mensuales del cliente
    df_integrado["operaciones_mensuales"] = df_integrado["operaciones_ult_12m"] / 12
    # Presión financiera del cliente (mensual)
    df_integrado["presion_financiera"] = (
        (df_integrado["gastos_ult_12m"]/12 + df_integrado["importe_solicitado"]/(df_integrado["duracion_credito"]*12))
        / (df_integrado["ingresos"]/12)
    )
    ####################################################################
    #   otros atributos que podrían agregarse:
    # - gasto promedio por operación realizada
    # - cantidad de operaciones mensuales con tarjeta
    # - estabilidad laboral (antiguedad_empleado / edad)
    ####################################################################

    # gasto promedio por operación realizada
    df_integrado["gasto_promedio_op"] = df_integrado["gastos_ult_12m"] / df_integrado["operaciones_ult_12m"].replace(0, 1)[cite: 1]

    # cantidad de operaciones mensuales con tarjeta (basado en el uso de la tarjeta)
    df_integrado["ops_mensuales_tarjeta"] = df_integrado["operaciones_ult_12m"] / 12[cite: 1]

    # estabilidad laboral (antiguedad_empleado / edad)
    df_integrado["estabilidad_laboral"] = df_integrado["antiguedad_empleado"] / df_integrado["edad"][cite: 1]

    ####################################################################
    # Se eliminan las columnas originales y se integran las nuevas columnas procesadas
    ####################################################################
    columnas_a_eliminar = [
        "id_cliente",
        "operaciones_ult_12m",
        "importe_solicitado",
        "duracion_credito",
        "nivel_tarjeta",
    ]

    df_integrado.drop(columnas_a_eliminar, inplace=True, axis=1)

    ####################################################################
    # Se exportan los datos procesados a un nuevo archivo CSV
    ####################################################################
    df_integrado.to_csv(output_dir + 'datos_integrados.csv', index=False)

    ##################################################################################
    # OPCIÓN EXTRA (ejemplo):  agregar la generación del reporte de metadatos a un txt 
    # o HTML con ydata-profiling.
    ##################################################################################

##################################################################################
    # OPCIÓN EXTRA: Generación automática de reporte de calidad y metadatos
    ##################################################################################
    from ydata_profiling import ProfileReport

    print("Generando reporte de perfilado de datos...")
    
    # Creamos el reporte de los datos integrados y procesados
    profile = ProfileReport(
        df_integrado, 
        title="Reporte de Metadatos - Datos Integrados",
        explorative=True
    )
    
    # Exportamos el reporte a formato HTML en la carpeta de documentación
    report_path = "docs/reporte_calidad_datos.html"
    profile.to_file(report_path)
    
    print(f"Reporte generado exitosamente en: {report_path}")

    

if __name__ == "__main__":
    process_data()  