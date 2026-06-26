from pathlib import Path
from os import makedirs

from deemix.app import deemix
from deemix.utils import checkFolder

class cli(deemix):
    def __init__(self, downloadpath, configFolder=None):
        super().__init__(configFolder, overwriteDownloadFolder=downloadpath)
        if downloadpath:
            print("Using folder: "+self.set.settings['downloadLocation'])

    def downloadLink(self, url, bitrate=None):
        for link in url:
            if ';' in link:
                for l in link.split(";"):
                    self.qm.addToQueue(self.dz, l, self.set.settings, bitrate)
            else:
                self.qm.addToQueue(self.dz, link, self.set.settings, bitrate)

    def requestValidArl(self):
        print("\nTo get your ARL:")
        print("  1. Open deezer.com in your browser and log in")
        print("  2. Open DevTools (F12) -> Application -> Cookies -> https://www.deezer.com")
        print("  3. Find cookie named 'arl' and copy its value")
        print()
        while True:
            arl = input("Paste here your arl: ").strip()
            if not arl:
                print("[Error] ARL cannot be empty. Please paste your ARL token.")
                continue
            if len(arl) < 100:
                print(f"[Error] ARL looks too short ({len(arl)} chars, expected 192+). Make sure you copied the full value.")
                continue
            print("[Info] Checking ARL with Deezer...")
            try:
                result = self.dz.login_via_arl(arl)
            except Exception as e:
                print(f"[Error] Network error while checking ARL: {e}")
                print("[Info] Check your internet connection and try again.")
                continue
            if result:
                print("[OK] Login successful!")
                break
            else:
                print("[Error] ARL was rejected by Deezer. Possible reasons:")
                print("  - ARL has expired (tokens last ~3 months, get a fresh one)")
                print("  - ARL was copied incorrectly (missing characters or extra spaces)")
                print("  - Your Deezer account is restricted or banned")
                print("  - You are not logged in on deezer.com (log in first, then copy ARL)")
                print()
        return arl

    def login(self):
        configFolder = Path(self.set.configFolder)
        if not configFolder.is_dir():
            makedirs(configFolder, exist_ok=True)
        if (configFolder / '.arl').is_file():
            with open(configFolder / '.arl', 'r') as f:
                arl = f.readline().rstrip("\n").strip()
            print("[Info] Found saved ARL, checking...")
            if not self.dz.login_via_arl(arl):
                print("[Error] Saved ARL is no longer valid (expired or revoked).")
                arl = self.requestValidArl()
        else:
            arl = self.requestValidArl()
        with open(configFolder / '.arl', 'w') as f:
            f.write(arl)
