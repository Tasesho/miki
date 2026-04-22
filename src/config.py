import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener token y API keys
TOKEN = os.getenv("TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# Validar que el token esté configurado
if not TOKEN:
    raise ValueError(" TOKEN no está configurado. Verifica tu archivo .env")
