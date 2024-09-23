import re
from logger import logger


def nettoyer_json(contenu):
    """Nettoie le contenu pour s'assurer qu'il s'agit d'un JSON valide."""
    logger.debug(f"Contenu avant nettoyage : {contenu}")
    # Supprimer tout texte avant le premier '{'
    contenu = re.sub(r'^[^{]*', '', contenu)
    # Supprimer tout texte après le dernier '}'
    contenu = re.sub(r'}[^}]*$', '}', contenu)
    logger.debug(f"Contenu après nettoyage : {contenu}")
    return contenu
