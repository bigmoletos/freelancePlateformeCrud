import unittest
from main import freelance_plateforme_CRUD_versionAPI_chatgpt


class TestLectureFichierCV(unittest.TestCase):

    def test_lire_fichier_cv(self):
        contenu = lire_fichier_cv("test_cv.txt")
        self.assertTrue(
            "prenom" in contenu
        )  # Vérifier que le fichier contient certaines informations attendues


if __name__ == '__main__':
    unittest.main()
