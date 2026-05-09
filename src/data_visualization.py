# Importación de librerías
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

def visualize_data(datos_creditos: str = "data/raw/datos_creditos.csv",
                   datos_tarjetas: str = "data/raw/datos_tarjetas.csv",
                   output_dir: str = "docs/figures/") -> None:
    """
    Generar visualizaciones de los datos del escenario y guardarlas en el directorio especificado.
    """
    # 1. MECANISMO DE SEGURIDAD: Crear el directorio de salida si no existe
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Lectura de los datos
    try:
        df_creditos = pd.read_csv(datos_creditos, sep=";")
        df_tarjetas = pd.read_csv(datos_tarjetas, sep=";")
    except FileNotFoundError as e:
        print(f"Error: No se encontraron los archivos de datos. {e}")
        return

    sns.set_style("whitegrid")

    # --- Gráficos Originales ---
    
    # Distribución de la variable 'target'
    plt.figure(figsize=(10, 6))
    sns.countplot(x='falta_pago', data=df_creditos)
    plt.title('Distribución de la variable target')
    plt.savefig(output_path / 'target_distribution.png')
    plt.close()

    # Matriz de correlaciones - Créditos
    num_df_c = df_creditos.select_dtypes(include=['float64', 'int64'])
    plt.figure(figsize=(10, 8))
    sns.heatmap(num_df_c.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Matriz de correlaciones - Créditos')
    plt.savefig(output_path / 'correlation_heatmap_creditos.png')
    plt.close()

    # Matriz de correlaciones - Tarjetas
    num_df_t = df_tarjetas.select_dtypes(include=['float64', 'int64'])
    plt.figure(figsize=(10, 8))
    sns.heatmap(num_df_t.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Matriz de correlaciones - Tarjetas')
    plt.savefig(output_path / 'correlation_heatmap_tarjetas.png')
    plt.close()

    # --- TODO COMPLETADO: Gráficos Adicionales ---

    # 1. Boxplot: Ingresos por Situación de Vivienda
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='situacion_vivienda', y='ingresos', hue='situacion_vivienda', 
                data=df_creditos, palette="Set2", legend=False)
    plt.title('Distribución de Ingresos por Situación de Vivienda')
    plt.savefig(output_path / 'ingresos_vs_vivienda_boxplot.png')
    plt.close()

    # 2. Scatter Plot: Edad vs Importe (CORREGIDO: estado_credito)
    # Se usa 'estado_credito' para coincidir con el dataset real
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='edad', y='importe_solicitado', hue='estado_credito', 
                    data=df_creditos, alpha=0.6, palette="viridis")
    plt.title('Relación Edad vs Importe Solicitado')
    plt.savefig(output_path / 'edad_vs_importe_scatter.png')
    plt.close()

    print(f"Éxito: Se han generado los 5 archivos en {output_dir}")

if __name__ == "__main__":
    visualize_data()