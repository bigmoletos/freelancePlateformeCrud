from openai import OpenAI
import json
import logging
from dotenv import load_dotenv
from config import API_KEY, ORGANIZATION_ID, PROJECT_ID

# Charger la clé API depuis .env
load_dotenv()

# Configurer les logs
logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# Initialiser le client OpenAI
client = OpenAI(api_key=API_KEY,
                organization=ORGANIZATION_ID,
                project=PROJECT_ID)



def lire_fichier_cv(chemin_fichier):
    """Lire le contenu du fichier CV txt."""
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            contenu = fichier.read()
        logging.debug(f"Contenu du fichier CV: {contenu}")
        return contenu
    except FileNotFoundError as e:
        logging.error(f"Le fichier {chemin_fichier} est introuvable: {e}")
        raise


def extraire_informations_cv(contenu_cv):
    """Utiliser l'API OpenAI pour extraire les informations utiles d'un CV."""
    try:
        response = client.chat.completions.create(
            # model="gpt-4o",
            model="gpt-4",
            # model="gpt-3.5-turbo",
            # model="gpt-3.5",
            # model="gpt-4-turbo",
            messages=[{
                "role": "system",
                "content":
                """Tu es un assistant qui aide à extraire les informations clés d'un CV au format texte et à les convertir en un fichier JSON structuré. Chaque section doit être bien définie avec des informations comme le prénom, le nom, l'email, le téléphone, la fonction, les expériences professionnelles, les formations, les projets, les centres d'intérêt, et la vie associative. Structure le tout de manière claire et concise."""
            }, {
                "role": "user",
                "content":
                f"""Voici un CV sous forme de texte brut, extrait les informations et crée un fichier JSON bien structuré avec les sections appropriées :
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
        [Détails sur les responsabilités et technologies...]

EXPERIENCE 2:
    Mars-2020 à juin-2023:
        Intégrateur Logiciel- Support Java (Agirc-Arrco INFOTEL-AD ‘Missions)
        [Détails sur les responsabilités et technologies...]

[Autres expériences, formations, projets, vie associative, centres d'intérêt]
."""
            }],
            max_tokens=1000,
            temperature=0.7)
        # Debug de la réponse
        logging.debug(f"Réponse de l'API: {response}")

        # Extraire le contenu textuel et le convertir en JSON
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logging.error(f"Erreur lors de l'appel API: {e}")
        raise


def ecrire_json_cv(data, chemin_fichier_json):
    """Écrire les données extraites dans un fichier JSON."""
    try:
        with open(chemin_fichier_json, "w", encoding="utf-8") as fichier_json:
            json.dump(data, fichier_json, ensure_ascii=False, indent=4)
        logging.info(
            f"Le fichier {chemin_fichier_json} a été créé avec succès.")
    except IOError as e:
        logging.error(f"Erreur lors de la création du fichier JSON: {e}")
        raise


if __name__ == "__main__":
    # Chemin du fichier CV texte
    chemin_fichier_cv = "C:\\programmation\\Projets_python\\plateformes_Freelance\\freelancePlateformeCrud\\data\\cv.txt"
    # Chemin du fichier JSON à générer
    chemin_fichier_json = "cv.json"

    # Lire le fichier CV
    contenu_cv = lire_fichier_cv(chemin_fichier_cv)

    # Extraire les informations via l'API OpenAI
    informations_cv = extraire_informations_cv(contenu_cv)

    # Écrire les informations dans un fichier JSON
    ecrire_json_cv(informations_cv, chemin_fichier_json)
