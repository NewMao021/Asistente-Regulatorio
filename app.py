import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuración de la página web
st.set_page_config(page_title="Asistente Corporativo Inteligente", page_icon="🤖", layout="centered")

# Configurar la API Key de Gemini desde los secretos seguros del servidor
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la configuración de GEMINI_API_KEY en los secretos del servidor.")
    st.stop()

# --- CORRECCIÓN 1: EXTRACCIÓN CORRECTA DEL ID DE TU ENLACE ---
# Extraje el ID real de tu enlace para construir la URL de descarga directa en CSV
SHEET_ID = "1zCqf7ohMD2ouAfqMLoTBw8KuUozZGEHd"
MAP_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300) # Guarda en caché los datos por 5 minutos para ahorrar ancho de banda
def obtener_datos_contexto():
    try:
        df = pd.read_csv(MAP_URL)
        # Convertimos las filas del Excel a un formato de texto legible para la IA
        contexto_lista = []
        for index, row in df.iterrows():
            elementos_fila = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
            contexto_lista.append(" | ".join(elementos_fila))
        return "\n".join(contexto_lista)
    except Exception as e:
        # --- CORRECCIÓN 2: Indentación corregida aquí (4 espacios más a la derecha) ---
        return f"Error al cargar los datos del Excel: {str(e)}"

# Interfaz Gráfica de Usuario (UI)
st.title("🤖 Asistente de IA Empresarial")
st.write("Pregúntame cualquier detalle sobre el inventario, políticas o datos internos de la empresa.")

# Inicializar historial de chat aislado por usuario
# --- CORRECCIÓN 3: Indentación corregida aquí ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar historial de conversación existente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar consulta del usuario
if user_query := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generar respuesta de la IA
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de datos..."):
            # 1. Obtener la información del Excel actualizado
            datos_empresa = obtener_datos_contexto()

            # 2. Diseñar el prompt del sistema instructivo
            prompt_sistema = (
                "Eres el asistente virtual oficial de la empresa. Tu deber es responder preguntas de clientes o "
                "empleados basándote única y exclusivamente en los siguientes datos actuales extraídos de nuestro "
                "documento Excel interno:\n\n"
                f"{datos_empresa}\n\n"
                "Instrucciones estrictas:\n"
                "1. Si la información solicitada no está en los datos provistos, responde amablemente que no dispones "
                "de ese dato por el momento.\n"
                "2. Sé profesional, claro y conciso.\n"
                "3. Responde siempre en el mismo idioma en el que te hablan."
            )
            try:
                model = genai.GenerativeModel('chat-bison-001')
                # --- CORRECCIÓN 4: Se unificó el salto de línea roto en el texto del prompt ---
                response = model.generate_content(f"{prompt_sistema}\n\nPregunta del usuario: {user_query}")
                output_text = response.text
                st.markdown(output_text)
                st.session_state.messages.append({"role": "assistant", "content": output_text})
            except Exception as e:
                st.error(f"Ocurrió un inconveniente al procesar la IA: {str(e)}")
