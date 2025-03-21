import os
import json
import logging
import requests
from typing import Dict, List
from dotenv import load_dotenv
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlatformConnectionTester:
    """
    Classe pour tester les connexions aux différentes plateformes de freelancing.
    """

    def __init__(self):
        """Initialise le testeur avec les configurations nécessaires."""
        load_dotenv()
        self.platforms = self._load_platforms()
        self.test_results = []

    def _load_platforms(self) -> List[Dict]:
        """Charge la liste des plateformes depuis le fichier JSON."""
        try:
            with open('data/liste_plateforme.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des plateformes: {e}")
            return []

    def test_connection(self, platform: Dict) -> Dict:
        """
        Teste la connexion à une plateforme spécifique.

        Args:
            platform: Dictionnaire contenant les informations de la plateforme

        Returns:
            Dict: Résultat du test de connexion
        """
        platform_name = platform['nom']
        email = os.getenv(f"{platform_name.upper()}_EMAIL")
        password = os.getenv(f"{platform_name.upper()}_PASSWORD")

        if not email or not password:
            return {
                "platform": platform_name,
                "status": "error",
                "message": "Identifiants manquants",
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Simulation de la connexion (à adapter selon chaque plateforme)
            response = requests.get(
                platform['login_url'],
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            if response.status_code == 200:
                return {
                    "platform": platform_name,
                    "status": "success",
                    "message": "Connexion réussie",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "platform": platform_name,
                    "status": "error",
                    "message": f"Erreur de connexion (status code: {response.status_code})",
                    "timestamp": datetime.now().isoformat()
                }

        except requests.exceptions.RequestException as e:
            return {
                "platform": platform_name,
                "status": "error",
                "message": f"Erreur de connexion: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def run_tests(self):
        """Exécute les tests de connexion pour toutes les plateformes."""
        logger.info("Démarrage des tests de connexion...")

        for platform in self.platforms:
            result = self.test_connection(platform)
            self.test_results.append(result)

            if result["status"] == "success":
                logger.info(f"✓ {platform['nom']}: Connexion réussie")
            else:
                logger.error(f"✗ {platform['nom']}: {result['message']}")

        self._save_results()

    def _save_results(self):
        """Sauvegarde les résultats des tests."""
        try:
            os.makedirs('test_results', exist_ok=True)
            filename = f"test_results/connection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"Résultats sauvegardés dans {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")

def main():
    """Point d'entrée principal du programme de test."""
    try:
        tester = PlatformConnectionTester()
        tester.run_tests()
        logger.info("Tests de connexion terminés")
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {e}")

if __name__ == "__main__":
    main()