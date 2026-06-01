# services/openwa_service.py
import requests
from django.conf import settings

def send_whatsapp_message(session_id, phone_number, message_text):
    """
    Envía un mensaje de texto vía OpenWA.
    El número debe incluir código de país sin '+' ni espacios, y terminar en '@c.us'
    """
    url = f"{settings.OPENWA_API_URL}/sessions/{session_id}/messages/send-text"
    headers = {
        "X-API-Key": settings.OPENWA_API_KEY,
        "Content-Type": "application/json",
    }
    # Formato del chatId: "521234567890@c.us" (código de país + número)
    formatted_chat_id = f"{phone_number}@c.us"
    payload = {
        "chatId": formatted_chat_id,
        "text": message_text,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Lanza una excepción si hay error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        # Aquí podrías loguear el error y manejarlo según tu lógica de negocio
        print(f"Error al enviar mensaje: {e}")
        return None