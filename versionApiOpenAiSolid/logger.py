import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"),
              logging.StreamHandler()])
logger = logging.getLogger(__name__)
