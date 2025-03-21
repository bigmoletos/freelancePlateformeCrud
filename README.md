# Gestionnaire de Plateformes Freelance

## Description
Outil automatisé pour la gestion des profils freelances sur différentes plateformes. Utilise l'API Mistral pour générer des profils optimisés et Selenium pour l'automatisation des mises à jour.

## Fonctionnalités
- Connexion automatique aux plateformes de freelancing
- Génération de profils optimisés avec l'API Mistral
- Mise à jour automatique des profils
- Tests de connexion automatisés
- Génération de rapports détaillés
- Logging complet des opérations
- Gestion centralisée des configurations

## Prérequis
- Python 3.8+
- Chrome (pour Selenium)
- Comptes sur les plateformes de freelancing
- Clé API Mistral
- [uv](https://github.com/astral-sh/uv) (optionnel, pour une installation plus rapide)

## Installation

### Option 1 : Installation avec venv (environnement virtuel Python)

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

### Option 2 : Installation avec uv (gestionnaire de paquets rapide)

#### Option 2.1 : Installation avec environnement virtuel
1. Installer uv :
```bash
pip install uv
```

2. Créer un environnement virtuel :
```bash
uv venv
```

3. Installer les dépendances :
```bash
uv pip install -r requirements.txt
```

#### Option 2.2 : Installation système (sans environnement virtuel)
1. Installer uv :
```bash
pip install uv
```

2. Installer les dépendances :
```bash
# Windows (en tant qu'administrateur)
uv pip install -r requirements.txt --system

# Linux/Mac
sudo uv pip install -r requirements.txt --system
```

> **Note sur les permissions** :
> - Sur Windows, exécutez PowerShell en tant qu'administrateur
> - Sur Linux/Mac, utilisez `sudo` pour l'installation système
> - En cas d'erreur d'accès, préférez l'installation avec environnement virtuel (Option 2.1)

### Résolution des dépendances

En cas de conflit de dépendances (notamment avec pytest et pytest-selenium), vous pouvez :

1. Installer les dépendances une par une avec des versions compatibles :
```bash
uv pip install pytest==6.2.5
uv pip install pytest-selenium==4.0.0
uv pip install -r requirements.txt --system
```

2. Ou utiliser l'option `--no-deps` pour installer sans dépendances :
```bash
uv pip install pytest-selenium==4.0.0 --no-deps
uv pip install -r requirements.txt --system
```

3. Ou modifier le fichier requirements.txt pour spécifier les versions compatibles :
```txt
pytest==6.2.5
pytest-selenium==4.0.0
selenium>=4.0.0
python-dotenv>=0.19.0
mistralai>=0.0.10
requests>=2.26.0
```

### Vérification de l'installation

Après l'installation, vérifiez que tout fonctionne correctement :

```bash
# Vérifier la version de Python
python --version

# Vérifier les packages installés
pip list

# Tester l'import des modules principaux
python -c "import selenium; import mistralai; import pytest"
```

### Configuration

1. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos informations
```

## Structure du projet
```
freelance-platform-manager/
├── data/               # Données du projet
│   ├── cv.txt         # CV source
│   └── liste_plateforme.json  # Configuration des plateformes
├── docs/              # Documentation
├── logs/              # Fichiers de log
├── outils/            # Outils utilitaires
│   ├── logger.py      # Gestionnaire de logs
│   ├── doc_manager.py # Gestionnaire de documentation
│   └── config_manager.py # Gestionnaire de configuration
├── profiles/          # Profils générés
├── test_results/      # Résultats des tests
├── plateforme_freelance.py  # Script principal
├── test_connections.py      # Tests de connexion
└── requirements.txt   # Dépendances
```

## Configuration

### Variables d'environnement (.env)
```env
# API Mistral
MISTRAL_API_KEY="votre_clé_api_mistral"
MISTRAL_API_LOGIN="votre_login"

# Identifiants des plateformes
PLATFORM_EMAIL="votre_email"
PLATFORM_PASSWORD="votre_password"
```

### Configuration des plateformes (liste_plateforme.json)
```json
[
  {
    "nom": "Upwork",
    "login_url": "https://www.upwork.com/login",
    "profile_url": "https://www.upwork.com/freelancers/settings"
  }
]
```

## Utilisation

### Exécution des scripts avec uv

#### Script principal
```bash
uv run plateforme_freelance.py
```

#### Tests de connexion
```bash
uv run test_connections.py
```

#### Gestionnaire de configuration
```bash
uv run outils/config_manager.py
```

#### Gestionnaire de documentation
```bash
uv run outils/doc_manager.py
```

### Exécution avec venv (alternative)
```bash
# Script principal
python plateforme_freelance.py

# Tests de connexion
python test_connections.py

# Gestionnaire de configuration
python outils/config_manager.py

# Gestionnaire de documentation
python outils/doc_manager.py
```

## Logs et Rapports

### Logs
Les logs sont stockés dans le dossier `logs/` avec rotation automatique :
- Format : `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`
- Rotation : 10MB par fichier, 5 fichiers de backup

### Rapports de test
Les rapports de test sont générés dans `test_results/` au format Markdown :
- Résumé des tests
- Détails par plateforme
- Statistiques de succès/échec

## Développement

### Tests
```bash
# Tests unitaires
pytest

# Tests avec couverture
pytest --cov=.

# Tests Selenium
pytest test_connections.py
```

### Formatage du code
```bash
# Formatage avec Black
black .

# Tri des imports avec isort
isort .

# Vérification des types avec mypy
mypy .
```

### Documentation
```bash
# Génération de la documentation
sphinx-build -b html docs/source docs/build
```

## Contribution
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support
Pour toute question ou problème, ouvrir une issue sur GitHub.
