import network
import gc
import urequests
import os
import json
import machine
from time import sleep

class OTAUpdater:
    """Handles OTA updates: checks Wi-Fi, fetches version.json, downloads and installs files."""
    
    def __init__(self, repo_url):
        # Clean and convert GitHub repo to raw URL if needed
        if "www.github.com" in repo_url:
            repo_url = repo_url.replace("www.github", "raw.githubusercontent")
        elif "github.com" in repo_url:
            repo_url = repo_url.replace("github", "raw.githubusercontent")
        
        self.repo_url = repo_url.rstrip('/') + '/main/'
        self.version_url = self.repo_url + 'version.json'
        print(f"[OTA] Version URL: {self.version_url}")
        
        # Load current version
        if 'version.json' in os.listdir():
            with open('version.json') as f:
                self.current_version = float(json.load(f)['version'])
        else:
            self.current_version = 0
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)
        
        print(f"[OTA] Current version: {self.current_version}")

    def is_wifi_connected(self):
        """Returns True if Wi-Fi is connected."""
        wlan = network.WLAN(network.STA_IF)
        return wlan.active() and wlan.isconnected()

    def check_for_updates(self):
        """Checks GitHub for a new version and stores filenames to fetch."""
        if not self.is_wifi_connected():
            print("[OTA] Wi-Fi not connected.")
            return False
        
        print(f"[OTA] Checking for updates at: {self.version_url}")
        try:
            response = urequests.get(self.version_url)
            print("[OTA] Raw response text:", response.text)
            data = response.json()
            response.close()
        except Exception as e:
            print(f"[OTA] Failed to get version info: {e}")
            return False

        self.latest_version = float(data.get('version', 0))
        self.file_list = data.get('filenames', [])

        print(f"[OTA] Latest version: {self.latest_version}")
        print(f"[OTA] Files to update: {self.file_list}")
        
        return self.latest_version > self.current_version

    def fetch_and_write_files(self):
        """Downloads all files from the list and writes them to the file system."""
        for file in self.file_list:
            file_url = self.repo_url + file
            print(f"[OTA] Downloading: {file_url}")
            try:
                response = urequests.get(file_url)
                if response.status_code == 200:
                    # Ensure folder exists
                    dirs = file.rsplit('/', 1)[0]
                    if '/' in file and not dirs in os.listdir():
                        try:
                            os.mkdir(dirs)
                        except OSError as e:
                            print(f"[OTA] Could not create folder '{dirs}': {e}")

                    # Write file
                    with open(file, 'w') as f:
                        f.write(response.text)
                    print(f"[OTA] Updated: {file}")
                else:
                    print(f"[OTA] Failed to fetch {file}: {response.status_code}")
                response.close()
                del response
                gc.collect() 
            except Exception as e:
                print(f"[OTA] Error fetching {file}: {e}")

        # Update local version
        with open('version.json', 'w') as f:
            json.dump({'version': self.latest_version}, f)

    def download_and_install_update_if_available(self,optional_deleted_file=None):
        """Performs OTA update if newer version is available."""
        if self.check_for_updates():
            print("[OTA] New version found. Updating...")
            self.fetch_and_write_files()
            print("[OTA] Restarting device.")
            if optional_deleted_file:
                if 'to_be_updated.txt' in os.listdir():
                    os.remove('to_be_updated.txt')
            
            print('Update successfully!')
            return 'Update successfully!'
            machine.reset()
        else:
            print("[OTA] No new updates available.")
            return 'No new updates available'
