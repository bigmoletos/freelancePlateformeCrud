import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

class CustomLogger:
    """
    Classe pour gérer les logs de manière centralisée avec rotation des fichiers.
    """

    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        level: int = logging.INFO
    ):
        """
        Initialise le logger personnalisé.

        Args:
            name: Nom du logger
            log_dir: Dossier pour stocker les fichiers de log
            max_bytes: Taille maximale d'un fichier de log
            backup_count: Nombre de fichiers de backup à conserver
            level: Niveau de log (INFO, DEBUG, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Création du dossier de logs si nécessaire
        os.makedirs(log_dir, exist_ok=True)

        # Format du log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Handler pour le fichier avec rotation
        log_file = os.path.join(
            log_dir,
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log un message de niveau INFO."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log un message de niveau DEBUG."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log un message de niveau WARNING."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log un message de niveau ERROR."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log un message de niveau CRITICAL."""
        self.logger.critical(message)

    def exception(self, message: str):
        """Log une exception avec le stack trace."""
        self.logger.exception(message)

    def get_logger(self) -> logging.Logger:
        """Retourne l'instance du logger."""
        return self.logger

# Exemple d'utilisation
if __name__ == "__main__":
    logger = CustomLogger("test_logger")
    logger.info("Test de log INFO")
    logger.debug("Test de log DEBUG")
    logger.warning("Test de log WARNING")
    logger.error("Test de log ERROR")
    try:
        raise Exception("Test d'exception")
    except Exception as e:
        logger.exception("Une exception s'est produite")