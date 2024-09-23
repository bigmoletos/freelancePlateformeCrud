# config.py
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis .env
load_dotenv()

# Récupérer la clé API OpenAI
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError(
        "La clé API OpenAI n'a pas été définie correctement. Veuillez vérifier le fichier .env et définir OPENAI_API_KEY."
    )

# Récupérer le Project ID
PROJECT_ID = os.getenv("USE_PROJECT_ID")
if not PROJECT_ID:
    raise ValueError(
        "Le Project ID n'a pas été défini correctement. Veuillez vérifier le fichier .env et définir USE_PROJECT_ID."
    )

# Récupérer l'Organization ID
ORGANIZATION_ID = os.getenv("USE_ORGANIZATION_ID")
if not ORGANIZATION_ID:
    raise ValueError(
        "L'Organization ID n'a pas été défini correctement. Veuillez vérifier le fichier .env et définir USE_ORGANIZATION_ID."
    )
