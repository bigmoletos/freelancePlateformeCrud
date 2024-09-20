import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import PyPDF2
import re
import requests


class GestionProfil:

    def __init__(self) -> None:
        """
        Initialise la classe GestionProfil.

        Charge les variables d'environnement, initialise le profil et extrait les données du CV.
        """
        load_dotenv()
        self.email: str = os.getenv('FREELANCE_EMAIL', '')
        self.password: str = os.getenv('FREELANCE_PASSWORD', '')
        self.profil: Dict[str, Any] = {}
        self.cv_path: str = "data/cv.pdf"
        self.extraire_cv()

    def extraire_cv(self) -> None:
        """
        Extrait les informations du CV et les stocke dans self.profil.

        Raises:
            Exception: Si une erreur survient lors de l'extraction du CV.
        """
        try:
            with open(self.cv_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

            self.profil['nom'] = self.extraire_info(text, r"Nom:\s*(.+)")
            self.profil['prenom'] = self.extraire_info(text, r"Prénom:\s*(.+)")
            self.profil['titre'] = self.extraire_info(text, r"Titre:\s*(.+)")
            self.profil['competences'] = self.extraire_liste(
                text, r"Compétences:\s*(.+)")
            self.profil['experience'] = self.extraire_experience(text)
            self.profil['formation'] = self.extraire_formation(text)

            print("Informations extraites du CV avec succès")
        except Exception as e:
            print(f"Erreur lors de l'extraction du CV : {e}")

    def extraire_info(self, text: str, pattern: str) -> str:
        """
        Extrait une information spécifique du texte en utilisant une expression régulière.

        Args:
            text (str): Le texte à analyser.
            pattern (str): L'expression régulière pour extraire l'information.

        Returns:
            str: L'information extraite ou une chaîne vide si non trouvée.

        >>> gp = GestionProfil()
        >>> gp.extraire_info("Nom: Dupont", r"Nom:\s*(.+)")
        'Dupont'
        >>> gp.extraire_info("Aucun nom", r"Nom:\s*(.+)")
        ''
        """
        match = re.search(pattern, text)
        return match.group(1) if match else ""

    def extraire_liste(self, text: str, pattern: str) -> List[str]:
        """
        Extrait une liste d'éléments du texte en utilisant une expression régulière.

        Args:
            text (str): Le texte à analyser.
            pattern (str): L'expression régulière pour extraire la liste.

        Returns:
            List[str]: La liste des éléments extraits.

        >>> gp = GestionProfil()
        >>> gp.extraire_liste("Compétences: Python, Java, C++", r"Compétences:\s*(.+)")
        ['Python', 'Java', 'C++']
        >>> gp.extraire_liste("Aucune compétence", r"Compétences:\s*(.+)")
        []
        """
        match = re.search(pattern, text)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []

    def creer_compte_upwork(self) -> None:
        """
        Crée un compte sur Upwork en utilisant les informations du profil.

        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête HTTP.
        """
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
                print("Compte Upwork créé avec succès")
            else:
                print(
                    f"Échec de la création du compte Upwork. Code d'erreur : {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la création du compte Upwork : {e}")

    def maj_profil_linkedin(self) -> None:
        """
        Met à jour le profil LinkedIn avec les informations du profil local.

        Raises:
            requests.exceptions.RequestException: Si une erreur survient lors de la requête HTTP.
        """
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
                print("Profil LinkedIn mis à jour avec succès")
            else:
                print(
                    f"Échec de la mise à jour du profil LinkedIn. Code d'erreur : {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la mise à jour du profil LinkedIn : {e}")


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    gestionnaire = GestionProfil()
    print("Profil extrait du CV :")
    print(json.dumps(gestionnaire.profil, indent=2, ensure_ascii=False))

    gestionnaire.creer_compte_upwork()
    gestionnaire.maj_profil_linkedin()
