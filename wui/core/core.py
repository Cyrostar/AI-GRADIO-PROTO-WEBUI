import os
import json
import shutil

path_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

wui_cnfg = os.path.join(path_base, "wui.json")
wui_locs = os.path.join(path_base, "locales")
wui_mods = os.path.join(path_root, "models")

import sys

core_path = os.path.dirname(os.path.abspath(__file__))
if core_path not in sys.path:
    sys.path.insert(0, core_path)

comfy_site_packages = r"S:\ComfyUI\ComfyUI\python_embeded\Lib\site-packages"
if os.path.exists(comfy_site_packages) and comfy_site_packages not in sys.path:
    sys.path.append(comfy_site_packages)

comfy_root = r"S:\ComfyUI\ComfyUI\ComfyUI"
if os.path.exists(comfy_root) and comfy_root not in sys.path:
    sys.path.append(comfy_root)

def load_wui():
    """Reads the global configuration from wui.json."""
    if os.path.exists(wui_cnfg):
        try:
            with open(wui_cnfg, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}
    
def save_wui(language=None, last_user=None, last_project=None):
    """Saves global states to wui.json in exact order: language, user, project."""
    current_data = load_wui()
    
    # Enforce precise key insertion order
    new_data = {
        "wui_lang": language if language is not None else current_data.get("wui_lang", "en"),
        "wui_user": last_user if last_user is not None else current_data.get("wui_user", "artha"),
        "wui_project": last_project if last_project is not None else current_data.get("wui_project", "myproject")
    }
    
    try:
        with open(wui_cnfg, "w") as f:
            json.dump(new_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

wui_data = load_wui()
wui_lang = wui_data.get("wui_lang", "en")
wui_user = wui_data.get("wui_user", "artha")
wui_proj = wui_data.get("wui_project", "myproject")

# --- 1. USER MANAGEMENT LOGIC ---
# Dynamically assign user path inside the global user's folder

u_path = os.path.join(path_base, "users")
os.makedirs(u_path, exist_ok=True)

user_name = ""
user_path = ""

def list_users():
    if not os.path.exists(u_path):
        return []
    all_items = os.listdir(u_path)
    return sorted([item for item in all_items if os.path.isdir(os.path.join(u_path, item))])

def delete_user(name):
    target = os.path.join(u_path, name)
    if os.path.exists(target) and os.path.isdir(target):
        shutil.rmtree(target)
        return True
    return False

available_users = list_users()

if not available_users:
    os.makedirs(os.path.join(u_path, "artha"), exist_ok=True)
    user_name = "artha"
else:
    user_name = wui_user if wui_user in available_users else available_users[0]
        
user_path = os.path.join(u_path, user_name)

# --- 2. PROJECT MANAGEMENT LOGIC ---
# Dynamically assign project path inside the active user's folder

p_path = os.path.join(user_path, "projects")

os.makedirs(p_path, exist_ok=True)

project_name = ""
project_path = ""

def list_projects():
    if not os.path.exists(p_path):
        return []
    all_items = os.listdir(p_path)
    project_names = [
        item for item in all_items 
        if os.path.isdir(os.path.join(p_path, item))
    ]
    return sorted(project_names)
    
def delete_project(name):
    target = os.path.join(p_path, name)
    if os.path.exists(target) and os.path.isdir(target):
        shutil.rmtree(target)
        return True
    return False
    
available_projects = list_projects()

if not available_projects:
    os.makedirs(os.path.join(p_path, "myproject"), exist_ok=True)
    project_name = "myproject"
else:
    project_name = wui_proj if wui_proj in available_projects else available_projects[0]
        
project_path = os.path.join(p_path, project_name)

# Save initial states
save_wui(language=wui_lang, last_user=user_name, last_project=project_name)
        
def get_available_languages():
    """Scans the locales for available language JSON files."""
    if not os.path.exists(wui_locs):
        return ["en", "tr"] # Safe fallback
    
    langs = []
    for f in os.listdir(wui_locs):
        if f.endswith(".json"):
            # Extracts 'en' from 'en_US.json' or 'tr' from 'tr_TR.json'
            lang_code = f.split("_")[0] 
            if lang_code not in langs:
                langs.append(lang_code)
                
    return sorted(langs) if langs else ["en", "tr"]
        
class Translator:
    def __init__(self):
        config = load_wui()
        # Default to "en" if not set
        self.language = config.get("wui_lang", "en")
        self.language_map = self._load_language_file(self.language)

    def _load_language_file(self, lang):
        if not os.path.exists(wui_locs):
            return {}
            
        for f in os.listdir(wui_locs):
            if f.startswith(f"{lang}_") and f.endswith(".json"):
                lang_path = os.path.join(wui_locs, f)
                try:
                    with open(lang_path, "r", encoding="utf-8") as file:
                        return json.load(file)
                except Exception as e:
                    print(f"Error loading language file {lang_path}: {e}")
                    
        return {} # Returns empty dict if file is not found

    def __call__(self, key):
        # Return translated string, fallback to key if missing
        return self.language_map.get(key, key)
        
_ = Translator() 
ui_language = _.language