import json
import os
import shutil

class AppState:
    def __init__(self):
        self.config_file = "launcher_state.json"
        self.username = "Player"
        self.ram = 2048  # Default 2GB
        self.minecraft_dir = os.path.join(os.getcwd(), "minecraft_data")
        self.modpacks = []
        self.active_modpack = None
        self.java_path = ""
        self.ms_auth_data = None
        self.skin_path = ""
        
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.username = data.get("username", self.username)
                    self.ram = data.get("ram", self.ram)
                    self.minecraft_dir = data.get("minecraft_dir", self.minecraft_dir)
                    self.java_path = data.get("java_path", self.java_path)
                    self.modpacks = data.get("modpacks", [])
                    self.ms_auth_data = data.get("ms_auth_data")
                    self.skin_path = data.get("skin_path", "")
                    active_id = data.get("active_modpack")
                    if active_id:
                        for mp in self.modpacks:
                            if mp.get("id") == active_id:
                                self.active_modpack = mp
                                break
            except Exception as e:
                print(f"Error loading state: {e}")

    def save(self):
        data = {
            "username": self.username,
            "ram": self.ram,
            "minecraft_dir": self.minecraft_dir,
            "java_path": self.java_path,
            "modpacks": self.modpacks,
            "ms_auth_data": self.ms_auth_data,
            "skin_path": self.skin_path,
            "active_modpack": self.active_modpack.get("id") if self.active_modpack else None
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving state: {e}")

    def add_modpack(self, name, version, loader):
        import uuid
        modpack = {
            "id": str(uuid.uuid4()),
            "name": name,
            "version": version,
            "loader": loader,
            "mods": []
        }
        self.modpacks.append(modpack)
        self.active_modpack = modpack
        self.save()
        return modpack

    def set_skin(self, source_path):
        if not os.path.exists(source_path):
            return
        
        skins_dir = os.path.join(os.getcwd(), "skins")
        if not os.path.exists(skins_dir):
            os.makedirs(skins_dir)
            
        dest_filename = f"{self.username}.png"
        dest_path = os.path.join(skins_dir, dest_filename)
        
        try:
            shutil.copy2(source_path, dest_path)
            self.skin_path = dest_path
            self.save()
            return True
        except Exception as e:
            print(f"Error saving skin: {e}")
            return False

state = AppState()
