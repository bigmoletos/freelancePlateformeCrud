import os
import re
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

class DocManager:
    """
    Gestionnaire de documentation pour le projet.
    """

    def __init__(
        self,
        project_name: str,
        doc_dir: str = "docs",
        template_dir: str = "templates"
    ):
        """
        Initialise le gestionnaire de documentation.

        Args:
            project_name: Nom du projet
            doc_dir: Dossier pour la documentation
            template_dir: Dossier pour les templates
        """
        self.project_name = project_name
        self.doc_dir = doc_dir
        self.template_dir = template_dir
        self.setup_directories()

    def setup_directories(self):
        """Crée les dossiers nécessaires pour la documentation."""
        os.makedirs(self.doc_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)

    def generate_readme(self, description: str, requirements: List[str]):
        """
        Génère un fichier README.md pour le projet.

        Args:
            description: Description du projet
            requirements: Liste des prérequis
        """
        readme_content = f"""# {self.project_name}

{description}

## Prérequis

{chr(10).join(f"- {req}" for req in requirements)}

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py
```

## Structure du projet

```
{self.project_name}/
├── data/               # Données du projet
├── docs/              # Documentation
├── logs/              # Fichiers de log
├── outils/            # Outils utilitaires
├── profiles/          # Profils générés
├── test_results/      # Résultats des tests
└── requirements.txt   # Dépendances
```

## Configuration

Le fichier `.env` doit contenir les variables suivantes :

```env
# API Mistral
MISTRAL_API_KEY="votre_clé_api_mistral"
MISTRAL_API_LOGIN="votre_login"

# Identifiants des plateformes
PLATFORM_EMAIL="votre_email"
PLATFORM_PASSWORD="votre_password"
```

## Tests

Pour exécuter les tests :

```bash
python test_connections.py
```

## Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT.
"""

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

    def generate_api_doc(self, module_path: str):
        """
        Génère la documentation API à partir des docstrings.

        Args:
            module_path: Chemin du module à documenter
        """
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location("module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        api_doc = f"""# Documentation API - {self.project_name}

## Classes

"""

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                api_doc += f"### {name}\n\n"
                if obj.__doc__:
                    api_doc += f"{obj.__doc__}\n\n"

                api_doc += "#### Méthodes\n\n"
                for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                    if method.__doc__:
                        api_doc += f"##### {method_name}\n\n{method.__doc__}\n\n"

        with open(os.path.join(self.doc_dir, "api.md"), "w", encoding="utf-8") as f:
            f.write(api_doc)

    def generate_changelog(self, version: str, changes: List[str]):
        """
        Génère un fichier CHANGELOG.md.

        Args:
            version: Version du projet
            changes: Liste des changements
        """
        changelog_content = f"""# Changelog

## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### Ajouté
{chr(10).join(f"- {change}" for change in changes)}

"""

        changelog_path = os.path.join(self.doc_dir, "CHANGELOG.md")
        if os.path.exists(changelog_path):
            with open(changelog_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
                changelog_content += existing_content

        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(changelog_content)

    def generate_requirements_doc(self, requirements_file: str):
        """
        Génère la documentation des dépendances.

        Args:
            requirements_file: Chemin du fichier requirements.txt
        """
        with open(requirements_file, "r", encoding="utf-8") as f:
            requirements = f.readlines()

        doc_content = """# Dépendances du projet

## Liste des packages

"""

        for req in requirements:
            if req.strip() and not req.startswith("#"):
                doc_content += f"- {req.strip()}\n"

        with open(os.path.join(self.doc_dir, "requirements.md"), "w", encoding="utf-8") as f:
            f.write(doc_content)

# Exemple d'utilisation
if __name__ == "__main__":
    doc_manager = DocManager("FreelancePlatformManager")

    # Génération du README
    doc_manager.generate_readme(
        "Outil de gestion des comptes des plateformes de freelancing",
        [
            "Python 3.8+",
            "pip",
            "Chrome (pour Selenium)"
        ]
    )

    # Génération de la documentation API
    doc_manager.generate_api_doc("plateforme_freelance.py")

    # Génération du changelog
    doc_manager.generate_changelog(
        "1.0.0",
        [
            "Initialisation du projet",
            "Ajout de la gestion des plateformes",
            "Intégration de l'API Mistral"
        ]
    )

    # Génération de la documentation des dépendances
    doc_manager.generate_requirements_doc("requirements.txt")