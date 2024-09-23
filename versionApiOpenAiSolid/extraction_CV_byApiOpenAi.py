from openIA_client import extraire_informations_cv
from logger import logger
import json


def lire_fichier_cv(chemin_fichier):
    """Lire le contenu du fichier CV txt."""
    logger.info(f"Lecture du fichier CV : {chemin_fichier}")
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            contenu = fichier.read()
        logger.debug(
            f"Contenu du fichier CV (premiers 100 caractères) : {contenu[:100]}..."
        )
        return contenu
    except FileNotFoundError:
        logger.error(f"Le fichier {chemin_fichier} est introuvable.")
        raise


def ecrire_json_cv(data, chemin_fichier_json):
    """Écrire les données extraites dans un fichier JSON."""
    logger.info(
        f"Écriture des données dans le fichier JSON : {chemin_fichier_json}")
    try:
        with open(chemin_fichier_json, "w", encoding="utf-8") as fichier_json:
            json.dump(data, fichier_json, ensure_ascii=False, indent=4)
        logger.info(
            f"Le fichier {chemin_fichier_json} a été créé avec succès.")
    except IOError as e:
        logger.error(f"Erreur lors de la création du fichier JSON : {e}")
        raise


def process_cv(chemin_fichier_cv, chemin_fichier_json):
    """Traiter le CV : lire, extraire les informations et écrire dans un fichier JSON."""
    # Lire le fichier CV
    contenu_cv = lire_fichier_cv(chemin_fichier_cv)
    logger.info(f"Contenu du fichier CV : {contenu_cv}")

    # Extraire les informations via l'API OpenAI
    informations_cv = extraire_informations_cv(contenu_cv)
    logger.info(f"Informations extraites : {informations_cv}")
    # Écrire les informations dans un fichier JSON
    ecrire_json_cv(informations_cv, chemin_fichier_json)
    logger.info(f"Fichier JSON créé : {chemin_fichier_json}")
