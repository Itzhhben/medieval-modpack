import json
import hashlib
import sys
from pathlib import Path
from urllib.request import urlopen, urlretrieve

MANIFEST_URL = "https://raw.githubusercontent.com/Itzhhben/medieval-modpack/main/manifest.json"
LOCAL_ROOT = Path(__file__).resolve().parent.parent
LOCAL_MANIFEST_PATH = LOCAL_ROOT / ".local_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_json(url: str) -> dict:
    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def ensure_parent_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path):
    ensure_parent_dir(dest)
    print(f"Descargando: {dest.relative_to(LOCAL_ROOT)}")
    urlretrieve(url, dest)


def load_local_manifest() -> dict | None:
    if LOCAL_MANIFEST_PATH.exists():
        with open(LOCAL_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_local_manifest(manifest: dict):
    with open(LOCAL_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def sync_files(remote_manifest: dict):
    base_url = remote_manifest["base_url"]
    remote_files = {entry["path"]: entry["sha256"] for entry in remote_manifest["files"]}

    for rel_path, remote_hash in remote_files.items():
        local_path = LOCAL_ROOT / rel_path
        needs_download = True

        if local_path.exists():
            local_hash = sha256_file(local_path)
            if local_hash.lower() == remote_hash.lower():
                needs_download = False

        if needs_download:
            file_url = f"{base_url}/{rel_path}"
            download_file(file_url, local_path)

            downloaded_hash = sha256_file(local_path)
            if downloaded_hash.lower() != remote_hash.lower():
                raise RuntimeError(f"Hash incorrecto después de descargar: {rel_path}")

    old_manifest = load_local_manifest()
    if old_manifest:
        old_files = {entry["path"] for entry in old_manifest.get("files", [])}
        removed_files = old_files - set(remote_files.keys())

        for rel_path in removed_files:
            local_path = LOCAL_ROOT / rel_path
            if local_path.exists():
                print(f"Eliminando archivo viejo: {rel_path}")
                local_path.unlink()


def main():
    print("Buscando actualizaciones del modpack...\n")

    remote_manifest = download_json(MANIFEST_URL)
    local_manifest = load_local_manifest()

    remote_version = remote_manifest.get("pack_version", "0")
    local_version = local_manifest.get("pack_version", "0") if local_manifest else "0"

    print(f"Versión local:  {local_version}")
    print(f"Versión remota: {remote_version}\n")

    if local_version != remote_version:
        print("Hay actualización. Descargando mods...\n")
        sync_files(remote_manifest)
        save_local_manifest(remote_manifest)
        print("\nModpack actualizado correctamente 🗿🔥")
    else:
        print("Tu modpack ya está al día 🗿")

    input("\nPresiona ENTER para cerrar. Luego abre tu launcher y usa esta carpeta del pack.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        input("Presiona ENTER para salir...")
        sys.exit(1)