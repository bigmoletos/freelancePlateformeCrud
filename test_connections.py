### Script:
### [
###     "uv python test_connections.py"
### ]
### Dependencies:
### [
###     "selenium",
###     "outils"
### ]

"""
Module de test des connexions aux plateformes de freelancing.

Ce module permet de :
- Tester la connexion à chaque plateforme
- Vérifier la validité des identifiants
- Générer un rapport de test détaillé
- Logger les résultats des tests
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Import des outils personnalisés
from outils import CustomLogger, ConfigManager, DocManager

class PlatformConnectionTester:
    """
    Classe de test des connexions aux plateformes de freelancing.

    Cette classe permet de :
    - Tester la connexion à chaque plateforme
    - Vérifier la validité des identifiants
    - Générer des rapports de test
    - Gérer les erreurs de connexion
    """

    def __init__(self):
        """
        Initialise le testeur de connexions.

        Configure :
        - Le logger personnalisé
        - Le gestionnaire de configuration
        - Le gestionnaire de documentation
        - Le driver Selenium
        """
        # Initialisation des outils
        self.logger = CustomLogger("platform_tester")
        self.config = ConfigManager()
        self.doc_manager = DocManager("PlatformConnectionTester")

        # Chemin vers le répertoire du script
        self.script_dir = Path(__file__).parent.absolute()

        # Initialisation du driver
        self.driver = None
        self.test_results = []

        self.logger.info("Initialisation du PlatformConnectionTester terminée")

    def _init_selenium(self):
        """
        Initialise le driver Selenium pour les tests.

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
            json_path = self.script_dir / 'data' / 'liste_plateforme.json'
            self.logger.info(f"Tentative de chargement du fichier: {json_path}")

            if not json_path.exists():
                self.logger.error(f"Fichier non trouvé: {json_path}")
                return []

            with open(json_path, 'r', encoding='utf-8') as f:
                platforms = json.load(f)
                self.logger.info(f"Chargement de {len(platforms)} plateformes")
                return platforms
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des plateformes: {e}")
            return []

    def test_platform_connection(self, platform: Dict) -> Dict:
        """
        Teste la connexion à une plateforme spécifique.

        Args:
            platform: Dictionnaire contenant les informations de la plateforme

        Returns:
            Dict: Résultats du test avec statut et messages
        """
        platform_name = platform['nom']
        email = self.config.get_env(f"{platform_name.upper()}_EMAIL")
        password = self.config.get_env(f"{platform_name.upper()}_PASSWORD")

        result = {
            'platform': platform_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'message': '',
            'error': None
        }

        if not email or not password:
            result['message'] = "Identifiants manquants"
            self.logger.error(f"Identifiants manquants pour {platform_name}")
            return result

        try:
            self.logger.info(f"Test de connexion à {platform_name}")
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

            result['status'] = 'success'
            result['message'] = "Connexion réussie"
            self.logger.info(f"Test de connexion réussi pour {platform_name}")

        except TimeoutException:
            result['message'] = "Timeout lors de la connexion"
            result['error'] = "TimeoutException"
            self.logger.error(f"Timeout lors de la connexion à {platform_name}")
        except WebDriverException as e:
            result['message'] = f"Erreur Selenium: {str(e)}"
            result['error'] = "WebDriverException"
            self.logger.error(f"Erreur Selenium pour {platform_name}: {e}")
        except Exception as e:
            result['message'] = f"Erreur inattendue: {str(e)}"
            result['error'] = type(e).__name__
            self.logger.error(f"Erreur inattendue pour {platform_name}: {e}")

        return result

    def run_tests(self):
        """
        Exécute les tests de connexion sur toutes les plateformes.

        Cette méthode :
        1. Initialise Selenium
        2. Charge la liste des plateformes
        3. Teste chaque plateforme
        4. Génère un rapport de test
        5. Ferme proprement Selenium
        """
        try:
            self.logger.info("Démarrage des tests de connexion")
            self._init_selenium()

            platforms = self._load_platforms()
            if not platforms:
                self.logger.error("Aucune plateforme à tester")
                return

            for platform in platforms:
                result = self.test_platform_connection(platform)
                self.test_results.append(result)
                time.sleep(2)  # Pause entre les tests

            self._generate_test_report()

        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution des tests: {e}")
        finally:
            self._close_selenium()

    def _generate_test_report(self):
        """
        Génère un rapport de test détaillé.

        Le rapport inclut :
        - Un résumé des résultats
        - Les détails de chaque test
        - Les statistiques de succès/échec
        """
        try:
            # Création du dossier de résultats si nécessaire
            os.makedirs('test_results', exist_ok=True)

            # Calcul des statistiques
            total_tests = len(self.test_results)
            successful_tests = sum(1 for r in self.test_results if r['status'] == 'success')
            failed_tests = total_tests - successful_tests

            # Génération du rapport
            report = f"""# Rapport de test des connexions
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé
- Total des tests: {total_tests}
- Tests réussis: {successful_tests}
- Tests échoués: {failed_tests}
- Taux de succès: {(successful_tests/total_tests)*100:.1f}%

## Détails des tests

"""
            for result in self.test_results:
                report += f"""### {result['platform']}
- Statut: {result['status']}
- Message: {result['message']}
- Timestamp: {result['timestamp']}
"""
                if result['error']:
                    report += f"- Erreur: {result['error']}\n"
                report += "\n"

            # Sauvegarde du rapport
            filename = f"test_results/connection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)

            self.logger.info(f"Rapport de test généré: {filename}")

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {e}")

def main():
    """
    Point d'entrée principal du programme de test.

    Cette fonction :
    1. Initialise le testeur de connexions
    2. Exécute les tests
    3. Gère les erreurs globales
    """
    try:
        tester = PlatformConnectionTester()
        tester.run_tests()
        tester.logger.info("Tests de connexion terminés")
    except Exception as e:
        print(f"Erreur lors de l'exécution des tests: {e}")

if __name__ == "__main__":
    main()