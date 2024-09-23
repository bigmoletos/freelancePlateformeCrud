from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import logging
from json.decoder import JSONDecodeError
import re

# Charger la clé API depuis .env
load_dotenv()
from config import API_KEY, ORGANIZATION_ID, PROJECT_ID


# Configurer les logs pour fichier et console
logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Créer un gestionnaire de flux pour afficher dans la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Ajouter le gestionnaire de flux au logger
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)

logger.info("Client OpenAI initialisé avec succès.")

# Initialiser le client OpenAI
client = OpenAI(api_key=API_KEY,
                organization=ORGANIZATION_ID,
                project=PROJECT_ID)

logger.info("Client OpenAI initialisé avec succès.")
logger.info("démarrage du programme")


def lire_fichier_cv(chemin_fichier):
    """Lire le contenu du fichier CV texte."""
    logger.info(f"Lecture du fichier {chemin_fichier}")
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            contenu = fichier.read()
        return contenu
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Le fichier {chemin_fichier} est introuvable.")


def nettoyer_json(contenu):
    """Nettoie le contenu pour s'assurer qu'il s'agit d'un JSON valide."""
    logger.debug(f"Contenu avant nettoyage : {contenu}")
    # Supprimer tout texte avant le premier '{'
    contenu = re.sub(r'^[^{]*', '', contenu)
    # Supprimer tout texte après le dernier '}'
    contenu = re.sub(r'}[^}]*$', '}', contenu)
    logger.debug(f"Contenu après nettoyage : {contenu}")
    return contenu


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
            # model=           "gpt-4",  # Utilisez gpt-3.5-turbo si vous n'avez pas accès à GPT-4
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

def ecrire_json_cv(data, chemin_fichier_json):
    """Écrire les données extraites dans un fichier JSON."""
    logger
    try:
        with open(chemin_fichier_json, "w", encoding="utf-8") as fichier_json:
            json.dump(data, fichier_json, ensure_ascii=False, indent=4)
        print(f"Le fichier {chemin_fichier_json} a été créé avec succès.")
    except IOError as e:
        print(f"Erreur lors de la création du fichier JSON : {e}")


if __name__ == "__main__":
    # Chemin du fichier CV texte et du fichier JSON de sortie
    # Chemin du fichier CV texte
    chemin_fichier_cv = "C:\\programmation\\Projets_python\\plateformes_Freelance\\freelancePlateformeCrud\\freelancePlateformeCrud\\data\\cv.txt"
    # Chemin du fichier JSON à générer
    chemin_fichier_json = "C:\\programmation\\Projets_python\\plateformes_Freelance\\freelancePlateformeCrud\\freelancePlateformeCrud\\data\\extract\\cv.json"

    # Lire le contenu du fichier CV
    contenu_cv = lire_fichier_cv(chemin_fichier_cv)

    # Extraire les informations via GPT-4
    informations_cv = extraire_informations_cv(contenu_cv)

    # Si l'extraction a réussi, écrire les informations dans un fichier JSON
    if informations_cv:
        ecrire_json_cv(informations_cv, chemin_fichier_json)
