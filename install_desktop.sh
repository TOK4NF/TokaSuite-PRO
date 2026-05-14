#!/usr/bin/env bash
cd "$(dirname "$0")"

APP_PATH="$(pwd)/dist/TokaSuitePro"
DESKTOP_FILE="$HOME/.local/share/applications/tokasuitepro.desktop"

if [ ! -f "$APP_PATH" ]; then
  echo "Erreur : compile d'abord avec ./build_linux.sh"
  exit 1
fi

mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Toka Suite Pro
Comment=Application Windows/Linux tout-en-un de Toka
Exec=$APP_PATH
Terminal=false
Type=Application
Categories=Utility;Development;
EOF

chmod +x "$DESKTOP_FILE"
echo "Raccourci installé : $DESKTOP_FILE"
