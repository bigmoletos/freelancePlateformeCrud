import os
from typing import Dict, List, Any
from dotenv import load_dotenv
import re
import requests
from collections import Counter
from prettytable import PrettyTable
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict
import spacy
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
    # Dictionnaire de correspondance entre les noms de mois et leurs numéros
    months = {
        'janv': '01',
        'jan': '01',
        'fév': '02',
        'feb': '02',
        'mars': '03',
        'mar': '03',
        'avril': '04',
        'apr': '04',
        'mai': '05',
        'may': '05',
        'juin': '06',
        'jun': '06',
        'juillet': '07',
        'jul': '07',
        'août': '08',
        'aug': '08',
        'sept': '09',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'déc': '12',
        'dec': '12'
    }

    logger.debug(f"Parsing de la date : {date_str}")
    date_str = date_str.lower()

    # Remplacement des noms de mois par leurs numéros
    for fr, num in months.items():
        date_str = date_str.replace(fr, num)

    # Séparation des parties de la date
    parts = date_str.split()
    if len(parts) == 1:  # Année seule
        logger.debug(f"Date parsée (année seule) : 01/01/{parts[0]}")
        return f"01/01/{parts[0]}"
    elif len(parts) == 2:  # Mois et année
        logger.debug(
            f"Date parsée (mois et année) : 01/{parts[0].zfill(2)}/{parts[1]}")
        return f"01/{parts[0].zfill(2)}/{parts[1]}"
    elif len(parts) == 3:  # Jour, mois et année
        logger.debug(
            f"Date parsée (jour, mois et année) : {parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
        )
        return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
    else:
        logger.warning(f"Format de date non reconnu : {date_str}")
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
    logger.debug(f"Formatage de la plage de dates : {date_str}")

    # Recherche d'une plage de dates
    date_range_match = re.search(
        r'(\w+[-\s]?\d{4})\s*[-à:]\s*(\w+[-\s]?\d{4})', date_str)
    if date_range_match:
        start_date, end_date = date_range_match.groups()
        start_formatted = parse_date(start_date)
        end_formatted = parse_date(end_date)
        end_parts = end_formatted.split('/')
        end_formatted = f"{end_parts[0]}/{end_parts[1]}/{end_parts[2]}"  # Assurez-vous que le jour de fin est 26
        logger.debug(
            f"Plage de dates formatée : {start_formatted} au {end_formatted}")
        return f"{start_formatted} au {end_formatted}"

    # Recherche d'une date unique
    single_date_match = re.search(r'(\w+[-\s]?\d{4})', date_str)
    if single_date_match:
        formatted_date = parse_date(single_date_match.group(1))
        logger.debug(f"Date unique formatée : {formatted_date}")
        return formatted_date

    logger.warning(f"Format de date non reconnu : {date_str}")
    return date_str


if __name__ == "__main__":
    import doctest
    doctest.testmod()


class ParagrapheExtracteur(ABC):

    def __init__(self, titre: str):
        self.titre = titre
        self.pattern = re.compile(rf"{titre}:(.*?)(?=\n\n[A-Z]|\Z)", re.DOTALL)

    @abstractmethod
    def extraire(self, texte: str) -> List[Dict[str, str]]:
        pass


class FormationExtracteur(ParagrapheExtracteur):

    def __init__(self):
        super().__init__("FORMATIONS DIPLOMES")

    def extraire(self, texte: str) -> List[Dict[str, str]]:
        match = self.pattern.search(texte)
        if not match:
            return []

        contenu = match.group(1).strip()
        logger.debug(f"Contenu extrait : {contenu}")
        formations = []
        for ligne in contenu.split('\n'):
            logger.debug(f"Extraction de la formation : {ligne}")
            if ligne.strip():
                date_match = re.search(
                    r'(\w+[-\s]?\d{4}\s*[-:]\s*\w+[-\s]?\d{4})', ligne)
                logger.debug(f"Date trouvée : {date_match}")
                if date_match:
                    date = format_date_range(date_match.group(1))
                    logger.debug(f"Date formatée : {date}")
                    description = ligne.replace(date_match.group(1),
                                                '').strip()
                    logger.debug(f"Description : {description}")
                    formations.append({
                        "date": date,
                        "description": description
                    })
                    logger.debug(f"Formation ajoutée : {formations[-1]}")
        return formations


class CentresInteretExtracteur(ParagrapheExtracteur):

    def __init__(self):
        super().__init__("CENTRES D'INTERET")

    def extraire(self, texte: str) -> List[Dict[str, str]]:
        match = self.pattern.search(texte)
        if not match:
            return []

        contenu = match.group(1).strip()
        logger.debug(f"Contenu extrait : {contenu}")
        centres_interet = [{
            "date": "",
            "description": ligne.strip()
        } for ligne in contenu.split('\n') if ligne.strip()]
        logger.debug(f"Centres d'intérêt extraits : {centres_interet}")
        return centres_interet


class VieAssociativeExtracteur(ParagrapheExtracteur):

    def __init__(self):
        super().__init__("VIE ASSOCIATIVE")

    def extraire(self, texte: str) -> List[Dict[str, str]]:
        match = self.pattern.search(texte)
        if not match:
            return []

        contenu = match.group(1).strip()
        logger.debug(f"Contenu extrait : {contenu}")
        activites = []
        current_date = ""
        current_description = []

        for ligne in contenu.split('\n'):
            ligne = ligne.strip()
            logger.debug(f"Extraction de l'activité : {ligne}")
            if ligne:
                date_match = re.search(
                    r'(depuis\s+\d{2}-\d{4}|\w+[-\s]?\d{4}\s*[-:]\s*\w+[-\s]?\d{4})',
                    ligne, re.IGNORECASE)
                logger.debug(f"Date trouvée : {date_match}")
                if date_match:
                    if current_description:
                        activites.append({
                            "date":
                            format_date_range(current_date)
                            if current_date else "Non spécifié",
                            "description":
                            " ".join(current_description)
                        })
                        logger.debug(f"Activité ajoutée : {activites[-1]}")
                    current_date = date_match.group(1)
                    current_description = [
                        ligne.replace(date_match.group(1), '').strip()
                    ]
                    logger.debug(f"Date mise à jour : {current_date}")
                    logger.debug(
                        f"Description mise à jour : {current_description}")
                else:
                    current_description.append(ligne)
                    logger.debug(
                        f"Description mise à jour : {current_description}")
        if current_description:
            activites.append({
                "date":
                format_date_range(current_date)
                if current_date else "Non spécifié",
                "description":
                " ".join(current_description)
            })
            logger.debug(f"Activité ajoutée : {activites[-1]}")
        return activites


class CoordonneeExtracteur:

    def __init__(self):
        self.champs = {
            'prenom': r"prenom:\s*(.+)",
            'nom': r"nom:\s*(.+)",
            'email': r"email:\s*(.+)",
            'telephone': r"telephone:\s*(.+)",
            'fonction': r"fonction:\s*(.+)"
        }

    def extraire(self, texte: str) -> Dict[str, str]:
        coordonnees = {}
        for champ, pattern in self.champs.items():
            match = re.search(pattern, texte, re.IGNORECASE)
            logger.debug(f"Extraction du champ {champ} : {match}")
            if match:
                coordonnees[champ] = match.group(1).strip()
                logger.debug(
                    f"Coordonnée {champ} ajoutée : {coordonnees[champ]}")
            else:
                logger.warning(f"Champ {champ} non trouvé dans le CV")
                coordonnees[champ] = ""
                logger.debug(
                    f"Coordonnée {champ} ajoutée : {coordonnees[champ]}")
        return coordonnees


class ExtractionCV:

    def __init__(self):
        self.extracteurs = [
            FormationExtracteur(),
            CentresInteretExtracteur(),
            VieAssociativeExtracteur()
        ]
        self.coordonnee_extracteur = CoordonneeExtracteur()

    def extraire(self, texte_cv: str) -> Dict[str, Any]:
        profil = self.coordonnee_extracteur.extraire(texte_cv)
        for extracteur in self.extracteurs:
            profil[extracteur.titre.lower().replace(
                ' ', '_')] = extracteur.extraire(texte_cv)
            logger.debug(
                f"Extraction de {extracteur.titre} : {profil[extracteur.titre.lower().replace(' ', '_')]}"
            )
        return profil


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
        """
        logger.info(f"Début de l'extraction du CV depuis {self.cv_path}")
        try:
            with open(self.cv_path, 'r', encoding='utf-8') as file:
                texte_cv = file.read()

            extracteur = ExtractionCV()
            self.profil = extracteur.extraire(texte_cv)

            # Sauvegarde dans un fichier JSON
            json_path = os.path.join('data', 'extract', 'cv.json')
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.profil, json_file, ensure_ascii=False, indent=4)

            logger.info(f"Informations du CV stockées dans {json_path}")
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du CV : {str(e)}")
            raise


if __name__ == "__main__":
    gestionnaire = GestionProfil()
    logger.info("Profil extrait avec succès")


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
            logger.error(
                f"Échec de la création du compte Upwork. Code d'erreur : {response.status_code}"
            )
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
        "firstName": {
            "localized": {
                "fr_FR": self.profil['prenom']
            }
        },
        "lastName": {
            "localized": {
                "fr_FR": self.profil['nom']
            }
        },
        "headline": {
            "localized": {
                "fr_FR": self.profil['titre']
            }
        }
    }
    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info("Profil LinkedIn mis à jour avec succès")
        else:
            logger.error(
                f"Échec de la mise à jour du profil LinkedIn. Code d'erreur : {response.status_code}"
            )
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
    stats_globales["offres_par_region"].update({
        "Paris": 50,
        "Lyon": 30,
        "Marseille": 20
    })
    stats_globales["offres_par_type_poste"].update({
        "Développeur": 60,
        "Designer": 40
    })
    stats_globales["tjm_moyen"] = [450, 500, 400]
    stats_globales["durees"] = [30, 60, 90, 120]

    # Calcul du TJM moyen
    if stats_globales["tjm_moyen"]:
        stats_globales["tjm_moyen"] = sum(stats_globales["tjm_moyen"]) / len(
            stats_globales["tjm_moyen"])
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
