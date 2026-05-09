from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import joblib
from typing import Dict

app = FastAPI(
    title="Modelo de Predicción de Mora en Créditos",
    description="Una API para predecir la probabilidad de mora en créditos utilizando un modelo de machine learning entrenado con datos históricos.",
    version="1.0.0"
)

#+++++++++++++++++++++++++
class PredictionRequest(BaseModel):
    # ---------------------------------------------------------------------------------
    # TODO: Modelo adaptado a la fase de preparación de datos (Proyecto 13MBID)
    # ---------------------------------------------------------------------------------
    edad: int = Field(..., ge=18, le=100, description="Edad del cliente en años")
    antiguedad_empleado: float = Field(..., ge=0, description="Años de experiencia laboral")
    situacion_vivienda: str = Field(..., pattern="^(ALQUILER|PROPIA|HIPOTECADA|OTRA)$", description="Estado de propiedad de la vivienda")
    ingresos: int = Field(..., gt=0, description="Ingresos anuales totales")
    objetivo_credito: str = Field(..., description="Motivo del préstamo (e.g., EDUCACION, PERSONAL, VIVIENDA)")
    pct_income: float = Field(..., alias="pct_ingreso", ge=0, le=1.0, description="Proporción del ingreso destinada al crédito")
    tasa_interes: float = Field(..., ge=0, description="Tasa de interés aplicada")
    estado_credito: int = Field(..., description="Estado actual (0 para pagado, 1 para mora)")
    antiguedad_cliente: float = Field(..., description="Meses de relación con la entidad")
    estado_civil: str = Field(..., description="Estado civil del solicitante")
    estado_cliente: str = Field(..., description="Estado operativo del cliente (ACTIVO/INACTIVO)")
    gastos_ult_12m: float = Field(..., description="Monto total de gastos en el último año")
    genero: str = Field(..., pattern="^(M|F)$", description="Género del cliente")
    limite_credito_tc: float = Field(..., description="Límite asignado en tarjeta de crédito")
    nivel_educativo: str = Field(..., description="Último nivel de estudios alcanzado")
    personas_a_cargo: float = Field(..., ge=0, description="Número de dependientes económicos")
    capacidad_pago: float = Field(..., description="Indicador de solvencia calculado")
    operaciones_mensuales: float = Field(..., description="Promedio de transacciones al mes")
    presion_financiera: float = Field(..., description="Relación deuda/ingreso calculada")

    class Config:
        populate_by_name = True # Permite usar el alias 'pct_ingreso'
        json_schema_extra = {
            "example": {
                "edad": 30,
                "antiguedad_empleado": 5.0,
                "situacion_vivienda": "ALQUILER",
                "ingresos": 50000,
                "objetivo_credito": "PERSONAL",
                "pct_ingreso": 0.12,
                "tasa_interes": 14.5,
                "estado_credito": 0,
                "antiguedad_cliente": 24.0,
                "estado_civil": "SOLTERO",
                "estado_cliente": "ACTIVO",
                "gastos_ult_12m": 12000.0,
                "genero": "M",
                "limite_credito_tc": 5000.0,
                "nivel_educativo": "UNIVERSITARIO_COMPLETO",
                "personas_a_cargo": 0.0,
                "capacidad_pago": 0.45,
                "operaciones_mensuales": 15.0,
                "presion_financiera": 0.24
            }
        }
#+++++++++++++++++++++++++
class PredictionResponse(BaseModel):
    prediction: str
    probability: Dict[str, float]
    class_labels: Dict[str, str]
    model_info: Dict[str, str]

# Cargar el modelo entrenado
# ESTO VA DENTRO DEL ARCHIVO api.py, NO EN LA TERMINAL
MODEL_PATH = "models/prod_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print("Modelo cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")

@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a la API de Predicción de Mora en Créditos",
        "endpoints": {
            "/predict": "POST - Realiza una predicción de mora en créditos",
            "/docs": "GET - Documentación interactiva de la API",
            "/health": "GET - Verifica el estado de la API"
        }
    }

@app.get("/health")
def health_check():
    if model is not None:
        return {"status": "ok", "message": "La API está funcionando correctamente."}
    else:
        return {"status": "error", "message": "El modelo no está cargado. Verifica el estado del modelo."}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="El modelo no está disponible. Intenta nuevamente más tarde.")
    
    try:
        # Convertir la solicitud a un DataFrame
        input_data = pd.DataFrame([request.dict()])
        
        # Realizar la predicción
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0]
        
        # Mapear las etiquetas de clase a descripciones legibles
        class_labels = model.named_steps['model'].classes_
        probability_dict = {
            # El dict de probabilidades se construye dinámicamente para que se adapte a cualquier número de clases
            # CAMBIO: no estaba hecha la conversión a str y ese era el error en SP6
            str(class_labels[i]): float(probability[i]) for i in range(len(class_labels))
        }
        model_info = {
            "model_version": "1.0.0",
            "model_type": type(model.named_steps["model"]).__name__, # Para que el nombre se complete automáticamente según el modelo cargado
        }
        return PredictionResponse(
            prediction=str(prediction),
            probability=probability_dict,
            class_labels={
                "0": "No entra en mora (N)",
                "1": "Entra en mora (Y)"
            },
            model_info=model_info
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al realizar la predicción: {e}")