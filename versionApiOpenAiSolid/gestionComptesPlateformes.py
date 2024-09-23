import json
import requests
from logger import logger
from config import FREELANCE_EMAIL, FREELANCE_PASSWORD
from cv_loader import CVLoader



class Plateforme:

    def __init__(self, nom, url):
   
        """
        Initialiser la plateforme avec un nom et une URL.

        :param nom: Nom de la plateforme
        :param url: URL de la plateforme
        """
        self.nom = nom
        self.url = url

    def creer_compte(self):
        """
        Créer un compte sur la plateforme.
        Cette méthode utilise des requêtes HTTP pour accéder à l'URL de la plateforme,
        remplir le formulaire d'inscription et soumettre le formulaire.
        """
        logger.info(f"Création du compte sur {self.nom}")
        self.remplir_formulaire_inscription()
        logger.info(f"Compte créé sur {self.nom}")

    def remplir_formulaire_inscription(self):
        """
        Remplir le formulaire d'inscription spécifique à la plateforme.
        Cette méthode doit être implémentée par les sous-classes pour fournir les étapes spécifiques.
        """
        raise NotImplementedError("Cette méthode doit être implémentée par les sous-classes.")

    def mettre_a_jour_profil(self, profil):
        """
        Mettre à jour le profil sur la plateforme.
        Cette méthode doit être implémentée par les sous-classes.

        :param profil: Dictionnaire contenant les informations du profil
        """
        raise NotImplementedError("Cette méthode doit être implémentée par les sous-classes.")

    def obtenir_statistiques(self):
        """
        Obtenir des statistiques sur la plateforme.
        Cette méthode doit être implémentée par les sous-classes.

        :return: Dictionnaire contenant les statistiques de la plateforme
        """
        raise NotImplementedError("Cette méthode doit être implémentée par les sous-classes.")

class Malt(Plateforme):
    def __init__(self):
        # super().__init__('Malt', 'https://www.malt.fr/freelancer-signup/signup/headline')
        super().__init__('Malt', 'https://www.malt.fr/registration/api/user/me')
# pai d'inscription https://www.malt.fr/registration/api/user/me

    def remplir_formulaire_inscription(self):
        """
        Remplir le formulaire d'inscription pour Malt en utilisant l'API et les données du CV.
        """
        session = requests.Session()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # Charger les données du CV
        with open("data/extract/cv.json", "r",
                  encoding="utf-8") as fichier_json:
            cv = json.load(fichier_json)

    # def mettre_a_jour_profil(self, profil):
    #     """Mettre à jour le profil sur Upwork."""
    #     logger.info(f"Mise à jour du profil sur {self.nom}")
    #     # Implémentation spécifique pour mettre à jour le profil Upwork
    #     pass
#https://www.malt.fr/api/profile/new/with-account
# {"location":"Marseille, France","countryCode":"FR","city":"Marseille","country":"France","administrativeAreaLevel1":"Provence-Alpes-Côte d'Azur","administrativeAreaLevel1Code":"Provence-Alpes-Côte d'Azur","administrativeAreaLevel2":"Bouches-du-Rhône","administrativeAreaLevel2Code":null,"administrativeAreaLevel3":null,"administrativeAreaLevel3Code":null,"administrativeAreaLevel4":null,"administrativeAreaLevel4Code":null,"lat":43.29695,"lon":5.38107,"workPlacePreference":"ONSITE","willingnessToTravelInternationally":false,"headline":"data scientist","experienceLevel":"INTERMEDIATE","tags":["Machine learning","Python","Data visualisation","SQL","Scikit-learn","Deep Learning","Analyse de données","Pandas","TensorFlow","NLP","Big Data","Data mining","Git","Gestion de projet","Microsoft Excel"],"price":550,"priceHidden":false,"phoneNumber":"+33663748518","families":["data"],"categories":["data_scientist","data_analyst"],"preferredFamily":"data","preferredCategory":"data_scientist","categorySuggestion":null,"industryExpertises":[],"functionalSkills":[],"invitationCode":null,"languages":[{"language":{"code":"fr","name":"Français"},"level":"NATIVE"}],"funnelMode":"FREELANCER","corporateProgram":null}

# Extraire les compétences du CV
        competences = []
        for experience in cv.get("parcours_professionnel", []):
            competences.extend(experience.get("technologies", []))
        competences = list(set(competences))  # Supprimer les doublons

        # Préparer les données pour l'inscription
        data = {
            "location": f"{cv.get('adresse', 'Marseille')}, France",
            "countryCode": "FR",
            "city": cv.get('adresse', 'Marseille').split(',')[0].strip(),
            "country": "France",
            "administrativeAreaLevel1": "Provence-Alpes-Côte d'Azur",
            "administrativeAreaLevel1Code": "Provence-Alpes-Côte d'Azur",
            "administrativeAreaLevel2": "Bouches-du-Rhône",
            "lat": 43.29695,  # Ces valeurs devraient idéalement être obtenues via une API de géocodage
            "lon": 5.38107,
            "workPlacePreference": "ONSITE",
            "willingnessToTravelInternationally": False,
            "headline": cv.get("fonction", ""),
            "experienceLevel": "INTERMEDIATE",  # Cette valeur pourrait être déterminée en fonction de l'expérience dans le CV
            "tags": competences[:15],  # Malt limite probablement le nombre de tags
            "price": 550,  # Cette valeur devrait être déterminée en fonction du CV ou des préférences de l'utilisateur
            "priceHidden": False,
            "phoneNumber": cv.get("telephone", ""),
            "families": ["data"],  # Cette valeur devrait être déterminée en fonction du CV
            "categories": ["data_scientist", "data_analyst"],  # Ces catégories devraient être déterminées en fonction du CV
            "preferredFamily": "data",
            "preferredCategory": "data_scientist",
            "languages": [{"language": {"code": "fr", "name": "Français"}, "level": "NATIVE"}],  # Ces informations devraient être extraites du CV
            "funnelMode": "FREELANCER"
        }

        # Envoyer la requête d'inscription
        response = session.post(self.url, json=data, headers=headers)
        if response.status_code != 200:
            logger.error(f"Échec de l'inscription sur {self.nom}: {response.text}")
            return

        # Créer le compte
        account_data = {
            "account": {
                "firstName": cv.get("prenom", ""),
                "lastName": cv.get("nom", ""),
                "email": FREELANCE_EMAIL,
                "password": FREELANCE_PASSWORD,
                "optOutFromNewsletter": True
            },
            "profileCreationRequestId": response.json().get("profileCreationRequestId")
        }

        response = session.post(f"{self.url}/with-account", json=account_data, headers=headers)
        if response.status_code != 200:
            logger.error(f"Échec de la création du compte sur {self.nom}: {response.text}")
            return

        logger.info(f"Inscription réussie sur {self.nom}")

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur Malt."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil Malt
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur Malt."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques AngelList
        pass

class LinkedIn(Plateforme):
    def __init__(self):
        super().__init__('LinkedIn', 'https://www.linkedin.com')

    def get_selectors(self):
        """Obtenir les sélecteurs pour LinkedIn."""
        return "#email-address", "#password", "#password"

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur LinkedIn."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil LinkedIn
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur LinkedIn."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques LinkedIn
        pass

class Dice(Plateforme):
    def __init__(self):
        super().__init__('Dice', 'https://www.dice.com')

    def get_selectors(self):
        """Obtenir les sélecteurs pour Dice."""
        return "#email", "#password", "#password"

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur Dice."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil Dice
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur Dice."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques Dice
        pass

class Upwork(Plateforme):
    def __init__(self):
        super().__init__('Upwork', 'https://www.upwork.com')

    def get_selectors(self):
        """Obtenir les sélecteurs pour Upwork."""
        return "#email", "#password", "button[type='submit']"

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur Upwork."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil Upwork
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur Upwork."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques Upwork
        pass

class Tekkit(Plateforme):
    def __init__(self):
        super().__init__('Tekkit', 'https://www.teckit.fr')

    def get_selectors(self):
        """Obtenir les sélecteurs pour Tekkit."""
        return "#email", "#password", "#password"

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur Tekkit."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil Tekkit
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur Tekkit."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques Tekkit
        pass

class GestionProfil:
    def __init__(self):
        """
        Initialiser la gestion des profils avec une liste de plateformes.
        """
        self.plateformes = [
            Upwork(),
            Freelancer(),
            Guru(),
            AngelList(),
            LinkedIn(),
            Dice(),
            Malt(),
            Tekkit()
        ]

    def creer_comptes(self):
        """
        Créer des comptes sur les plateformes disponibles.
        """
        for plateforme in self.plateformes:
            try:
                plateforme.creer_compte()
                logger.info(f"Compte créé sur {plateforme.nom}")
            except Exception as e:
                logger.error(f"Échec de la création du compte sur {plateforme.nom}: {str(e)}")

    def mise_a_jour_profil(self, profil):
        """
        Mettre à jour le profil sur les plateformes disponibles.

        :param profil: Dictionnaire contenant les informations du profil
        """
        for plateforme in self.plateformes:
            try:
                plateforme.mettre_a_jour_profil(profil)
                logger.info(f"Profil mis à jour sur {plateforme.nom}")
            except Exception as e:
                logger.error(f"Échec de la mise à jour du profil sur {plateforme.nom}: {str(e)}")

    def obtenir_statistiques(self):
        """
        Obtenir des statistiques sur les plateformes disponibles.

        :return: Dictionnaire contenant les statistiques de chaque plateforme
        """
        statistiques = {}
        for plateforme in self.plateformes:
            try:
                statistiques[plateforme.nom] = plateforme.obtenir_statistiques()
            except Exception as e:
                logger.error(f"Échec de l'obtention des statistiques sur {plateforme.nom}: {str(e)}")
        return statistiques

if __name__ == "__main__":
    gestionnaire = GestionProfil()

    # Extraction des données du CV
    chemin_fichier_cv = "data/extract/cv.json"
    with open(chemin_fichier_cv, "r", encoding="utf-8") as fichier_json:
        profil = json.load(fichier_json)

    # Création des comptes
    gestionnaire.creer_comptes()

    # Mise à jour du profil
    gestionnaire.mise_a_jour_profil(profil)

    # Obtention et affichage des statistiques
    stats = gestionnaire.obtenir_statistiques()
    # Afficher les statistiques (implémentez cette méthode selon vos besoins)
    # gestionnaire.afficher_statistiques(stats)
