from openai import OpenAI
from logger import logger
from dotenv import load_dotenv
from utils import nettoyer_json
import json
from json.decoder import JSONDecodeError

load_dotenv()
from config import API_KEY, ORGANIZATION_ID, PROJECT_ID


# Initialiser le client OpenAI, organization et projet étant optionnels
client = OpenAI(api_key=API_KEY,
                organization=ORGANIZATION_ID,
                project=PROJECT_ID)

logger.info("Client OpenAI initialisé avec succès.")
logger.info("démarrage du programme")



def extraire_informations_cv(contenu_cv):
    """Utiliser l'API OpenAI pour extraire les informations utiles d'un CV."""
    logger.info("Début de l'extraction des informations du CV")
    logger.debug(f"Contenu du CV : {contenu_cv[:100]}..."
                 )  # Log des 100 premiers caractères du CV
    logger.debug(f"Contenu du CV : {contenu_cv}")

    try:
        logger.info("Envoi de la requête à l'API OpenAI")
        # Prompt système pour définir le rôle de l'IA
        system_prompt = """
        Tu es un assistant qui aide à extraire les informations clés d'un CV au format texte et à les convertir en un fichier JSON structuré.
        Chaque section doit être bien définie avec des informations comme le prénom, le nom, l'email, le téléphone, la fonction,
        les expériences professionnelles, les formations, les projets, les centres d'intérêt, et la vie associative.
        Structure le tout de manière claire et concise.
        """

        # Envoyer la requête à l'API OpenAI avec le contenu du CV et le prompt utilisateur
        response = client.chat.completions.create(
            # model="gpt-4",
            model="gpt-4o",
            # model="gpt-3.5-turbo",
            # model="gpt-3.5",
            # model="gpt-4-turbo",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role":
                "user",
                "content":
                f"""Voici un CV sous forme de texte brut {contenu_cv}, extrait les informations et crée un fichier JSON bien structuré avec les sections appropriées par exemple:
prenom: Francois
nom: Romaru
adresse: 13009 La Ciotat
telephone:0663748518
email: romaru@yopmail.com
fonction: Full Stack Data Scientist

PARCOURS PROFESSIONNEL
EXPERIENCE 1:
    nov-2023 - sept-2024 :
        Full Stack Data Scientist  (AIOLIV )
        Prévision du vent en temps réel pour les JO de voile 2024 à Marseille,


EXPERIENCE 2:
    Mars-2020 à juin-2023:
        Intégrateur Logiciel- Support Java (Agirc-Arrco INFOTEL-AD ‘Missions)
        [Détails sur les responsabilités et technologies...]


Autres expériences,
formations,
projets,
vie associative,
centres d'intérêt
...
"""
            }],
            max_tokens=3000,
            temperature=0.5)

        # except Exception as e:
        #     logger.error(f"Erreur lors de l'appel API : {str(e)}")
        #     raise
        logger.info("Réponse reçue de l'API OpenAI")
        logger.debug(f"Réponse complète de l'API : {response}")

        content = response.choices[0].message.content
        logger.debug(f"Contenu brut de la réponse : {content}")

        content_nettoye = nettoyer_json(content)

        try:
            parsed_json = json.loads(content_nettoye)
            logger.info("Parsing du JSON réussi")
            return parsed_json
        except JSONDecodeError as json_err:
            logger.error(f"Erreur de décodage JSON : {json_err}")
            return {
                "error": "Impossible de décoder la réponse en JSON",
                "contenu": content_nettoye
            }

    except Exception as e:
        logger.error(f"Erreur lors de l'appel API : {str(e)}")
        raise
