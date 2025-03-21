import os
import json
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

class ConfigManager:
    """
    Gestionnaire de configuration pour le projet.
    """

    def __init__(
        self,
        config_file: str = "config.json",
        env_file: str = ".env"
    ):
        """
        Initialise le gestionnaire de configuration.

        Args:
            config_file: Fichier de configuration JSON
            env_file: Fichier de variables d'environnement
        """
        self.config_file = config_file
        self.env_file = env_file
        self.config = self._load_config()
        self._load_env()

    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return {}

    def _load_env(self):
        """Charge les variables d'environnement."""
        load_dotenv(self.env_file)

    def save_config(self):
        """Sauvegarde la configuration dans le fichier JSON."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.

        Args:
            key: Clé de configuration
            default: Valeur par défaut si la clé n'existe pas

        Returns:
            Valeur de configuration
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """
        Définit une valeur de configuration.

        Args:
            key: Clé de configuration
            value: Valeur à définir
        """
        self.config[key] = value
        self.save_config()

    def get_env(self, key: str, default: Any = None) -> Optional[str]:
        """
        Récupère une variable d'environnement.

        Args:
            key: Nom de la variable
            default: Valeur par défaut si la variable n'existe pas

        Returns:
            Valeur de la variable d'environnement
        """
        return os.getenv(key, default)

    def set_env(self, key: str, value: str):
        """
        Définit une variable d'environnement.

        Args:
            key: Nom de la variable
            value: Valeur à définir
        """
        os.environ[key] = value

    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """
        Récupère la configuration d'une plateforme spécifique.

        Args:
            platform_name: Nom de la plateforme

        Returns:
            Configuration de la plateforme
        """
        return self.config.get("platforms", {}).get(platform_name, {})

    def set_platform_config(self, platform_name: str, config: Dict[str, Any]):
        """
        Définit la configuration d'une plateforme spécifique.

        Args:
            platform_name: Nom de la plateforme
            config: Configuration à définir
        """
        if "platforms" not in self.config:
            self.config["platforms"] = {}
        self.config["platforms"][platform_name] = config
        self.save_config()

    def get_api_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration des APIs.

        Returns:
            Configuration des APIs
        """
        return self.config.get("api", {})

    def set_api_config(self, config: Dict[str, Any]):
        """
        Définit la configuration des APIs.

        Args:
            config: Configuration à définir
        """
        self.config["api"] = config
        self.save_config()

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration du logging.

        Returns:
            Configuration du logging
        """
        return self.config.get("logging", {})

    def set_logging_config(self, config: Dict[str, Any]):
        """
        Définit la configuration du logging.

        Args:
            config: Configuration à définir
        """
        self.config["logging"] = config
        self.save_config()

# Exemple d'utilisation
if __name__ == "__main__":
    config = ConfigManager()

    # Configuration des APIs
    config.set_api_config({
        "mistral": {
            "model": "mistral-tiny",
            "max_tokens": 1000
        }
    })

    # Configuration d'une plateforme
    config.set_platform_config("upwork", {
        "timeout": 30,
        "retry_count": 3
    })

    # Configuration du logging
    config.set_logging_config({
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "app.log"
    })

    # Récupération des configurations
    print("API Config:", config.get_api_config())
    print("Upwork Config:", config.get_platform_config("upwork"))
    print("Logging Config:", config.get_logging_config())