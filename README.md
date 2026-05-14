# Toka Suite Pro — Windows + Linux

Toka Suite Pro est une application locale tout-en-un avec une interface moderne, compatible Windows et Linux.

Elle détecte automatiquement la plateforme au lancement avec `platform.system()` puis adapte les chemins, les boutons et les commandes système.

## Nouveautés de cette version Pro

- Interface plus moderne avec dashboard, cartes, badges et thème violet/bleu
- Dashboard avec stats CPU, RAM, batterie et OS
- Nouveaux modules hors FiveM :
  - Dev tools
  - File tools
  - Web tools
  - Générateurs
  - Quick launcher
- Scripts Linux/Windows plus propres
- Dépendances compatibles Python 3.14
- README mis à jour

## Modules inclus

### Dashboard

Vue d'ensemble avec :

- OS détecté
- CPU
- RAM
- batterie
- raccourcis vers les outils

### Optimiseur

Actions sûres selon l'OS :

Windows :

- nettoyage fichiers temporaires
- ouverture du gestionnaire des tâches
- ouverture du nettoyage disque Windows
- ouverture du dossier données Toka

Linux :

- nettoyage `/tmp` côté utilisateur
- nettoyage cache pip
- ouverture du moniteur système si disponible
- ouverture du dossier données Toka

Aucune commande `sudo` n'est lancée.

### Notes privées

Bloc-notes local chiffré.

### To-do list

Ajout, coche et suppression de tâches.

### Coffre

Coffre local chiffré pour stocker :

- site/application
- identifiant/email
- mot de passe

Avec générateur de mot de passe fort.

### Site generator

Génère un site moderne avec :

- `index.html`
- `style.css`
- `script.js`

Le site est sauvegardé dans le dossier de données Toka.

### Dev tools

Outils développeur :

- SHA256 texte
- Base64 encode
- Base64 decode
- JSON formatter

### File tools

Outils fichiers :

- analyse d'un fichier par chemin
- taille en octets et MB
- SHA256 fichier
- date de modification
- nettoyage de nom de fichier

### Web tools

Outils web :

- URL encode
- URL decode
- recherche Google
- recherche DuckDuckGo
- bouton GitHub

### Générateurs

Génère localement :

- mot de passe fort
- token sécurisé
- pseudo stylé
- palette de couleurs HEX

### Quick launcher

Ajoute des raccourcis vers :

- sites web
- dossiers locaux
- fichiers locaux

## Dossiers de sauvegarde

Windows :

```txt
Documents/TokaSuite
```

Linux :

```txt
~/.local/share/TokaSuite
```

## Lancer sur Windows sans compiler

Double-clique sur :

```txt
run_windows.bat
```

Ou en terminal :

```bat
run_windows.bat
```

## Compiler le .exe Windows

```bat
build_windows.bat
```

Résultat :

```txt
dist\TokaSuitePro.exe
```

## Lancer sur Linux sans compiler

```bash
chmod +x run_linux.sh
./run_linux.sh
```

## Compiler l'exécutable Linux

```bash
chmod +x build_linux.sh
./build_linux.sh
```

Résultat :

```txt
dist/TokaSuitePro
```

## Ajouter au menu d'applications Linux

Après compilation :

```bash
chmod +x install_desktop.sh
./install_desktop.sh
```

## Dépendances Python

```txt
customtkinter>=5.2.2
psutil>=7.0.0
cryptography>=46.0.0
pyinstaller>=6.20.0
```

## Dépendances système Linux

Sur Arch / CachyOS :

```bash
sudo pacman -S python tk
```

Sur Debian / Ubuntu / Linux Mint :

```bash
sudo apt install python3 python3-venv python3-tk
```

## Erreur possible : libtk8.6.so

Si tu vois :

```txt
ImportError: libtk8.6.so: cannot open shared object file
```

Sur CachyOS / Arch :

```bash
sudo pacman -S tk
```

Puis :

```bash
rm -rf .venv
./run_linux.sh
```

## Sécurité

Les notes et mots de passe sont chiffrés localement avec `cryptography.Fernet`.

Le fichier de clé est stocké dans le dossier de données Toka :

```txt
vault.key
```

Ne supprime pas ce fichier si tu veux garder accès à tes données chiffrées.

## Important

L'application ne contient aucun module FiveM.

Elle ne fait pas :

- modification registre Windows
- commande sudo Linux
- suppression système dangereuse
- envoi de données en ligne

Tout est local, sauf les boutons qui ouvrent explicitement une recherche web ou une URL.
