#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "
████████╗ ██████╗ ██╗  ██╗ █████╗
╚══██╔══╝██╔═══██╗██║ ██╔╝██╔══██╗
   ██║   ██║   ██║█████╔╝ ███████║
   ██║   ██║   ██║██╔═██╗ ██╔══██║
   ██║   ╚██████╔╝██║  ██╗██║  ██║
   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

        BUILD TOKA SUITE PRO
"

echo "[1/5] Vérification Python..."
python3 --version

echo "[2/5] Création environnement virtuel..."
python3 -m venv .venv

echo "[3/5] Installation dépendances..."
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements.txt

echo "[4/5] Compilation..."
python -m PyInstaller --noconfirm --onefile --windowed --name "TokaSuitePro" app.py

echo "[5/5] Terminé."
echo "Ton exécutable Linux est ici : dist/TokaSuitePro"
