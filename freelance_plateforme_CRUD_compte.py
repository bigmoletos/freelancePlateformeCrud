import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import PyPDF2
import re
import requests
from collections import Counter
from prettytable import PrettyTable

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
            self.profil['competences'] = self.extraire_liste(text, r"Compétences:\s*(.+)")
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
                print(f"Échec de la création du compte Upwork. Code d'erreur : {response.status_code}")
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
            "firstName": {"localized": {"fr_FR": self.profil['prenom']}},
            "lastName": {"localized": {"fr_FR": self.profil['nom']}},
            "headline": {"localized": {"fr_FR": self.profil['titre']}}
        }
        try:
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code == 200:
                print("Profil LinkedIn mis à jour avec succès")
            else:
                print(f"Échec de la mise à jour du profil LinkedIn. Code d'erreur : {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la mise à jour du profil LinkedIn : {e}")

    def obtenir_statistiques(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des offres sur toutes les plateformes.

        Returns:
            Dict[str, Any]: Un dictionnaire contenant les statistiques agrégées.
        """
        stats_globales = {
            "offres_par_region": Counter(),
            "offres_par_type_poste": Counter(),
            "tjm_moyen": [],
            "durees": []
        }

        for plateforme, url in self.plateformes.items():
            if url:
                try:
                    if plateforme == 'Upwork':
                        stats = self.stats_upwork()
                    elif plateforme == 'Freelancer':
                        stats = self.stats_freelancer()
                    # ... autres plateformes ...

                    stats_globales["offres_par_region"].update(stats.get("offres_par_region", {}))
                    stats_globales["offres_par_type_poste"].update(stats.get("offres_par_type_poste", {}))
                    stats_globales["tjm_moyen"].extend(stats.get("tjm", []))
                    stats_globales["durees"].extend(stats.get("durees", []))
                except Exception as e:
                    print(f"Erreur lors de la récupération des statistiques de {plateforme}: {e}")

        # Calcul du TJM moyen
        if stats_globales["tjm_moyen"]:
            stats_globales["tjm_moyen"] = sum(stats_globales["tjm_moyen"]) / len(stats_globales["tjm_moyen"])
        else:
            stats_globales["tjm_moyen"] = 0

        return stats_globales

    def afficher_statistiques(self, statistiques: Dict[str, Any]) -> None:
        """
        Affiche les statistiques des offres de manière formatée.

        Args:
            statistiques (Dict[str, Any]): Les statistiques à afficher.

        >>> gp = GestionProfil()
        >>> stats = {
        ...     "offres_par_region": Counter({"Paris": 50, "Lyon": 30, "Marseille": 20}),
        ...     "offres_par_type_poste": Counter({"Développeur": 60, "Designer": 40}),
        ...     "tjm_moyen": 450,
        ...     "durees": [30, 60, 90, 120]
        ... }
        >>> gp.afficher_statistiques(stats)
        Statistiques des offres :
        <BLANKLINE>
        Offres par région :
        +------------+-------------+
        |   Région   | Nombre d'offres |
        +------------+-------------+
        |   Paris    |     50      |
        |    Lyon    |     30      |
        | Marseille  |     20      |
        +------------+-------------+
        <BLANKLINE>
        Offres par type de poste :
        +-------------+-------------+
        | Type de poste | Nombre d'offres |
        +-------------+-------------+
        | Développeur |     60      |
        |  Designer   |     40      |
        +-------------+-------------+
        <BLANKLINE>
        TJM moyen : 450 €
        <BLANKLINE>
        Durées des missions :
        - Minimum : 30 jours
        - Maximum : 120 jours
        - Moyenne : 75 jours
        """
        print("Statistiques des offres :")
        print()

        # Affichage des offres par région
        table_region = PrettyTable()
        table_region.field_names = ["Région", "Nombre d'offres"]
        for region, nombre in statistiques["offres_par_region"].most_common():
            table_region.add_row([region, nombre])
        print("Offres par région :")
        print(table_region)
        print()

        # Affichage des offres par type de poste
        table_poste = PrettyTable()
        table_poste.field_names = ["Type de poste", "Nombre d'offres"]
        for poste, nombre in statistiques["offres_par_type_poste"].most_common():
            table_poste.add_row([poste, nombre])
        print("Offres par type de poste :")
        print(table_poste)
        print()

        # Affichage du TJM moyen
        print(f"TJM moyen : {statistiques['tjm_moyen']:.2f} €")
        print()

        # Affichage des durées des missions
        durees = statistiques["durees"]
        if durees:
            print("Durées des missions :")
            print(f"- Minimum : {min(durees)} jours")
            print(f"- Maximum : {max(durees)} jours")
            print(f"- Moyenne : {sum(durees) / len(durees):.0f} jours")
        else:
            print("Aucune information sur les durées des missions")

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    gestionnaire = GestionProfil()
    print("Profil extrait du CV :")
    print(json.dumps(gestionnaire.profil, indent=2, ensure_ascii=False))

    gestionnaire.creer_compte_upwork()
    gestionnaire.maj_profil_linkedin()
    # Obtention et affichage des statistiques
    stats = gestionnaire.obtenir_statistiques()
    gestionnaire.afficher_statistiques(stats)
