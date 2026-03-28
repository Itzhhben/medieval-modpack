import os
import json
import hashlib

BASE_URL = "https://raw.githubusercontent.com/Itzhhben/medieval-modpack/main"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_folder(folder):
    files = []
    for root, _, filenames in os.walk(folder):
        for name in filenames:
            path = os.path.join(root, name)
            rel_path = path.replace("\\", "/")
            files.append({
                "path": rel_path,
                "sha256": sha256_file(path)
            })
    return files

manifest = {
    "pack_name": "medieval-modpack",
    "pack_version": "1.0.0",
    "base_url": BASE_URL,
    "files": scan_folder("mods")
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("Manifest generado 🗿🔥")