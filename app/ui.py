import streamlit as st
import requests

st.set_page_config(
    page_title="Predicción de Mora en Créditos", 
    page_icon=":credit_card:", 
    layout="wide"
)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Instrucciones")
    st.write("""
    1. Ingrese los datos del cliente en el formulario.
    2. Haga clic en el botón "Predecir" para obtener la probabilidad de mora.
    3. Revise los resultados y la información del modelo.
    """)
    st.divider()
    st.header("Configuración de la API")
    api_url = st.text_input(
        "URL de la API",
        value="https://one3mbid-oct2526-nuevo.onrender.com", # URL de tu servicio en Render
        help="Ingrese la URL donde está alojada la API de predicción."
    )
    st.divider()
    if st.button("Probar Conexión a la API"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("Conexión exitosa a la API.")
            else:
                st.error(f"Error al conectar: {response.status_code}")
        except Exception as e:
            st.error(f"Error al conectar: {e}")

# --- CUERPO PRINCIPAL ---
st.title("Predicción de Mora en Créditos")
st.write("Ingrese los datos del cliente para evaluar el riesgo de impago utilizando el modelo de Machine Learning.")

with st.form("prediction_form"):
    st.subheader("Datos Personales y Demográficos")
    col1, col2, col3 = st.columns(3)

    with col1:
        edad = st.number_input("Edad", min_value=18, max_value=100, value=30)
        genero = st.selectbox("Género", options=["M", "F"])
        estado_civil = st.selectbox("Estado Civil", options=["CASADO", "SOLTERO", "DIVORCIADO", "VIUDO", "OTRO"])

    with col2:
        nivel_educativo = st.selectbox(
            "Nivel Educativo", 
            options=["PRIMARIO", "SECUNDARIO", "TERCIARIO", "UNIVERSITARIO_INCOMPLETO", "UNIVERSITARIO_COMPLETO", "POSGRADO"])
        situacion_vivienda = st.selectbox(
            "Situación de Vivienda", 
            options=["ALQUILER", "PROPIETARIO", "HIPOTECADA", "OTRA"])

    with col3:
        personas_a_cargo = st.number_input("Personas a Cargo", min_value=0, max_value=20, value=0)
        estado_cliente = st.selectbox("Estado del Cliente", options=["ACTIVO", "INACTIVO"])
        estado_credito = st.number_input("Estado del crédito (Numérico)", min_value=0, value=1, step=1)
    
    st.divider()
    st.subheader("Información Financiera y Crédito")
    col4, col5, col6 = st.columns(3)

    with col4:
        ingresos = st.number_input("Ingresos Mensuales", min_value=0, value=50000)
        antiguedad_empleado = st.number_input("Antigüedad Laboral (años)", min_value=0, max_value=50, value=1)
    
    with col5:
        objetivo_credito = st.selectbox(
            "Objetivo del Crédito", 
            options=["PERSONAL", "VIVIENDA", "VEHICULO", "NEGOCIOS", "EDUCACION", "OTRO"])
        tasa_interes = st.number_input("Tasa de interés (%)", min_value=0.0, value=15.0, step=0.01)
        pct_ingreso = st.number_input("Relación Cuota/Ingreso (0.0 a 1.0)", min_value=0.0, max_value=1.0, value=0.1)
    
    with col6:
        antiguedad_cliente = st.number_input("Antigüedad del cliente (meses)", min_value=0, value=36)
        limite_credito_tc = st.number_input("Límite de Tarjeta de Crédito", min_value=0.0, value=10000.0)

    st.divider()
    st.subheader("Actividad de Gastos")
    col7, col8 = st.columns(2)

    with col7:
        gastos_ult_12m = st.number_input("Total Gastos Último Año", min_value=0.0, value=1200.0)
    
    with col8:
        operaciones_mensuales = st.number_input("Promedio Operaciones Mensuales", min_value=1.0, value=5.0)

    st.divider()
    submit_button = st.form_submit_button("Predecir", use_container_width=True, type="primary")

# --- LÓGICA DE PREDICCIÓN ---
if submit_button:
    # 1. Ingeniería de Características (Calculamos las columnas que pide el modelo)
    # Estas variables corrigen el error 503 detectado anteriormente
    presion_financiera_calc = float(gastos_ult_12m / ingresos) if ingresos > 0 else 0.0
    capacidad_pago_calc = float((ingresos - (gastos_ult_12m / 12)) / (personas_a_cargo + 1))
    gasto_promedio_op_calc = float(gastos_ult_12m / (operaciones_mensuales * 12)) if operaciones_mensuales > 0 else 0.0
    estabilidad_laboral_calc = float(antiguedad_empleado / edad) if edad > 0 else 0.0

    # 2. Construcción del JSON (Payload) con nombres exactos requeridos por la API
    input_data = {
        "edad": int(edad),
        "antiguedad_empleado": int(antiguedad_empleado),
        "situacion_vivienda": situacion_vivienda,
        "ingresos": float(ingresos),
        "objetivo_credito": objetivo_credito,
        "pct_ingreso": float(pct_ingreso),
        "tasa_interes": float(tasa_interes),
        "estado_credito": int(estado_credito),
        "antiguedad_cliente": float(antiguedad_cliente),
        "estado_civil": estado_civil,
        "estado_cliente": estado_cliente,
        "gastos_ult_12m": float(gastos_ult_12m),
        "genero": genero,
        "limite_credito_tc": float(limite_credito_tc),
        "nivel_educativo": nivel_educativo,
        "personas_a_cargo": float(personas_a_cargo),
        "operaciones_mensuales": float(operaciones_mensuales),
        # Columnas críticas corregidas:
        "capacidad_pago": capacidad_pago_calc,
        "presion_financiera": presion_financiera_calc,
        "ops_mensuales_tarjeta": float(operaciones_mensuales), # Nombre alternativo que pedía el error
        "gasto_promedio_op": gasto_promedio_op_calc,
        "estabilidad_laboral": estabilidad_laboral_calc
    }

    try:
        with st.spinner("Conectando con la API en Render..."):
            resp = requests.post(f"{api_url}/predict", json=input_data, timeout=60)
            resp.raise_for_status()
            result = resp.json()

        st.success("¡Predicción realizada!")
        
        # --- MOSTRAR RESULTADOS ---
        col_res1, col_res2 = st.columns(2)
        
        prediction = result.get("prediction")
        probabilidades = result.get("probability", {})
        
        with col_res1:
            st.metric("Resultado", "MORA" if str(prediction) == "1" else "SIN MORA")
            if str(prediction) == "1":
                st.error("⚠️ El cliente tiene alto riesgo de incumplimiento.")
            else:
                st.success("✅ El cliente es apto para el crédito.")

        with col_res2:
            # Intentamos obtener la probabilidad de la clase 1 (Mora)
            p_mora = probabilidades.get("1", probabilidades.get(1, 0.0))
            st.progress(p_mora, text=f"Probabilidad de Mora: {p_mora*100:.2f}%")

    except requests.exceptions.HTTPError as e:
        # Aquí capturamos el error 503 o 422 y mostramos el detalle de la API
        st.error(f"Error de la API: {resp.json().get('detail', str(e))}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")