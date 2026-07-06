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
            
            # --- SOLUCIÓN CONEXIÓN DIRECTA POR HTTP (OPCIÓN 3) ---
            import requests
            import json

            api_key = st.secrets["GEMINI_API_KEY"]
            # Usamos el endpoint oficial y moderno v1 con el modelo estable
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Estructuramos el JSON exacto que pide la API de Google
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{prompt_sistema}\n\nPregunta del usuario: {user_query}"}
                        ]
                    }
                ]
            }
            
            try:
                # Realizamos la petición web directa
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    response_data = response.json()
                    # Extraemos el texto de la respuesta de la estructura de Google
                    output_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Mostramos en pantalla y guardamos en historial
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                else:
                    st.error(f"Error de la API de Google (Código {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Ocurrió un inconveniente al procesar la comunicación directa: {str(e)}")
