from extraction_CV_byApiOpenAi import process_cv
from logger import logger

if __name__ == "__main__":
    print("Début de l'exécution du script")
    try:
        # Chemins des fichiers
        # Chemin du fichier CV texte
        chemin_fichier_cv = "C:\\programmation\\Projets_python\\plateformes_Freelance\\freelancePlateformeCrud\\freelancePlateformeCrud\\data\\cv.txt"
        # Chemin du fichier JSON à générer
        chemin_fichier_json = "C:\\programmation\\Projets_python\\plateformes_Freelance\\freelancePlateformeCrud\\freelancePlateformeCrud\\data\\extract\\cv.json"

        print(f"Chemin du fichier CV : {chemin_fichier_cv}")
        print(f"Chemin du fichier JSON : {chemin_fichier_json}")

        # Traiter le CV
        process_cv(chemin_fichier_cv, chemin_fichier_json)

        print("Fin de l'exécution du script")
        logger.info("Programme terminé avec succès")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        logger.exception("Une erreur non gérée s'est produite")
