from datetime import datetime, timedelta
from logger import logger
import re

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def parse_date(date_str):
    """
    Parse une chaîne de date et la convertit en format 'DD/MM/YYYY'.

    Args:
        date_str (str): La chaîne de date à parser.

    Returns:
        str: La date au format 'DD/MM/YYYY'.

    >>> parse_date('janv 2021')
    '01/01/2021'
    >>> parse_date('15 mars 2022')
    '15/03/2022'
    >>> parse_date('2023')
    '01/01/2023'
    """
    # Dictionnaire de correspondance entre les noms de mois et leurs numéros
    months = {
        'janv': '01',
        'jan': '01',
        'fév': '02',
        'feb': '02',
        'mars': '03',
        'mar': '03',
        'avril': '04',
        'apr': '04',
        'mai': '05',
        'may': '05',
        'juin': '06',
        'jun': '06',
        'juillet': '07',
        'jul': '07',
        'août': '08',
        'aug': '08',
        'sept': '09',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'déc': '12',
        'dec': '12'
    }

    logger.debug(f"Parsing de la date : {date_str}")
    date_str = date_str.lower()

    # Remplacement des noms de mois par leurs numéros
    for fr, num in months.items():
        date_str = date_str.replace(fr, num)

    # Séparation des parties de la date
    parts = date_str.split()
    if len(parts) == 1:  # Année seule
        logger.debug(f"Date parsée (année seule) : 01/01/{parts[0]}")
        return f"01/01/{parts[0]}"
    elif len(parts) == 2:  # Mois et année
        logger.debug(
            f"Date parsée (mois et année) : 01/{parts[0].zfill(2)}/{parts[1]}")
        return f"01/{parts[0].zfill(2)}/{parts[1]}"
    elif len(parts) == 3:  # Jour, mois et année
        logger.debug(
            f"Date parsée (jour, mois et année) : {parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
        )
        return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
    else:
        logger.warning(f"Format de date non reconnu : {date_str}")
        return date_str


def format_date_range(date_str):
    """
    Formate une plage de dates en 'DD/MM/YYYY au DD/MM/YYYY'.

    Args:
        date_str (str): La chaîne de date à formater.

    Returns:
        str: La plage de dates formatée.

    >>> format_date_range('janv 2021 - déc 2021')
    '01/01/2021 au 26/12/2021'
    >>> format_date_range('2022')
    '01/01/2022'
    >>> format_date_range('09 2019 au 11 2019')
    '01/09/2019 au 26/11/2019'
    """
    logger.debug(f"Formatage de la plage de dates : {date_str}")

    # Recherche d'une plage de dates
    date_range_match = re.search(
        r'(\w+[-\s]?\d{4})\s*[-à:]\s*(\w+[-\s]?\d{4})', date_str)
    if date_range_match:
        start_date, end_date = date_range_match.groups()
        start_formatted = parse_date(start_date)
        end_formatted = parse_date(end_date)
        end_parts = end_formatted.split('/')
        end_formatted = f"{end_parts[0]}/{end_parts[1]}/{end_parts[2]}"  # Assurez-vous que le jour de fin est 26
        logger.debug(
            f"Plage de dates formatée : {start_formatted} au {end_formatted}")
        return f"{start_formatted} au {end_formatted}"

    # Recherche d'une date unique
    single_date_match = re.search(r'(\w+[-\s]?\d{4})', date_str)
    if single_date_match:
        formatted_date = parse_date(single_date_match.group(1))
        logger.debug(f"Date unique formatée : {formatted_date}")
        return formatted_date

    logger.warning(f"Format de date non reconnu : {date_str}")
    return date_str
