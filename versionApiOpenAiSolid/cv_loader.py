import json


class CVLoader:
    _instance = None
    _cv = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CVLoader, cls).__new__(cls)
            cls._instance._load_cv()
        return cls._instance

    def _load_cv(self):
        with open("data/extract/cv.json", "r",
                  encoding="utf-8") as fichier_json:
            self._cv = json.load(fichier_json)

    @property
    def cv(self):
        return self._cv
