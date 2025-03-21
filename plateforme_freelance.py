### Script:
### [
###     "uv python plateforme_freelance.py"
### ]
### Dependencies:
### [
###     "python-dotenv",
###     "requests",
###     "mistralai",
###     "selenium",
###     "outils"
### ]

"""
Module principal pour la gestion des plateformes de freelancing.

Ce module permet de :
- Se connecter aux différentes plateformes de freelancing
- Générer des profils optimisés avec l'API Mistral
- Mettre à jour automatiquement les profils
- Gérer les configurations et les logs
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import des outils personnalisés
from outils import CustomLogger, ConfigManager, DocManager

class FreelancePlatformManager:
    """
    Gestionnaire principal des plateformes de freelancing.

    Cette classe gère :
    - Les connexions aux plateformes
    - La génération de profils avec Mistral AI
    - La mise à jour automatique des profils
    - La gestion des configurations
    - Le logging des opérations
    """

    def __init__(self):
        """
        Initialise le gestionnaire avec les configurations nécessaires.

        Charge :
        - Les variables d'environnement
        - La configuration du projet
        - Le logger personnalisé
        - Les données des plateformes
        - Les données du CV
        """
        # Initialisation des outils
        self.logger = CustomLogger("freelance_platform")
        self.config = ConfigManager()
        self.doc_manager = DocManager("FreelancePlatformManager")

        # Chargement des configurations
        load_dotenv()
        self.mistral_api_key = self.config.get_env('MISTRAL_API_KEY')
        self.mistral_login = self.config.get_env('MISTRAL_API_LOGIN')

        # Initialisation du client Mistral
        self.client = MistralClient(api_key=self.mistral_api_key)

        # Chargement des données
        self.platforms = self._load_platforms()
        self.cv_data = self._load_cv()
        self.driver = None

        self.logger.info("Initialisation du FreelancePlatformManager terminée")

    def _load_platforms(self) -> List[Dict]:
        """
        Charge la liste des plateformes depuis le fichier JSON.

        Returns:
            List[Dict]: Liste des plateformes avec leurs configurations

        Raises:
            FileNotFoundError: Si le fichier de plateformes n'existe pas
            json.JSONDecodeError: Si le fichier JSON est malformé
        """
        try:
            with open('data/liste_plateforme.json', 'r', encoding='utf-8') as f:
                platforms = json.load(f)
                self.logger.info(f"Chargement de {len(platforms)} plateformes")
                return platforms
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des plateformes: {e}")
            return []

    def _load_cv(self) -> Dict:
        """
        Charge et parse le CV depuis le fichier texte.

        Returns:
            Dict: Données structurées du CV

        Raises:
            FileNotFoundError: Si le fichier CV n'existe pas
        """
        try:
            with open('data/cv.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                cv_data = self._parse_cv(content)
                self.logger.info("Chargement du CV réussi")
                return cv_data
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du CV: {e}")
            return {}

    def _parse_cv(self, content: str) -> Dict:
        """
        Parse le contenu du CV en dictionnaire structuré.

        Args:
            content: Contenu brut du CV

        Returns:
            Dict: CV structuré avec sections et données
        """
        cv_data = {}
        current_section = None

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                cv_data[key.strip()] = value.strip()
            elif line.isupper():
                current_section = line
                cv_data[current_section] = []
            elif current_section:
                cv_data[current_section].append(line)

        return cv_data

    def _init_selenium(self):
        """
        Initialise le driver Selenium pour l'automatisation web.

        Configure :
        - Le mode headless
        - Les options de sécurité
        - Les timeouts
        """
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
            self.logger.info("Initialisation de Selenium réussie")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de Selenium: {e}")
            raise

    def _close_selenium(self):
        """Ferme proprement le driver Selenium."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Fermeture de Selenium réussie")
            except Exception as e:
                self.logger.error(f"Erreur lors de la fermeture de Selenium: {e}")

    def login_to_platform(self, platform: Dict) -> bool:
        """
        Se connecte à une plateforme spécifique.

        Args:
            platform: Dictionnaire contenant les informations de la plateforme

        Returns:
            bool: True si la connexion est réussie, False sinon
        """
        platform_name = platform['nom']
        email = self.config.get_env(f"{platform_name.upper()}_EMAIL")
        password = self.config.get_env(f"{platform_name.upper()}_PASSWORD")

        if not email or not password:
            self.logger.error(f"Identifiants manquants pour {platform_name}")
            return False

        try:
            self.logger.info(f"Tentative de connexion à {platform_name}")
            self.driver.get(platform['login_url'])

            # Attendre que les champs de connexion soient présents
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = self.driver.find_element(By.NAME, "password")

            # Remplir les champs
            email_field.send_keys(email)
            password_field.send_keys(password)

            # Cliquer sur le bouton de connexion
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Attendre que la connexion soit réussie
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(platform['profile_url'])
            )

            self.logger.info(f"Connexion réussie à {platform_name}")
            return True

        except TimeoutException:
            self.logger.error(f"Timeout lors de la connexion à {platform_name}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion à {platform_name}: {e}")
            return False

    def generate_platform_profile(self, platform_name: str) -> Optional[str]:
        """
        Génère un profil optimisé pour une plateforme spécifique.

        Args:
            platform_name: Nom de la plateforme

        Returns:
            Optional[str]: Profil généré ou None en cas d'erreur
        """
        try:
            self.logger.info(f"Génération du profil pour {platform_name}")
            messages = [
                ChatMessage(
                    role="system",
                    content=f"Tu es un expert en création de profils freelances pour {platform_name}."
                ),
                ChatMessage(
                    role="user",
                    content=f"Crée un profil optimisé pour {platform_name} basé sur ce CV: {json.dumps(self.cv_data, indent=2)}"
                )
            ]

            response = self.client.chat(
                model="mistral-tiny",
                messages=messages
            )

            profile = response.choices[0].message.content
            self.logger.info(f"Profil généré avec succès pour {platform_name}")
            return profile

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du profil: {e}")
            return None

    def update_platform_profile(self, platform: Dict, profile: str) -> bool:
        """
        Met à jour le profil sur une plateforme spécifique.

        Args:
            platform: Dictionnaire contenant les informations de la plateforme
            profile: Texte du profil à mettre à jour

        Returns:
            bool: True si la mise à jour est réussie, False sinon
        """
        try:
            self.logger.info(f"Mise à jour du profil sur {platform['nom']}")
            self.driver.get(platform['profile_url'])

            # Attendre que le champ de description soit présent
            description_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "description"))
            )

            # Mettre à jour la description
            description_field.clear()
            description_field.send_keys(profile)

            # Sauvegarder les modifications
            save_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            save_button.click()

            # Attendre la confirmation
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )

            self.logger.info(f"Profil mis à jour avec succès sur {platform['nom']}")
            return True

        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du profil sur {platform['nom']}: {e}")
            return False

    def update_all_profiles(self):
        """
        Met à jour les profils sur toutes les plateformes.

        Cette méthode :
        1. Initialise Selenium
        2. Pour chaque plateforme :
           - Se connecte
           - Génère un profil optimisé
           - Met à jour le profil
        3. Ferme proprement Selenium
        """
        try:
            self.logger.info("Démarrage de la mise à jour des profils")
            self._init_selenium()

            for platform in self.platforms:
                self.logger.info(f"Traitement de la plateforme {platform['nom']}")

                # Connexion à la plateforme
                if not self.login_to_platform(platform):
                    continue

                # Génération du profil
                profile = self.generate_platform_profile(platform['nom'])
                if not profile:
                    continue

                # Mise à jour du profil
                if self.update_platform_profile(platform, profile):
                    self._save_profile(platform['nom'], profile)

        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des profils: {e}")
        finally:
            self._close_selenium()

    def _save_profile(self, platform_name: str, profile: str):
        """
        Sauvegarde le profil généré.

        Args:
            platform_name: Nom de la plateforme
            profile: Contenu du profil
        """
        try:
            os.makedirs('profiles', exist_ok=True)
            filename = f"profiles/{platform_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(profile)
            self.logger.info(f"Profil sauvegardé: {filename}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du profil: {e}")

def main():
    """
    Point d'entrée principal du programme.

    Cette fonction :
    1. Initialise le gestionnaire de plateformes
    2. Met à jour tous les profils
    3. Gère les erreurs globales
    """
    try:
        manager = FreelancePlatformManager()
        manager.update_all_profiles()
        manager.logger.info("Mise à jour des profils terminée avec succès")
    except Exception as e:
        print(f"Erreur lors de l'exécution du programme: {e}")

if __name__ == "__main__":
    main()