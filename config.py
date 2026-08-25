import os
from dotenv import load_dotenv
load_dotenv()
# Configuración de SafeGuard
# Este archivo contiene las configuraciones principales de la aplicación

# API de Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Configuración de archivos
DATA_DIRECTORY = "data"
HISTORIAL_FILE = "historial_analisis.json"

# Configuración del servidor
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# Límites de la aplicación
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_TEXT_LENGTH = 10000  # caracteres

# Umbrales de detección (0-100)
RISK_HIGH_THRESHOLD = 70
RISK_MEDIUM_THRESHOLD = 30

# Configuración de reportes
REPORTS_TITLE = "Reporte de Análisis Anti-Grooming"
COMPANY_NAME = "SafeGuard"

# Números de emergencia (personalizar según país/región)
EMERGENCY_NUMBERS = {
    "general": "911",
    "linea_ayuda": "0800-222-1717",
    "email_denuncias": "denuncias@ciberseguridad.gov"
}

# Mensajes del sistema
SYSTEM_MESSAGES = {
    "analyzing": "Analizando contenido con IA...",
    "no_threat": "No se detectaron señales de grooming",
    "threat_detected": "Se detectaron señales de grooming",
    "error": "Error en el análisis. Intenta nuevamente."
}

# Recomendaciones por nivel de riesgo
RECOMMENDATIONS = {
    "alto": [
        "Contactar inmediatamente a las autoridades (911)",
        "Guardar toda la evidencia (capturas de pantalla, mensajes)",
        "No confrontar al agresor directamente",
        "Proteger al menor manteniendo la calma",
        "Buscar ayuda profesional especializada"
    ],
    "medio": [
        "Aumentar la supervisión de las actividades en línea",
        "Hablar con el menor sobre seguridad digital",
        "Monitorear más de cerca las comunicaciones",
        "Educar sobre las señales de peligro",
        "Considerar contactar a un especialista"
    ],
    "bajo": [
        "Mantener comunicación abierta con el menor",
        "Continuar con supervisión regular",
        "Reforzar educación sobre seguridad en línea",
        "Estar atento a cambios de comportamiento",
        "Fomentar la confianza para reportar problemas"
    ]
}