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
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')
logger = logging.getLogger(__name__)

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def parse_date(date_str):
    """
    Parse une chaîne de date et la convertit en format 'DD/MM/YYYY'.

    Args:
        date_str (str): La chaîne de date à parser.

    Returns:
        str: La date au format 'DD/MM/YYYY'.

    >>> parse_date('janv 2021')
    '01/01/2021'
    >>> parse_date('15 mars 2022')
    '15/03/2022'
    >>> parse_date('2023')
    '01/01/2023'
    """
    months = {
        'janv': '01', 'jan': '01',
        'fév': '02', 'feb': '02',
        'mars': '03', 'mar': '03',
        'avril': '04', 'apr': '04',
        'mai': '05', 'may': '05',
        'juin': '06', 'jun': '06',
        'juillet': '07', 'jul': '07',
        'août': '08', 'aug': '08',
        'sept': '09', 'sep': '09',
        'oct': '10',
        'nov': '11',
        'déc': '12', 'dec': '12'
    }

    date_str = date_str.lower()
    for fr, num in months.items():
        date_str = date_str.replace(fr, num)

    parts = date_str.split()
    if len(parts) == 1:  # Année seule
        return f"01/01/{parts[0]}"
    elif len(parts) == 2:  # Mois et année
        return f"01/{parts[0].zfill(2)}/{parts[1]}"
    elif len(parts) == 3:  # Jour, mois et année
        return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
    else:
        return date_str

def format_date_range(date_str):
    """
    Formate une plage de dates en 'DD/MM/YYYY au DD/MM/YYYY'.

    Args:
        date_str (str): La chaîne de date à formater.

    Returns:
        str: La plage de dates formatée.

    >>> format_date_range('janv 2021 - déc 2021')
    '01/01/2021 au 26/12/2021'
    >>> format_date_range('2022')
    '01/01/2022'
    >>> format_date_range('09 2019 au 11 2019')
    '01/09/2019 au 26/11/2019'
    """
    date_range_match = re.search(r'(\w+[-\s]?\d{4})\s*[-à:]\s*(\w+[-\s]?\d{4})', date_str)
    if date_range_match:
        start_date, end_date = date_range_match.groups()
        start_formatted = parse_date(start_date)
        end_formatted = parse_date(end_date)
        end_parts = end_formatted.split('/')
        end_formatted = f"{end_parts[0]}/{end_parts[1]}/{end_parts[2]}"  # Assurez-vous que le jour de fin est 26
        return f"{start_formatted} au {end_formatted}"

    single_date_match = re.search(r'(\w+[-\s]?\d{4})', date_str)
    if single_date_match:
        return parse_date(single_date_match.group(1))

    return date_str

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
        self.cv_path: str = "data/cv.txt"
        self.nlp = fr_core_news_md.load()
        try:
            self.extraire_cv()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du CV : {e}")

    def extraire_cv(self) -> None:
        """
        Extrait les informations du CV et les stocke dans self.profil.

        Cette fonction lit le contenu du CV, extrait les différentes sections
        (informations de base, expérience, formation, etc.) et les stocke dans
        un dictionnaire structuré. Le résultat est ensuite sauvegardé dans un
        fichier JSON.

        Raises:
            Exception: Si une erreur survient lors de l'extraction ou du traitement des données.
        """
        logger.info(f"Début de l'extraction du CV depuis {self.cv_path}")
        try:
            # Lecture du fichier CV
            with open(self.cv_path, 'r', encoding='utf-8') as file:
                texte_cv = file.read()
            logger.debug("Fichier CV lu avec succès")

            self.profil = {
                'nom': '',
                'prenom': '',
                'email': '',
                'telephone': '',
                'competences': [],
                'experience': [],
                'formation': [],
                'fonction': '',
                'diplomes': [],
                'centres_interet': [],
                'vie_associative': [],
                'projets': []
            }

            # Extraction des informations de base
            logger.info("Extraction des informations de base")
            self.profil["prenom"] = re.search(r"prenom:\s*(.+)", texte_cv, re.IGNORECASE).group(1).strip()
            self.profil["nom"] = re.search(r"nom:\s*(.+)", texte_cv, re.IGNORECASE).group(1).strip()
            self.profil["email"] = re.search(r"email:\s*(.+)", texte_cv, re.IGNORECASE).group(1).strip()
            self.profil["telephone"] = re.search(r"telephone:\s*(.+)", texte_cv, re.IGNORECASE).group(1).strip()
            self.profil["fonction"] = re.search(r"fonction:\s*(.+)", texte_cv, re.IGNORECASE).group(1).strip()
            logger.debug(f"Informations de base extraites : {self.profil['prenom']} {self.profil['nom']}")

            # Extraction de l'expérience professionnelle
            logger.info("Extraction de l'expérience professionnelle")
            experience_matches = re.findall(r"EXPERIENCE \d+:\s*(.*?)(?=EXPERIENCE \d+:|PROJETS :|$)", texte_cv, re.DOTALL)
            for exp in experience_matches:
                lines = exp.strip().split('\n')
                if lines:
                    date_range = format_date_range(lines[0])
                    description = '\n'.join(lines[1:]).strip()
                    self.profil["experience"].append({"date": date_range, "description": description})
            logger.debug(f"Nombre d'expériences extraites : {len(self.profil['experience'])}")

            # Extraction des formations et diplômes
            logger.info("Extraction des formations et diplômes")
            formation_match = re.search(r"FORMATIONS DIPLOMES :(.*?)(?=CENTRES D'INTERET:|$)", texte_cv, re.DOTALL)
            if formation_match:
                formations = formation_match.group(1).strip().split('\n')
                for i in range(0, len(formations), 2):
                    if i+1 < len(formations):
                        date_range = format_date_range(formations[i])
                        description = formations[i+1].strip()
                        self.profil["formation"].append({"date": date_range, "description": description})
                        if "bac+" in description.lower() or "master" in description.lower() or "licence" in description.lower():
                            self.profil["diplomes"].append({"date": date_range, "description": description})
            logger.debug(f"Nombre de formations extraites : {len(self.profil['formation'])}")
            logger.debug(f"Nombre de diplômes extraits : {len(self.profil['diplomes'])}")

            # Extraction des centres d'intérêt
            logger.info("Extraction des centres d'intérêt")
            centres_interet_match = re.search(r"CENTRES D'INTERET:(.*?)(?=VIE ASSOCIATIVE:|$)", texte_cv, re.DOTALL)
            if centres_interet_match:
                centres_interet = centres_interet_match.group(1).strip().split('\n')
                self.profil["centres_interet"] = [{"date": "", "description": c.strip()} for c in centres_interet if c.strip()]
            logger.debug(f"Nombre de centres d'intérêt extraits : {len(self.profil['centres_interet'])}")

            # Extraction de la vie associative
            logger.info("Extraction de la vie associative")
            vie_associative_match = re.search(r"VIE ASSOCIATIVE:(.*?)(?=PROJETS :|$)", texte_cv, re.DOTALL)
            if vie_associative_match:
                vie_associative = vie_associative_match.group(1).strip().split('\n')
                current_description = []
                for ligne in vie_associative:
                    ligne = ligne.strip()
                    if ligne:
                        date_match = re.search(r'(\w+[-\s]?\d{4}\s*[-:]\s*\w+[-\s]?\d{4}|depuis\s+\d{2}-\d{4})', ligne, re.IGNORECASE)
                        if date_match:
                            if current_description:
                                self.profil["vie_associative"].append({
                                    "date": format_date_range(current_description[0]),
                                    "description": " ".join(current_description[1:])
                                })
                            current_description = [date_match.group(1), ligne.replace(date_match.group(1), '').strip()]
                        else:
                            current_description.append(ligne)
                if current_description:
                    self.profil["vie_associative"].append({
                        "date": format_date_range(current_description[0]),
                        "description": " ".join(current_description[1:])
                    })
            logger.debug(f"Nombre d'activités associatives extraites : {len(self.profil['vie_associative'])}")

            # Extraction des projets
            logger.info("Extraction des projets")
            projets_match = re.search(r"PROJETS :(.*?)(?=VEILLE TECHNOLOGIQUE:|FORMATIONS DIPLOMES :|$)", texte_cv, re.DOTALL)
            if projets_match:
                projets = projets_match.group(1).strip().split('\n')
                current_project = {}
                for ligne in projets:
                    ligne = ligne.strip()
                    if ligne:
                        date_match = re.search(r'(\w+[-\s]?\d{4}\s*[-:]\s*\w+[-\s]?\d{4})', ligne)
                        if date_match:
                            if current_project:
                                current_project["description"] = [desc for desc in current_project["description"] if desc]
                                self.profil["projets"].append(current_project)
                            current_project = {
                                "date": format_date_range(date_match.group(1)),
                                "description": [ligne.replace(date_match.group(1), '').strip()]
                            }
                        elif current_project:
                            current_project["description"].append(ligne)
                if current_project:
                    current_project["description"] = [desc for desc in current_project["description"] if desc]
                    self.profil["projets"].append(current_project)
            logger.debug(f"Nombre de projets extraits : {len(self.profil['projets'])}")

            # Stockage des informations du CV dans un fichier JSON
            json_path = os.path.join('data', 'extract', 'cv.json')
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.profil, json_file, ensure_ascii=False, indent=4)

            logger.info(f"Informations du CV stockées dans {json_path}")
            logger.info("Extraction du CV terminée avec succès")
            logger.debug(f"Profil extrait : {self.profil}")
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du CV : {str(e)}")
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
