import requests
import subprocess
import os
from PySide6.QtCore import QThread, Signal

import minecraft_launcher_lib


class LaunchWorker(QThread):
    progress_update = Signal(str, int)
    log_output = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, username, version, directory, ram, java_path=None, ms_auth=None):
        super().__init__()
        self.username = username
        self.version = version
        self.directory = directory
        self.ram = ram
        self.java_path = java_path
        self.ms_auth = ms_auth

    def run(self):
        try:
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)

            installed_versions = [v['id'] for v in minecraft_launcher_lib.utils.get_installed_versions(self.directory)]
            if self.version not in installed_versions:
                self.progress_update.emit(f"Installing {self.version}...", 0)
                minecraft_launcher_lib.install.install_minecraft_version(
                    self.version, self.directory,
                    callback={
                        "setStatus": lambda t: self.progress_update.emit(t, 0),
                        "setProgress": lambda p: self.progress_update.emit("Downloading...", int(p)),
                        "setMax": lambda m: None
                    }
                )

            options = {
                "username": self.username,
                "uuid": "",
                "token": "",
                "jvmArguments": [f"-Xmx{self.ram}M", f"-Xms{self.ram}M"]
            }

            if self.ms_auth:
                options["username"] = self.ms_auth["name"]
                options["uuid"] = self.ms_auth.get("uuid", "")
                options["token"] = self.ms_auth.get("minecraft_access_token", "")

            if self.java_path:
                options["executablePath"] = self.java_path

            self.progress_update.emit("Launching...", 100)
            cmd = minecraft_launcher_lib.command.get_minecraft_command(self.version, self.directory, options)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_output.emit(output.strip())
            stderr = process.communicate()[1]
            if stderr:
                self.log_output.emit(f"STDERR: {stderr}")

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


# -------------------------
# Microsoft → Xbox → Minecraft flow
# -------------------------
class MSLoginWorker(QThread):
    code_needed = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            client_id = "00000000402b5328"
            redirect_uri = "https://login.live.com/oauth20_desktop.srf"
            scope = "XboxLive.signin offline_access"

            url = f"https://login.live.com/oauth20_authorize.srf?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
            self.code_needed.emit(f"1. Login in browser\n2. Copy the full redirect URL\n\nURL: {url}")

        except Exception as e:
            self.error.emit(f"Failed to get login URL: {e}")


class MSLoginFinisher(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, redirect_url):
        super().__init__()
        self.redirect_url = redirect_url

    def run(self):
        try:
            code = self.redirect_url.split("code=")[1].split("&")[0]

            # -------------------------
            # Step 1: Exchange code for Microsoft token
            # -------------------------
            data = {
                "client_id": "00000000402b5328",
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://login.live.com/oauth20_desktop.srf"
            }
            r = requests.post("https://login.live.com/oauth20_token.srf", data=data)
            r.raise_for_status()
            ms_token = r.json()["access_token"]

            # -------------------------
            # Step 2: Authenticate with Xbox Live
            # -------------------------
            xbl_req = {
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": f"d={ms_token}"
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
            }
            r = requests.post("https://user.auth.xboxlive.com/user/authenticate", json=xbl_req)
            r.raise_for_status()
            xbl_token = r.json()["Token"]

            # -------------------------
            # Step 3: XSTS auth
            # -------------------------
            xsts_req = {
                "Properties": {
                    "SandboxId": "RETAIL",
                    "UserTokens": [xbl_token]
                },
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT"
            }
            r = requests.post("https://xsts.auth.xboxlive.com/xsts/authorize", json=xsts_req)
            r.raise_for_status()
            xsts = r.json()
            xsts_token = xsts["Token"]
            user_hash = xsts["DisplayClaims"]["xui"][0]["uhs"]

            # -------------------------
            # Step 4: Get Minecraft access token
            # -------------------------
            mc_req = {
                "identityToken": f"XBL3.0 x={user_hash};{xsts_token}"
            }
            r = requests.post("https://api.minecraftservices.com/authentication/login_with_xbox", json=mc_req)
            r.raise_for_status()
            mc_access_token = r.json()["access_token"]

            # -------------------------
            # Step 5: Get Minecraft profile
            # -------------------------
            r = requests.get(
                "https://api.minecraftservices.com/minecraft/profile",
                headers={"Authorization": f"Bearer {mc_access_token}"}
            )
            r.raise_for_status()
            profile = r.json()

            self.finished.emit({
                "minecraft_access_token": mc_access_token,
                "xsts_token": xsts_token,
                "xbl_token": xbl_token,
                "name": profile["name"],
                "uuid": profile["id"]
            })

        except Exception as e:
            self.error.emit(f"Microsoft login failed: {str(e)}")
