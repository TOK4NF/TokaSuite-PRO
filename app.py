
import os
import sys
import json
import shutil
import secrets
import string
import tempfile
import platform
import subprocess
import hashlib
import base64
import urllib.parse
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
import psutil
from cryptography.fernet import Fernet, InvalidToken


APP_NAME = "Toka Suite Pro"

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == "windows"
IS_LINUX = SYSTEM == "linux"

ASCII_ART = r"""
████████╗ ██████╗ ██╗  ██╗ █████╗
╚══██╔══╝██╔═══██╗██║ ██╔╝██╔══██╗
   ██║   ██║   ██║█████╔╝ ███████║
   ██║   ██║   ██║██╔═██╗ ██╔══██║
   ██║   ╚██████╔╝██║  ██╗██║  ██║
   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

        T O K A   S U I T E   P R O
"""


def get_data_dir() -> Path:
    if IS_WINDOWS:
        return Path.home() / "Documents" / "TokaSuite"
    if IS_LINUX:
        return Path.home() / ".local" / "share" / "TokaSuite"
    return Path.home() / "TokaSuite"


DATA_DIR = get_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)

KEY_FILE = DATA_DIR / "vault.key"
NOTES_FILE = DATA_DIR / "secure_notes.bin"
TODO_FILE = DATA_DIR / "todo.json"
PASSWORDS_FILE = DATA_DIR / "passwords.bin"
QUICKLINKS_FILE = DATA_DIR / "quicklinks.json"
BOOKMARKS_FILE = DATA_DIR / "bookmarks.json"


def safe_chmod(path: Path, mode: int):
    try:
        if not IS_WINDOWS:
            os.chmod(path, mode)
    except Exception:
        pass


def load_or_create_key():
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    safe_chmod(KEY_FILE, 0o600)
    return key


FERNET = Fernet(load_or_create_key())


def encrypt_json(data, path: Path):
    raw = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    path.write_bytes(FERNET.encrypt(raw))
    safe_chmod(path, 0o600)


def decrypt_json(path: Path, default):
    if not path.exists():
        return default
    try:
        raw = FERNET.decrypt(path.read_bytes())
        return json.loads(raw.decode("utf-8"))
    except (InvalidToken, json.JSONDecodeError):
        return default


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def open_file_manager(path: Path):
    try:
        if IS_WINDOWS:
            os.startfile(path)
        elif IS_LINUX:
            subprocess.Popen(["xdg-open", str(path)])
        else:
            subprocess.Popen(["open", str(path)])
    except Exception:
        pass


def open_url(url: str):
    try:
        if IS_WINDOWS:
            os.startfile(url)
        elif IS_LINUX:
            subprocess.Popen(["xdg-open", url])
        else:
            subprocess.Popen(["open", url])
    except Exception:
        pass


class TokaSuite(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.os_label = "Windows" if IS_WINDOWS else "Linux" if IS_LINUX else platform.system()
        self.accent = "#7C3AED"
        self.accent_2 = "#06B6D4"
        self.bg = "#050510"
        self.panel = "#0D1020"
        self.card_bg = "#12162A"

        self.title(f"{APP_NAME} - {self.os_label}")
        self.geometry("1320x800")
        self.minsize(1120, 700)
        self.configure(fg_color=self.bg)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=292, corner_radius=0, fg_color="#090B17")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)

        self.logo_box = ctk.CTkFrame(self.sidebar, corner_radius=24, fg_color="#10142A", border_width=1, border_color="#262B55")
        self.logo_box.grid(row=0, column=0, padx=16, pady=(18, 12), sticky="ew")
        self.logo_box.grid_columnconfigure(0, weight=1)

        self.logo = ctk.CTkLabel(
            self.logo_box,
            text=ASCII_ART,
            font=ctk.CTkFont(family="monospace", size=10, weight="bold"),
            justify="left",
            text_color="#F4F4FF"
        )
        self.logo.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        self.detected_label = ctk.CTkLabel(
            self.logo_box,
            text=f"● OS détecté : {self.os_label}",
            text_color="#8BDBFF",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.detected_label.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

        self.buttons = {}
        menus = [
            ("dashboard", "🏠  Dashboard"),
            ("optimizer", "🚀  Optimiseur"),
            ("notes", "🔐  Notes privées"),
            ("todo", "✅  To-do"),
            ("passwords", "🛡️  Coffre"),
            ("sitegen", "🌐  Site generator"),
            ("devtools", "🧰  Dev tools"),
            ("files", "📁  File tools"),
            ("webtools", "🔗  Web tools"),
            ("randomizer", "🎲  Générateurs"),
            ("quicklinks", "⚡  Quick launcher"),
            ("settings", "⚙️  Infos système"),
        ]

        for i, (key, label) in enumerate(menus, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                height=42,
                corner_radius=15,
                anchor="w",
                fg_color="#12162A",
                hover_color="#1F2550",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda k=key: self.show_page(k)
            )
            btn.grid(row=i, column=0, padx=18, pady=4, sticky="ew")
            self.buttons[key] = btn

        self.footer = ctk.CTkLabel(
            self.sidebar,
            text="Cross-platform • Local • Chiffré",
            text_color="gray70",
            font=ctk.CTkFont(size=12)
        )
        self.footer.grid(row=21, column=0, padx=18, pady=16, sticky="s")

        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color=self.bg)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self.container, height=110, fg_color=self.bg)
        self.header.grid(row=0, column=0, sticky="ew", padx=34, pady=(26, 4))
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header,
            text="Centre de contrôle moderne pour Windows et Linux.",
            text_color="#AEB7D8",
            font=ctk.CTkFont(size=15)
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.top_badge = ctk.CTkLabel(
            self.header,
            text=f"  {self.os_label}  •  {datetime.now().strftime('%d/%m/%Y')}  ",
            fg_color="#12162A",
            corner_radius=999,
            text_color="#E8EAFF",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.top_badge.grid(row=0, column=1, padx=8, sticky="e")

        self.page = ctk.CTkFrame(self.container, fg_color=self.bg)
        self.page.grid(row=1, column=0, sticky="nsew", padx=34, pady=20)
        self.page.grid_columnconfigure(0, weight=1)
        self.page.grid_rowconfigure(0, weight=1)

        self.show_page("dashboard")

    def clear_page(self):
        for child in self.page.winfo_children():
            child.destroy()

    def show_page(self, name):
        titles = {
            "dashboard": ("Dashboard", f"Toka Suite Pro a détecté automatiquement : {self.os_label}."),
            "optimizer": ("Optimiseur", "Nettoyage safe, stats système et raccourcis adaptés à ton OS."),
            "notes": ("Notes privées", "Notes locales chiffrées avec sauvegarde simple."),
            "todo": ("To-do list", "Gestion simple de tes tâches."),
            "passwords": ("Coffre", "Mots de passe chiffrés + générateur sécurisé."),
            "sitegen": ("Site generator", "Génère un mini-site moderne en HTML/CSS/JS."),
            "devtools": ("Dev tools", "Hash, Base64, JSON formatter et outils texte."),
            "files": ("File tools", "Analyse de fichiers, calcul SHA256 et nettoyage de nom."),
            "webtools": ("Web tools", "Encodeur URL, décodeur URL et liens rapides."),
            "randomizer": ("Générateurs", "Mots de passe, tokens, UUID-like, pseudo et palettes."),
            "quicklinks": ("Quick launcher", "Tes raccourcis locaux ou web dans un seul menu."),
            "settings": ("Infos système", "Détails de la plateforme et chemins utilisés."),
        }

        self.title_label.configure(text=titles[name][0])
        self.subtitle_label.configure(text=titles[name][1])
        self.clear_page()

        for k, b in self.buttons.items():
            b.configure(fg_color=(self.accent if k == name else "#12162A"))

        getattr(self, f"page_{name}")()

    def card(self, parent, title, subtitle=None):
        frame = ctk.CTkFrame(parent, corner_radius=26, fg_color=self.card_bg, border_width=1, border_color="#262B55")
        frame.grid_columnconfigure(0, weight=1)
        label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=21, weight="bold"), text_color="#FFFFFF")
        label.grid(row=0, column=0, padx=24, pady=(20, 0), sticky="w")
        if subtitle:
            sub = ctk.CTkLabel(frame, text=subtitle, text_color="#AEB7D8", wraplength=850, justify="left")
            sub.grid(row=1, column=0, padx=24, pady=(4, 12), sticky="w")
        return frame

    def small_stat(self, parent, title, value, row, col):
        frame = ctk.CTkFrame(parent, corner_radius=22, fg_color="#0F1327", border_width=1, border_color="#22284D")
        frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(frame, text=title, text_color="#AEB7D8", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=18, pady=(15, 2))
        ctk.CTkLabel(frame, text=value, text_color="#FFFFFF", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=18, pady=(0, 16))
        return frame

    def page_dashboard(self):
        self.page.grid_columnconfigure((0, 1, 2), weight=1)
        self.page.grid_rowconfigure((0, 1, 2), weight=1)

        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.25)
        disk_path = str(Path.home().anchor if IS_WINDOWS else Path.home())
        disk = psutil.disk_usage(disk_path)
        battery = psutil.sensors_battery()
        battery_text = "N/A" if battery is None else f"{int(battery.percent)}%"

        hero = ctk.CTkFrame(self.page, corner_radius=30, fg_color="#10142A", border_width=1, border_color="#303775")
        hero.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        hero.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hero, text="⚡ Bienvenue dans Toka Suite Pro", font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, padx=26, pady=(24, 4), sticky="w")
        ctk.CTkLabel(hero, text="Un hub local avec outils système, sécurité, dev, fichiers, web et productivité.", text_color="#AEB7D8", font=ctk.CTkFont(size=15)).grid(row=1, column=0, padx=26, pady=(0, 20), sticky="w")

        stats = ctk.CTkFrame(hero, fg_color="transparent")
        stats.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.small_stat(stats, "OS", self.os_label, 0, 0)
        self.small_stat(stats, "CPU", f"{cpu}%", 0, 1)
        self.small_stat(stats, "RAM", f"{ram.percent}%", 0, 2)
        self.small_stat(stats, "Batterie", battery_text, 0, 3)

        cards = [
            ("🧰 Dev tools", "Hash SHA256, Base64, JSON formatter, nettoyage texte.", "devtools"),
            ("📁 File tools", "Analyse un fichier, calcule son hash et sa taille.", "files"),
            ("🔗 Web tools", "Encode/décode des URL et ouvre des recherches rapides.", "webtools"),
            ("🎲 Générateurs", "Tokens, pseudos, mots de passe et couleurs.", "randomizer"),
            ("⚡ Quick launcher", "Ajoute tes liens et dossiers favoris.", "quicklinks"),
            ("🛡️ Coffre chiffré", "Stocke tes identifiants localement.", "passwords"),
        ]

        for i, (title, sub, page) in enumerate(cards):
            frame = self.card(self.page, title, sub)
            frame.grid(row=1 + i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            ctk.CTkButton(frame, text="Ouvrir", height=36, corner_radius=14, command=lambda p=page: self.show_page(p)).grid(row=2, column=0, padx=24, pady=(0, 20), sticky="ew")

    def page_optimizer(self):
        self.page.grid_columnconfigure((0, 1), weight=1)

        sys_card = self.card(self.page, "Statut système", f"Infos rapides sur ton système {self.os_label}.")
        sys_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory()
        disk_path = str(Path.home().anchor if IS_WINDOWS else Path.home())
        disk = psutil.disk_usage(disk_path)

        info = (
            f"Système : {platform.system()} {platform.release()}\n"
            f"Machine : {platform.machine()}\n"
            f"CPU : {cpu}%\n"
            f"RAM : {ram.percent}% utilisée ({round(ram.used/1024**3, 2)} Go / {round(ram.total/1024**3, 2)} Go)\n"
            f"Disque analysé : {disk_path}\n"
            f"Espace utilisé : {disk.percent}%\n"
            f"Données Toka Suite : {DATA_DIR}"
        )
        ctk.CTkLabel(sys_card, text=info, justify="left", font=ctk.CTkFont(size=15)).grid(row=2, column=0, padx=24, pady=18, sticky="w")

        actions = self.card(self.page, "Actions rapides", "Actions sûres : pas de modification système dangereuse.")
        actions.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.opt_result = ctk.CTkTextbox(actions, height=300, corner_radius=16)
        self.opt_result.grid(row=8, column=0, padx=24, pady=16, sticky="ew")
        self.opt_result.insert("end", f"Mode {self.os_label} actif.\nClique sur une action pour commencer.\n")

        ctk.CTkButton(actions, text="Nettoyer fichiers temporaires", height=42, command=self.clean_temp).grid(row=2, column=0, padx=24, pady=(15, 8), sticky="ew")
        ctk.CTkButton(actions, text="Ouvrir dossier données Toka", height=42, command=lambda: open_file_manager(DATA_DIR)).grid(row=3, column=0, padx=24, pady=8, sticky="ew")

        if IS_WINDOWS:
            ctk.CTkButton(actions, text="Ouvrir gestionnaire des tâches", height=42, command=self.open_task_manager).grid(row=4, column=0, padx=24, pady=8, sticky="ew")
            ctk.CTkButton(actions, text="Ouvrir nettoyage disque Windows", height=42, command=self.open_disk_cleanup).grid(row=5, column=0, padx=24, pady=8, sticky="ew")
        elif IS_LINUX:
            ctk.CTkButton(actions, text="Nettoyer cache pip", height=42, command=self.clean_pip_cache).grid(row=4, column=0, padx=24, pady=8, sticky="ew")
            ctk.CTkButton(actions, text="Ouvrir moniteur système", height=42, command=self.open_linux_monitor).grid(row=5, column=0, padx=24, pady=8, sticky="ew")

    def write_opt(self, text):
        self.opt_result.delete("1.0", "end")
        self.opt_result.insert("end", text)

    def clean_temp(self):
        temp = Path(tempfile.gettempdir())
        removed = 0
        failed = 0
        for item in temp.iterdir():
            try:
                if IS_LINUX:
                    try:
                        if item.owner() != os.environ.get("USER"):
                            continue
                    except Exception:
                        pass
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
                removed += 1
            except Exception:
                failed += 1
        self.write_opt(f"Nettoyage terminé.\nSystème : {self.os_label}\nÉléments traités : {removed}\nIgnorés/verrouillés : {failed}\nDossier : {temp}")

    def open_task_manager(self):
        try:
            subprocess.Popen("taskmgr")
        except Exception as e:
            self.write_opt(f"Impossible d'ouvrir le gestionnaire des tâches : {e}")

    def open_disk_cleanup(self):
        try:
            subprocess.Popen("cleanmgr")
        except Exception as e:
            self.write_opt(f"Impossible d'ouvrir cleanmgr : {e}")

    def clean_pip_cache(self):
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True, text=True, timeout=60)
            self.write_opt((result.stdout or "") + "\n" + (result.stderr or ""))
        except Exception as e:
            self.write_opt(f"Impossible de nettoyer le cache pip : {e}")

    def open_linux_monitor(self):
        commands = [["plasma-systemmonitor"], ["gnome-system-monitor"], ["ksysguard"], ["xfce4-taskmanager"], ["mate-system-monitor"], ["konsole", "-e", "htop"], ["xterm", "-e", "htop"]]
        for cmd in commands:
            if shutil.which(cmd[0]):
                subprocess.Popen(cmd)
                return
        self.write_opt("Aucun moniteur système trouvé. Installe htop, gnome-system-monitor ou plasma-systemmonitor.")

    def page_notes(self):
        self.page.grid_columnconfigure(0, weight=1)
        self.page.grid_rowconfigure(0, weight=1)

        frame = self.card(self.page, "Bloc-notes sécurisé", "Sauvegarde chiffrée quand tu cliques sur enregistrer.")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(2, weight=1)

        self.notes_box = ctk.CTkTextbox(frame, corner_radius=16, font=ctk.CTkFont(size=15))
        self.notes_box.grid(row=2, column=0, padx=24, pady=15, sticky="nsew")
        notes = decrypt_json(NOTES_FILE, {"text": ""}).get("text", "")
        self.notes_box.insert("end", notes)

        ctk.CTkButton(frame, text="Enregistrer les notes", height=42, command=self.save_notes).grid(row=3, column=0, padx=24, pady=(0, 18), sticky="ew")
        self.notes_status = ctk.CTkLabel(frame, text="")
        self.notes_status.grid(row=4, column=0, padx=24, pady=(0, 14), sticky="w")

    def save_notes(self):
        text = self.notes_box.get("1.0", "end").strip()
        encrypt_json({"text": text, "updated": datetime.now().isoformat()}, NOTES_FILE)
        self.notes_status.configure(text="✅ Notes enregistrées et chiffrées.")

    def page_todo(self):
        self.page.grid_columnconfigure(0, weight=1)
        self.page.grid_rowconfigure(0, weight=1)

        frame = self.card(self.page, "Mes tâches", "Ajoute, coche et supprime tes tâches.")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.grid(row=2, column=0, padx=24, pady=12, sticky="ew")
        row.grid_columnconfigure(0, weight=1)

        self.todo_entry = ctk.CTkEntry(row, height=42, placeholder_text="Nouvelle tâche...")
        self.todo_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkButton(row, text="Ajouter", height=42, width=120, command=self.add_todo).grid(row=0, column=1)

        self.todo_list_frame = ctk.CTkScrollableFrame(frame, height=390, corner_radius=16)
        self.todo_list_frame.grid(row=3, column=0, padx=24, pady=(5, 20), sticky="nsew")
        self.todo_data = load_json(TODO_FILE, [])
        self.refresh_todos()

    def refresh_todos(self):
        for child in self.todo_list_frame.winfo_children():
            child.destroy()
        for i, item in enumerate(self.todo_data):
            row = ctk.CTkFrame(self.todo_list_frame, corner_radius=14, fg_color="#1A1D2A")
            row.pack(fill="x", pady=6, padx=4)

            var = ctk.BooleanVar(value=item.get("done", False))
            chk = ctk.CTkCheckBox(row, text=item["text"], variable=var, command=lambda idx=i, v=var: self.toggle_todo(idx, v.get()))
            chk.pack(side="left", padx=14, pady=12)

            del_btn = ctk.CTkButton(row, text="Supprimer", width=100, fg_color="#7A1F2A", hover_color="#9E2B36", command=lambda idx=i: self.delete_todo(idx))
            del_btn.pack(side="right", padx=10, pady=8)

    def add_todo(self):
        text = self.todo_entry.get().strip()
        if not text:
            return
        self.todo_data.append({"text": text, "done": False})
        save_json(TODO_FILE, self.todo_data)
        self.todo_entry.delete(0, "end")
        self.refresh_todos()

    def toggle_todo(self, idx, done):
        self.todo_data[idx]["done"] = done
        save_json(TODO_FILE, self.todo_data)

    def delete_todo(self, idx):
        self.todo_data.pop(idx)
        save_json(TODO_FILE, self.todo_data)
        self.refresh_todos()

    def page_passwords(self):
        self.page.grid_columnconfigure((0, 1), weight=1)

        form = self.card(self.page, "Ajouter un mot de passe", "Les mots de passe sont sauvegardés dans un fichier chiffré.")
        form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.pass_site = ctk.CTkEntry(form, height=42, placeholder_text="Site / application")
        self.pass_user = ctk.CTkEntry(form, height=42, placeholder_text="Identifiant / email")
        self.pass_value = ctk.CTkEntry(form, height=42, placeholder_text="Mot de passe")
        self.pass_site.grid(row=2, column=0, padx=24, pady=8, sticky="ew")
        self.pass_user.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        self.pass_value.grid(row=4, column=0, padx=24, pady=8, sticky="ew")

        ctk.CTkButton(form, text="Générer un mot de passe", height=42, command=self.generate_password).grid(row=5, column=0, padx=24, pady=8, sticky="ew")
        ctk.CTkButton(form, text="Enregistrer", height=42, command=self.save_password_entry).grid(row=6, column=0, padx=24, pady=8, sticky="ew")

        list_card = self.card(self.page, "Coffre", "Clique sur afficher pour voir les mots de passe.")
        list_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_card.grid_rowconfigure(2, weight=1)

        self.pass_list = ctk.CTkTextbox(list_card, height=450, corner_radius=16)
        self.pass_list.grid(row=2, column=0, padx=24, pady=15, sticky="nsew")
        ctk.CTkButton(list_card, text="Afficher / rafraîchir", height=42, command=self.refresh_passwords).grid(row=3, column=0, padx=24, pady=(0, 18), sticky="ew")

    def get_password_data(self):
        return decrypt_json(PASSWORDS_FILE, [])

    def save_password_data(self, data):
        encrypt_json(data, PASSWORDS_FILE)

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}"
        pwd = "".join(secrets.choice(alphabet) for _ in range(24))
        self.pass_value.delete(0, "end")
        self.pass_value.insert(0, pwd)

    def save_password_entry(self):
        site = self.pass_site.get().strip()
        user = self.pass_user.get().strip()
        pwd = self.pass_value.get().strip()
        if not site or not pwd:
            return
        data = self.get_password_data()
        data.append({"site": site, "user": user, "password": pwd, "created": datetime.now().strftime("%d/%m/%Y %H:%M")})
        self.save_password_data(data)
        self.pass_site.delete(0, "end")
        self.pass_user.delete(0, "end")
        self.pass_value.delete(0, "end")
        self.refresh_passwords()

    def refresh_passwords(self):
        data = self.get_password_data()
        self.pass_list.delete("1.0", "end")
        if not data:
            self.pass_list.insert("end", "Aucun mot de passe enregistré.")
            return
        for i, item in enumerate(data, 1):
            self.pass_list.insert("end", f"{i}. {item['site']}\nIdentifiant : {item.get('user','')}\nMot de passe : {item['password']}\nCréé : {item.get('created','')}\n\n")

    def page_sitegen(self):
        self.page.grid_columnconfigure(0, weight=1)

        frame = self.card(self.page, "Générateur de site", "Génère un site moderne dans un dossier avec index.html, style.css et script.js.")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.web_name = ctk.CTkEntry(frame, height=42, placeholder_text="Nom du site")
        self.web_desc = ctk.CTkEntry(frame, height=42, placeholder_text="Description / slogan")
        self.web_button = ctk.CTkEntry(frame, height=42, placeholder_text="Texte du bouton principal")

        self.web_name.grid(row=2, column=0, padx=24, pady=8, sticky="ew")
        self.web_desc.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        self.web_button.grid(row=4, column=0, padx=24, pady=8, sticky="ew")

        self.web_result = ctk.CTkLabel(frame, text="", text_color="gray70")
        self.web_result.grid(row=6, column=0, padx=24, pady=14, sticky="w")

        ctk.CTkButton(frame, text="Générer le site", height=42, command=self.generate_site).grid(row=5, column=0, padx=24, pady=12, sticky="ew")

    def generate_site(self):
        name = self.web_name.get().strip() or "TokaSite"
        desc = self.web_desc.get().strip() or "Un site moderne généré avec Toka Suite Pro."
        button = self.web_button.get().strip() or "Commencer"

        folder = DATA_DIR / "GeneratedSites" / name.replace(" ", "_")
        folder.mkdir(parents=True, exist_ok=True)

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="glow"></div>
  <nav>
    <h1>{name}</h1>
    <a href="#features">Fonctionnalités</a>
  </nav>
  <main>
    <section class="hero">
      <pre>{ASCII_ART}</pre>
      <p class="tag">Site généré avec Toka Suite Pro</p>
      <h2>{desc}</h2>
      <button>{button}</button>
    </section>
    <section id="features" class="cards">
      <article>⚡ Rapide</article>
      <article>🖤 Moderne</article>
      <article>🖥️ Cross-platform</article>
    </section>
  </main>
  <script src="script.js"></script>
</body>
</html>"""

        css = """*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:#050509;color:white;min-height:100vh;overflow-x:hidden}.glow{position:fixed;inset:0;background:radial-gradient(circle at top,#7c3aed88,transparent 35%),radial-gradient(circle at bottom right,#06b6d455,transparent 30%);pointer-events:none}nav{position:relative;display:flex;justify-content:space-between;align-items:center;padding:28px 8vw}nav h1{font-size:26px;letter-spacing:-1px}nav a{color:#ddd;text-decoration:none}.hero{position:relative;min-height:70vh;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;padding:0 8vw}pre{font-size:12px;color:#b8a6ff;margin:0 0 15px}.tag{padding:10px 16px;border:1px solid #ffffff22;border-radius:999px;color:#bbb;background:#ffffff08}.hero h2{max-width:900px;font-size:clamp(44px,8vw,96px);line-height:.95;margin:25px 0;letter-spacing:-5px}button{border:0;border-radius:18px;padding:16px 24px;font-weight:800;background:white;color:#050509;cursor:pointer;box-shadow:0 20px 80px #ffffff22}.cards{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:0 8vw 80px}.cards article{background:#ffffff0c;border:1px solid #ffffff15;border-radius:28px;padding:35px;font-size:28px;font-weight:800;backdrop-filter:blur(20px)}@media(max-width:800px){.cards{grid-template-columns:1fr}.hero h2{letter-spacing:-2px}pre{font-size:9px}}"""
        js = """document.querySelector('button').addEventListener('click',()=>{alert('Bienvenue sur le site Toka !')})"""

        (folder / "index.html").write_text(html, encoding="utf-8")
        (folder / "style.css").write_text(css, encoding="utf-8")
        (folder / "script.js").write_text(js, encoding="utf-8")

        self.web_result.configure(text=f"✅ Site généré ici : {folder}")

    def page_devtools(self):
        self.page.grid_columnconfigure((0, 1), weight=1)

        hash_card = self.card(self.page, "Hash / Base64", "Transforme du texte rapidement.")
        hash_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.dev_input = ctk.CTkTextbox(hash_card, height=160, corner_radius=16)
        self.dev_input.grid(row=2, column=0, padx=24, pady=10, sticky="ew")
        self.dev_output = ctk.CTkTextbox(hash_card, height=220, corner_radius=16)
        self.dev_output.grid(row=5, column=0, padx=24, pady=10, sticky="ew")

        row = ctk.CTkFrame(hash_card, fg_color="transparent")
        row.grid(row=3, column=0, padx=24, pady=4, sticky="ew")
        row.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(row, text="SHA256", command=self.dev_sha256).grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkButton(row, text="Base64 encode", command=self.dev_b64_encode).grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkButton(row, text="Base64 decode", command=self.dev_b64_decode).grid(row=0, column=2, padx=4, sticky="ew")

        json_card = self.card(self.page, "JSON formatter", "Colle un JSON compact pour le rendre lisible.")
        json_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.json_input = ctk.CTkTextbox(json_card, height=220, corner_radius=16)
        self.json_input.grid(row=2, column=0, padx=24, pady=10, sticky="ew")
        ctk.CTkButton(json_card, text="Formater JSON", height=42, command=self.format_json).grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        self.json_output = ctk.CTkTextbox(json_card, height=220, corner_radius=16)
        self.json_output.grid(row=4, column=0, padx=24, pady=10, sticky="ew")

    def _get_text(self, box):
        return box.get("1.0", "end").strip()

    def _set_text(self, box, text):
        box.delete("1.0", "end")
        box.insert("end", text)

    def dev_sha256(self):
        txt = self._get_text(self.dev_input)
        self._set_text(self.dev_output, hashlib.sha256(txt.encode("utf-8")).hexdigest())

    def dev_b64_encode(self):
        txt = self._get_text(self.dev_input)
        self._set_text(self.dev_output, base64.b64encode(txt.encode("utf-8")).decode("utf-8"))

    def dev_b64_decode(self):
        txt = self._get_text(self.dev_input)
        try:
            self._set_text(self.dev_output, base64.b64decode(txt.encode("utf-8")).decode("utf-8"))
        except Exception as e:
            self._set_text(self.dev_output, f"Erreur Base64 : {e}")

    def format_json(self):
        txt = self._get_text(self.json_input)
        try:
            obj = json.loads(txt)
            self._set_text(self.json_output, json.dumps(obj, indent=2, ensure_ascii=False))
        except Exception as e:
            self._set_text(self.json_output, f"JSON invalide : {e}")

    def page_files(self):
        self.page.grid_columnconfigure(0, weight=1)

        frame = self.card(self.page, "Outils fichiers", "Entre un chemin de fichier pour calculer sa taille et son SHA256.")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.file_path = ctk.CTkEntry(frame, height=42, placeholder_text="Chemin du fichier, ex: /home/toka/image.png ou C:\\Users\\Toka\\file.zip")
        self.file_path.grid(row=2, column=0, padx=24, pady=10, sticky="ew")

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.grid(row=3, column=0, padx=24, pady=4, sticky="ew")
        row.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(row, text="Analyser fichier", command=self.analyze_file).grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkButton(row, text="Ouvrir dossier données", command=lambda: open_file_manager(DATA_DIR)).grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkButton(row, text="Nettoyer nom fichier", command=self.clean_filename).grid(row=0, column=2, padx=4, sticky="ew")

        self.file_output = ctk.CTkTextbox(frame, height=420, corner_radius=16, font=ctk.CTkFont(family="monospace", size=13))
        self.file_output.grid(row=4, column=0, padx=24, pady=16, sticky="ew")

    def analyze_file(self):
        p = Path(self.file_path.get().strip().strip('"'))
        if not p.exists() or not p.is_file():
            self._set_text(self.file_output, "Fichier introuvable.")
            return
        h = hashlib.sha256()
        try:
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            info = (
                f"Nom : {p.name}\n"
                f"Chemin : {p}\n"
                f"Taille : {p.stat().st_size} octets\n"
                f"Taille MB : {round(p.stat().st_size / 1024**2, 3)} MB\n"
                f"SHA256 : {h.hexdigest()}\n"
                f"Modifié : {datetime.fromtimestamp(p.stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')}"
            )
            self._set_text(self.file_output, info)
        except Exception as e:
            self._set_text(self.file_output, f"Erreur : {e}")

    def clean_filename(self):
        raw = self.file_path.get().strip()
        cleaned = "".join(c for c in raw if c.isalnum() or c in (" ", ".", "_", "-")).strip().replace(" ", "_")
        self._set_text(self.file_output, f"Nom nettoyé :\n{cleaned}")

    def page_webtools(self):
        self.page.grid_columnconfigure((0, 1), weight=1)

        enc = self.card(self.page, "URL tools", "Encode ou décode une URL.")
        enc.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.url_input = ctk.CTkTextbox(enc, height=160, corner_radius=16)
        self.url_input.grid(row=2, column=0, padx=24, pady=10, sticky="ew")
        row = ctk.CTkFrame(enc, fg_color="transparent")
        row.grid(row=3, column=0, padx=24, pady=4, sticky="ew")
        row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(row, text="Encode URL", command=self.url_encode).grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkButton(row, text="Decode URL", command=self.url_decode).grid(row=0, column=1, padx=4, sticky="ew")
        self.url_output = ctk.CTkTextbox(enc, height=220, corner_radius=16)
        self.url_output.grid(row=4, column=0, padx=24, pady=10, sticky="ew")

        search = self.card(self.page, "Recherche rapide", "Ouvre directement une recherche web.")
        search.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.search_entry = ctk.CTkEntry(search, height=42, placeholder_text="Recherche...")
        self.search_entry.grid(row=2, column=0, padx=24, pady=10, sticky="ew")
        ctk.CTkButton(search, text="Rechercher sur Google", height=42, command=lambda: self.search_web("google")).grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        ctk.CTkButton(search, text="Rechercher sur DuckDuckGo", height=42, command=lambda: self.search_web("ddg")).grid(row=4, column=0, padx=24, pady=8, sticky="ew")
        ctk.CTkButton(search, text="Ouvrir GitHub", height=42, command=lambda: open_url("https://github.com")).grid(row=5, column=0, padx=24, pady=8, sticky="ew")

    def url_encode(self):
        self._set_text(self.url_output, urllib.parse.quote(self._get_text(self.url_input)))

    def url_decode(self):
        self._set_text(self.url_output, urllib.parse.unquote(self._get_text(self.url_input)))

    def search_web(self, engine):
        q = urllib.parse.quote(self.search_entry.get().strip())
        if not q:
            return
        url = f"https://www.google.com/search?q={q}" if engine == "google" else f"https://duckduckgo.com/?q={q}"
        open_url(url)

    def page_randomizer(self):
        self.page.grid_columnconfigure((0, 1), weight=1)

        gen = self.card(self.page, "Générateurs rapides", "Crée des valeurs utiles rapidement.")
        gen.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.rand_output = ctk.CTkTextbox(gen, height=420, corner_radius=16, font=ctk.CTkFont(family="monospace", size=13))
        self.rand_output.grid(row=6, column=0, padx=24, pady=14, sticky="ew")
        for r, (txt, cmd) in enumerate([
            ("Mot de passe fort", self.rand_password),
            ("Token sécurisé", self.rand_token),
            ("Pseudo stylé", self.rand_pseudo),
            ("Palette HEX", self.rand_palette),
        ], start=2):
            ctk.CTkButton(gen, text=txt, height=42, command=cmd).grid(row=r, column=0, padx=24, pady=5, sticky="ew")

        tips = self.card(self.page, "Idées d’utilisation", "Des trucs pratiques à faire avec ces générateurs.")
        tips.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        text = (
            "• Mot de passe fort : pour créer un compte.\n"
            "• Token sécurisé : pour clé locale ou identifiant temporaire.\n"
            "• Pseudo stylé : pour projet, profil ou app.\n"
            "• Palette HEX : pour design web ou UI.\n\n"
            "Tout est généré localement sur ton PC."
        )
        ctk.CTkLabel(tips, text=text, justify="left", text_color="#DDE3FF", font=ctk.CTkFont(size=15)).grid(row=2, column=0, padx=24, pady=20, sticky="w")

    def rand_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}"
        self._set_text(self.rand_output, "".join(secrets.choice(alphabet) for _ in range(32)))

    def rand_token(self):
        self._set_text(self.rand_output, secrets.token_urlsafe(48))

    def rand_pseudo(self):
        prefixes = ["Toka", "Nova", "Atlas", "Ghost", "Pulse", "Storm", "Zero", "Night", "Astra", "Vortex"]
        suffixes = ["Core", "X", "Labs", "Flow", "Byte", "Wave", "Stack", "Hub", "Vision", "Nexus"]
        self._set_text(self.rand_output, f"{secrets.choice(prefixes)}{secrets.choice(suffixes)}{secrets.randbelow(999)}")

    def rand_palette(self):
        vals = [f"#{secrets.randbelow(0xFFFFFF):06X}" for _ in range(8)]
        self._set_text(self.rand_output, "\n".join(vals))

    def page_quicklinks(self):
        self.page.grid_columnconfigure((0, 1), weight=1)

        form = self.card(self.page, "Ajouter un raccourci", "Ajoute un lien web ou un chemin local.")
        form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.ql_name = ctk.CTkEntry(form, height=42, placeholder_text="Nom du raccourci")
        self.ql_target = ctk.CTkEntry(form, height=42, placeholder_text="URL ou chemin local")
        self.ql_name.grid(row=2, column=0, padx=24, pady=8, sticky="ew")
        self.ql_target.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        ctk.CTkButton(form, text="Ajouter", height=42, command=self.add_quicklink).grid(row=4, column=0, padx=24, pady=8, sticky="ew")

        list_card = self.card(self.page, "Mes raccourcis", "Clique pour ouvrir.")
        list_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.ql_frame = ctk.CTkScrollableFrame(list_card, height=460, corner_radius=16)
        self.ql_frame.grid(row=2, column=0, padx=24, pady=16, sticky="nsew")
        self.quicklinks = load_json(QUICKLINKS_FILE, [
            {"name": "Dossier données Toka", "target": str(DATA_DIR)},
            {"name": "GitHub", "target": "https://github.com"},
        ])
        self.refresh_quicklinks()

    def add_quicklink(self):
        name = self.ql_name.get().strip()
        target = self.ql_target.get().strip()
        if not name or not target:
            return
        self.quicklinks.append({"name": name, "target": target})
        save_json(QUICKLINKS_FILE, self.quicklinks)
        self.ql_name.delete(0, "end")
        self.ql_target.delete(0, "end")
        self.refresh_quicklinks()

    def refresh_quicklinks(self):
        for child in self.ql_frame.winfo_children():
            child.destroy()
        for i, item in enumerate(self.quicklinks):
            row = ctk.CTkFrame(self.ql_frame, corner_radius=14, fg_color="#1A1D2A")
            row.pack(fill="x", pady=6, padx=4)
            ctk.CTkButton(row, text=item["name"], height=38, anchor="w", command=lambda t=item["target"]: self.open_quicklink(t)).pack(side="left", fill="x", expand=True, padx=10, pady=8)
            ctk.CTkButton(row, text="X", width=38, fg_color="#7A1F2A", command=lambda idx=i: self.delete_quicklink(idx)).pack(side="right", padx=8, pady=8)

    def open_quicklink(self, target):
        if target.startswith("http://") or target.startswith("https://"):
            open_url(target)
        else:
            open_file_manager(Path(target))

    def delete_quicklink(self, idx):
        self.quicklinks.pop(idx)
        save_json(QUICKLINKS_FILE, self.quicklinks)
        self.refresh_quicklinks()

    def page_settings(self):
        self.page.grid_columnconfigure(0, weight=1)

        frame = self.card(self.page, "Détection automatique", "Cette page montre ce que l'application a détecté au lancement.")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        text = (
            f"{ASCII_ART}\n"
            f"Application : {APP_NAME}\n"
            f"Plateforme détectée : {self.os_label}\n"
            f"platform.system() : {platform.system()}\n"
            f"Version OS : {platform.release()}\n"
            f"Architecture : {platform.machine()}\n"
            f"Python : {platform.python_version()}\n"
            f"Dossier données : {DATA_DIR}\n\n"
            f"Windows actif : {IS_WINDOWS}\n"
            f"Linux actif : {IS_LINUX}\n"
        )

        box = ctk.CTkTextbox(frame, height=430, corner_radius=16, font=ctk.CTkFont(family="monospace", size=13))
        box.grid(row=2, column=0, padx=24, pady=18, sticky="ew")
        box.insert("end", text)

        ctk.CTkButton(frame, text="Ouvrir le dossier des données", height=42, command=lambda: open_file_manager(DATA_DIR)).grid(row=3, column=0, padx=24, pady=(0, 22), sticky="ew")


if __name__ == "__main__":
    print(ASCII_ART)
    print(f"Plateforme détectée : {platform.system()}")
    app = TokaSuite()
    app.mainloop()
