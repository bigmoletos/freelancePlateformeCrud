import os
from typing import Dict, List, Any
from dotenv import load_dotenv
# import PyPDF2
import re
import requests
from collections import Counter
from prettytable import PrettyTable
import json
import logging
# from pyresparser import ResumeParser
import spacy
# import en_core_web_sm
import fr_core_news_md

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')
logger = logging.getLogger(__name__)

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class GestionProfil:

    def __init__(self) -> None:
        """
        Initialise la classe GestionProfil.

        Charge les variables d'environnement et initialise le profil.
        """
        logger.info("Initialisation de GestionProfil")
        load_dotenv()
        self.email: str = os.getenv('FREELANCE_EMAIL', '')
        self.password: str = os.getenv('FREELANCE_PASSWORD', '')
        self.profil: Dict[str, Any] = {}
        # self.cv_path: str = "data/cv.pdf"
        self.cv_path: str = "data/cv.txt"
        self.nlp = fr_core_news_md.load()
        try:
            self.extraire_cv()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du CV : {e}")

    def extraire_cv(self) -> None:
        """
        Extrait les informations du CV et les stocke dans self.profil.
        """
        logger.info(f"Extraction du CV depuis {self.cv_path}")
        try:
            with open(self.cv_path, 'r', encoding='utf-8') as file:
                texte_cv = file.read()

            doc = self.nlp(texte_cv)

            # Extraction des informations basiques
            self.profil['nom'] = ''
            self.profil['prenom'] = ''
            self.profil['email'] = ''
            self.profil['telephone'] = ''
            self.profil['competences'] = []
            self.profil['experience'] = []
            self.profil['formation'] = []
            self.profil['titre'] = ''

            # Extraction des entités nommées
            for ent in doc.ents:
                if ent.label_ == 'PER':
                    noms = ent.text.split()
                    if len(noms) > 1:
                        self.profil['prenom'] = noms[0]
                        self.profil['nom'] = ' '.join(noms[1:])
                elif ent.label_ == 'EMAIL':
                    self.profil['email'] = ent.text
                elif ent.label_ == 'PHONE':
                    self.profil['telephone'] = ent.text

            # Extraction des compétences (à adapter selon votre CV)
            self.profil['competences'] = [
                token.text for token in doc
                if token.pos_ == 'NOUN' and token.is_alpha
            ]

            # Extraction du titre (première ligne non vide du CV)
            self.profil['titre'] = next(
                (line.strip()
                 for line in texte_cv.split('\n') if line.strip()), '')

            logger.info("Informations extraites du CV avec succès")
            logger.debug(f"Profil extrait : {self.profil}")
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du CV : {e}")
            raise

    def creer_compte_upwork(self) -> None:
        """
        Crée un compte sur Upwork en utilisant les informations du profil.

        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête HTTP.
        """
        logger.info("Création de compte Upwork")
        url = "https://www.upwork.com/signup/"
        data = {
            "email": self.email,
            "password": self.password,
            "firstName": self.profil['prenom'],
            "lastName": self.profil['nom'],
            "title": self.profil['titre'],
            "skills": ", ".join(self.profil['competences'])
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info("Compte Upwork créé avec succès")
            else:
                logger.error(f"Échec de la création du compte Upwork. Code d'erreur : {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la création du compte Upwork : {e}")

    def maj_profil_linkedin(self) -> None:
        """
        Met à jour le profil LinkedIn avec les informations du profil local.

        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête HTTP.
        """
        logger.info("Mise à jour du profil LinkedIn")
        url = "https://api.linkedin.com/v2/people/(id:{profile_id})"
        headers = {
            "Authorization": f"Bearer {self.linkedin_token}",
            "Content-Type": "application/json"
        }
        data = {
            "firstName": {"localized": {"fr_FR": self.profil['prenom']}},
            "lastName": {"localized": {"fr_FR": self.profil['nom']}},
            "headline": {"localized": {"fr_FR": self.profil['titre']}}
        }
        try:
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code == 200:
                logger.info("Profil LinkedIn mis à jour avec succès")
            else:
                logger.error(f"Échec de la mise à jour du profil LinkedIn. Code d'erreur : {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la mise à jour du profil LinkedIn : {e}")

    def obtenir_statistiques(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des offres sur toutes les plateformes.
        """
        logger.info("Récupération des statistiques globales")
        stats_globales = {
            "offres_par_region": Counter(),
            "offres_par_type_poste": Counter(),
            "tjm_moyen": [],
            "durees": []
        }

        # Simulation de récupération de statistiques
        logger.debug("Simulation de récupération de statistiques")
        stats_globales["offres_par_region"].update({"Paris": 50, "Lyon": 30, "Marseille": 20})
        stats_globales["offres_par_type_poste"].update({"Développeur": 60, "Designer": 40})
        stats_globales["tjm_moyen"] = [450, 500, 400]
        stats_globales["durees"] = [30, 60, 90, 120]

        # Calcul du TJM moyen
        if stats_globales["tjm_moyen"]:
            stats_globales["tjm_moyen"] = sum(stats_globales["tjm_moyen"]) / len(stats_globales["tjm_moyen"])
        else:
            stats_globales["tjm_moyen"] = 0

        logger.info("Statistiques globales récupérées")
        logger.debug(f"Statistiques : {stats_globales}")
        return stats_globales

    def afficher_statistiques(self, statistiques: Dict[str, Any]) -> None:
        """
        Affiche les statistiques des offres de manière formatée.
        """
        logger.info("Affichage des statistiques")
        print("Statistiques des offres :")
        print()

        # Affichage des offres par région
        logger.debug("Affichage des offres par région")
        table_region = PrettyTable()
        table_region.field_names = ["Région", "Nombre d'offres"]
        for region, nombre in statistiques["offres_par_region"].most_common():
            table_region.add_row([region, nombre])
        print("Offres par région :")
        print(table_region)
        print()

        # Affichage des offres par type de poste
        logger.debug("Affichage des offres par type de poste")
        table_poste = PrettyTable()
        table_poste.field_names = ["Type de poste", "Nombre d'offres"]
        for poste, nombre in statistiques["offres_par_type_poste"].most_common():
            table_poste.add_row([poste, nombre])
        print("Offres par type de poste :")
        print(table_poste)
        print()

        # Affichage du TJM moyen
        logger.debug(f"Affichage du TJM moyen : {statistiques['tjm_moyen']:.2f} €")
        print(f"TJM moyen : {statistiques['tjm_moyen']:.2f} €")
        print()

        # Affichage des durées des missions
        logger.debug("Affichage des durées des missions")
        durees = statistiques["durees"]
        if durees:
            print("Durées des missions :")
            print(f"- Minimum : {min(durees)} jours")
            print(f"- Maximum : {max(durees)} jours")
            print(f"- Moyenne : {sum(durees) / len(durees):.0f} jours")
        else:
            print("Aucune information sur les durées des missions")

        logger.info("Fin de l'affichage des statistiques")

if __name__ == "__main__":
    logger.info("Démarrage du programme")
    gestionnaire = GestionProfil()
    logger.info("Récupération des statistiques")
    stats = gestionnaire.obtenir_statistiques()
    logger.info("Affichage des statistiques")
    gestionnaire.afficher_statistiques(stats)
    logger.info("Fin du programme")
