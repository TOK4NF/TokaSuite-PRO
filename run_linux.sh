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

        T O K A   S U I T E   P R O
"

echo "[1/4] Vérification Python..."
python3 --version

echo "[2/4] Création environnement virtuel..."
python3 -m venv .venv

echo "[3/4] Installation dépendances..."
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements.txt

echo "[4/4] Lancement..."
python app.py
