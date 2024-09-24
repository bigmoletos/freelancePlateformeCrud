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
        self.cv_loader = CVLoader()

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
        super().__init__('Malt', 'https://www.malt.fr')
        self.base_url = 'https://www.malt.fr'
        self.signin_url = f'{self.base_url}/registration/api/signin-request-with-authentication-details'
        self.profile_url = f'{self.base_url}/profile/api/experiences'

    def get_headers(self, action, cookies=None):
        """
        Générer les headers pour les différentes actions.
        """
        common_headers = {
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://www.malt.fr',
            'referer': 'https://www.malt.fr/signin?redirect=/freelancer-signup/completion/linkedin-import',
            'x-xsrf-token': '695c4839-5cf4-4492-923e-ae841ea8e757',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'priority': 'u=1, i'
        }

        if cookies:
            common_headers['cookie'] = cookies

        if action == 'signin':
            return common_headers
        elif action == 'profile':
            return {
                **common_headers,
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'X-Requested-With': 'XMLHttpRequest'
            }
        else:
            return common_headers

    def get_url(self, action):
        """
        Générer les URLs pour les différentes actions.
        """
        if action == 'signin':
            return self.signin_url
        elif action == 'profile':
            return self.profile_url
        else:
            return self.base_url

    def connexion(self):
        """
        Se connecter à Malt en utilisant l'API de connexion.
        """
        cookies = (
            'i18n=fr-FR; XSRF-TOKEN=695c4839-5cf4-4492-923e-ae841ea8e757; '
            'malt-visitorId=3f696c81-7d8c-4879-9cba-3953a135db93; '
            'OptanonAlertBoxClosed=2024-09-23T16:56:40.839Z; '
            '__cfruid=b5cb2b9015b8f6c7bb190cbad1a0f95accd4714c-1727110712; '
            'hopsi=66f1a66567839d4d3a38ae73; _gcl_au=1.1.1369150334.1727155236; '
            'JSESSIONID=93F05039E287436203635F74128E2414; '
            'remember-me=ZVBONHlXR1BHOWNuN3NzSDZVbWwlMkZ3JTNEJTNEOjdhSE5jQld6TDREMzZaYWY2aXhmWUElM0QlM0Q; '
            'SESSION=YWEwZDQyYmItMGI5NC00OGJmLWJmM2UtNGYzOWMzMTZlY2Fk; '
            'cf_clearance=sXIaLYo70lUKPCOS9qvbwgGQn0AJ9eA1Botvv.q8rdI-1727163624-1.2.1.1-'
            'u5XQtx2hOzFEAqknBS4MLYPEYvrvcThLj4yVP4e.7w9fb3wh4glezfSFpZzjfOF.78.iunFeTzZGo2XKMBIDliahRiN9zN1LNIs8Bo8HU9GBb_6sKrxCrdmVHFBAhgMbg6omyYrFgo2.j5iHh9U..TE_km9AzeViJR7TdR.OwCPok4j2W5sF.PlWmAsMGBEXq1ByyRPK_Y6rkrNfY2Db_kLkXEwhN.qamWnB.p5YrdF.hm7R_wtx2dtX60CBT.uC6zI6sTVJvD752R_l59j4jUO0bYBcELzyRG11xJtLcmmHR3WMkBxusprPQtaS6.UxIibsRwRhppLwp1.axIlzKmOS9saF3BUp8k9yhvO7XVk9SC21mEof4Decj0PMdhkr; '
            'OptanonConsent=isGpcEnabled=0&datestamp=Tue+Sep+24+2024+09%3A40%3A24+GMT%2B0200+(heure+d%E2%80%99%C3%A9t%C3%A9+d%E2%80%99Europe+centrale)&version=202211.2.0&isIABGlobal=false&hosts=&consentId=ff6c826b-7793-43b8-9d30-98d03acba425&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0004%3A0%2CC0005%3A0&AwaitingReconsent=false&geolocation=%3B; '
            '__cf_bm=VY7Dw0_.GUXnPxMg7i7q7vq2wq7o96IoaIZKJ5bbcs8-1727168606-1.0.1.1-yUCdBOQLxwCObMcaiU3.Ch0OrAqm5A.t_c814tlIA4lmWtqf54jsae.LcGdRUL1BaMfnQFo95rGqnFxOenaAmPTD0B8FZ06tD2fRHo.4pw0'
        )

        headers = self.get_headers('signin', cookies=cookies)

        data = {
            'email': FREELANCE_EMAIL,
            'password': FREELANCE_PASSWORD
        }

        try:
            response = requests.post(self.get_url('signin'), headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"Connexion réussie sur {self.nom}")
            return response.cookies
        except requests.exceptions.RequestException as e:
            logger.error(f"Échec de la connexion sur {self.nom}: {str(e)}")
            return None

    def completer_profil(self, cookies):
        """
        Compléter le profil sur Malt en utilisant l'API et les données du CV.
        """
        headers = self.get_headers('profile', cookies=cookies)

        cv = self.cv_loader.cv

        # Extraire les informations nécessaires du CV
        experience = cv.get("parcours_professionnel", [])[0]  # Utiliser la première expérience comme exemple
        location = cv.get("adresse", "Aix-en-Provence, France")
        city = location.split(',')[0].strip()
        start_date = experience.get("date_debut", "2023-01-24")
        end_date = experience.get("date_fin", "2024-09-17")
        title = experience.get("intitule_poste", "intitule du poste romaru")
        company = experience.get("nom_entreprise", "ferry")
        description = experience.get("description", "sdssdssdsdssddssdssdssssdqqqqqqqqqqzderthhhyregthhtgfregtzvrgezrgrevrgzgregzbzefzgrthththtrgrgrrgzrgr")

        # Préparer les données pour compléter le profil
        data = {
            "companyId": "",
            "endDate": f"{end_date}T00:00:00.000Z",
            "area": "IT",
            "asFreelance": True,
            "company": company,
            "description": description,
            "location": {
                "formattedAddress": location,
                "street": None,
                "street2": None,
                "city": city,
                "zipCode": "13080",
                "administrativeAreaLevel4": None,
                "administrativeAreaLevel4Code": None,
                "administrativeAreaLevel3": None,
                "administrativeAreaLevel3Code": None,
                "administrativeAreaLevel2": "Bouches-du-Rhône",
                "administrativeAreaLevel2Code": "13",
                "administrativeAreaLevel1": "Provence-Alpes-Côte d'Azur",
                "administrativeAreaLevel1Code": "93",
                "country": "France",
                "countryCode": "FR",
                "region": None,
                "loc": {
                    "lat": 43.5283,
                    "lon": 5.44973
                },
                "_links": []
            },
            "startDate": f"{start_date}T00:00:00.000Z",
            "title": title,
            "requestOrigin": "SIGNUP"
        }

        try:
            response = requests.post(self.get_url('profile'), headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"Profil complété sur {self.nom}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Échec de la complétion du profil sur {self.nom}: {str(e)}")

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur Malt."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil Malt
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur Malt."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques Malt
        pass

class Upwork(Plateforme):
    def __init__(self):
        super().__init__('Upwork', 'https://www.upwork.com')

    def remplir_formulaire_inscription(self):
        """Remplir le formulaire d'inscription pour Upwork."""
        logger.info(f"Remplissage du formulaire d'inscription pour {self.nom}")
        # Implémentation spécifique pour remplir le formulaire d'inscription Upwork
        pass

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

class Freelancer(Plateforme):
    def __init__(self):
        super().__init__('Freelancer', 'https://www.freelancer.com')

    def remplir_formulaire_inscription(self):
        """Remplir le formulaire d'inscription pour Freelancer."""
        logger.info(f"Remplissage du formulaire d'inscription pour {self.nom}")
        # Implémentation spécifique pour remplir le formulaire d'inscription Freelancer
        pass

    def mettre_a_jour_profil(self, profil):
        """Mettre à jour le profil sur Freelancer."""
        logger.info(f"Mise à jour du profil sur {self.nom}")
        # Implémentation spécifique pour mettre à jour le profil Freelancer
        pass

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur Freelancer."""
        logger.info(f"Obtention des statistiques sur {self.nom}")
        # Implémentation spécifique pour obtenir les statistiques Freelancer
        pass

class GestionProfil:
    def __init__(self):
        self.plateformes = [Malt(), Upwork(), Freelancer()]

    def creer_comptes(self):
        """Créer des comptes sur les plateformes disponibles."""
        for plateforme in self.plateformes:
            try:
                plateforme.creer_compte()
                logger.info(f"Compte créé sur {plateforme.nom}")
            except Exception as e:
                logger.error(f"Échec de la création du compte sur {plateforme.nom}: {str(e)}")

    def mise_a_jour_profil(self, profil):
        """Mettre à jour le profil sur les plateformes disponibles."""
        for plateforme in self.plateformes:
            try:
                plateforme.mettre_a_jour_profil(profil)
                logger.info(f"Profil mis à jour sur {plateforme.nom}")
            except Exception as e:
                logger.error(f"Échec de la mise à jour du profil sur {plateforme.nom}: {str(e)}")

    def obtenir_statistiques(self):
        """Obtenir des statistiques sur les plateformes disponibles."""
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

    malt = Malt()
    cookies = malt.connexion()
    if cookies:
        malt.completer_profil(cookies)
    else:
        logger.error("Impossible de se connecter à Malt")
