import os

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("No se encontró GEMINI_API_KEY en el archivo .env")
    st.stop()

client = genai.Client(api_key=api_key)


st.set_page_config(
    page_title="EmpleaBot",
    page_icon="💼"
)

st.title("💼 EmpleaBot")
st.write("Asistente especializado en empleabilidad")


SYSTEM_PROMPT = """
Actúa como EmpleaBot, un asistente especializado en empleabilidad.

OBJETIVO:
Ayudar a estudiantes y personas que buscan empleo en:
- Preparación para entrevistas.
- Revisión de competencias.
- Orientación para búsqueda laboral.
- Mejora de CV y perfil profesional.

INSTRUCCIONES:
- Responde de manera clara, profesional y cordial.
- Personaliza las respuestas según la información proporcionada.
- Haz preguntas cuando necesites información adicional.
- En simulaciones de entrevista realiza una pregunta a la vez.
- Proporciona retroalimentación después de las respuestas.
- Explica brevemente tus recomendaciones.
- Da recomendaciones prácticas y fáciles de aplicar.

RESTRICCIONES:
- No inventes información sobre el usuario.
- No garantices que conseguirá un empleo.
- No inventes ofertas laborales.
- No realices procesos de selección en nombre de empresas.
- No desarrolles completamente proyectos académicos.
- No respondas preguntas que no estén relacionadas con empleabilidad.

CONTROL DE DOMINIO:
Antes de responder, determina si la consulta está relacionada
con empleabilidad.

Si la consulta NO está relacionada con empleabilidad,
NO respondas la pregunta solicitada.

En ese caso responde únicamente:

"Puedo ayudarte con entrevistas, competencias, búsqueda laboral
y CV. ¿Qué aspecto de tu empleabilidad deseas trabajar?"
"""


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.chat_input(
    "Escribe tu consulta sobre empleabilidad..."
)

if prompt:

    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    try:

        conversation = ""

        for message in st.session_state.messages:

            conversation += (
                f"{message['role']}: "
                f"{message['content']}\n"
            )

        # Solicitud a Gemini

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        answer = response.text

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:

        error_text = str(e)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            st.warning(
                "⚠️ Se alcanzó el límite gratuito temporal "
                "de la API de Gemini."
            )

            st.info(
                "El chatbot está correctamente configurado, "
                "pero la API gratuita no tiene solicitudes "
                "disponibles en este momento. "
                "Vuelve a intentarlo cuando se restablezca "
                "la cuota."
            )

        elif (
            "503" in error_text
            or "UNAVAILABLE" in error_text
        ):

            st.warning(
                "⚠️ El servicio de Gemini está temporalmente "
                "ocupado. Intenta nuevamente en unos minutos."
            )

        else:

            st.error(
                "Ocurrió un problema al procesar la consulta."
            )