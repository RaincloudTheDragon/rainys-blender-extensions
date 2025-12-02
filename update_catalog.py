#!/usr/bin/env python3
"""
Generate Blender extension repository metadata using Blender's server tool.

This script downloads the latest release archives from GitHub, lets Blender
validate/build the repository metadata, and rewrites the resulting JSON to
point back to the public GitHub release URLs.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import requests

# --- Configuration ---------------------------------------------------------

# List of addons to include in the repository.
ADDONS = [
    {
        "id": "basedplayblast",
        "repo": "RaincloudTheDragon/BasedPlayblast",
    },
    {
        "id": "rainys_bulk_scene_tools",
        "repo": "RaincloudTheDragon/Rainys-Bulk-Scene-Tools",
    },
]

BLENDER_EXECUTABLE = os.environ.get("BLENDER_PATH", "blender")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

BUILD_DIR = Path("build")
REPO_DIR = BUILD_DIR / "repo"
OUTPUT_INDEX = Path("index.json")

# ---------------------------------------------------------------------------

session = requests.Session()
session.headers.update({"Accept": "application/vnd.github+json"})
if GITHUB_TOKEN:
    session.headers.update({"Authorization": f"Bearer {GITHUB_TOKEN}"})


def github_api(url: str) -> Optional[Dict]:
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"  ⚠ GitHub request failed: {exc}")
        return None


def pick_zip_asset(assets: List[Dict]) -> Optional[Dict]:
    for asset in assets:
        name = asset.get("name", "")
        content_type = asset.get("content_type", "")
        if name.endswith(".zip") or content_type == "application/zip":
            return asset
    return None


def download_asset(url: str, destination: Path) -> bool:
    try:
        with session.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "wb") as file_obj:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file_obj.write(chunk)
        return True
    except requests.RequestException as exc:
        print(f"  ⚠ Download failed ({url}): {exc}")
        return False


def clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def run_blender_repo_generator(repo_dir: Path) -> None:
    cmd = [
        BLENDER_EXECUTABLE,
        "--background",
        "--factory-startup",
        "--command",
        "extension",
        "server-generate",
        "--repo-dir",
        str(repo_dir.resolve()),
    ]
    print(f"Running Blender repo generator:\n  {' '.join(str(part) for part in cmd)}")
    subprocess.run(cmd, check=True)


def rewrite_archive_urls(index_path: Path, url_map: Dict[str, str]) -> Dict:
    with open(index_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    for package in data.get("data", []):
        archive_value = package.get("archive_url") or package.get("archive_path", "")
        filename = Path(archive_value).name
        if filename in url_map:
            package["archive_url"] = url_map[filename]

    return data


def process_addon(addon: Dict, download_dir: Path) -> Optional[Dict[str, str]]:
    repo = addon["repo"]
    release = github_api(f"https://api.github.com/repos/{repo}/releases/latest")
    if not release:
        return None

    asset = pick_zip_asset(release.get("assets", []))
    if not asset:
        print(f"  ⚠ No ZIP asset found for {repo}")
        return None

    filename = asset["name"]
    download_url = asset["browser_download_url"]
    dest = download_dir / filename
    print(f"  ↳ downloading {filename}")
    if not download_asset(download_url, dest):
        return None

    return {
        "filename": filename,
        "archive_url": download_url,
    }


def main() -> None:
    print("Generating Blender extension repository metadata...")
    clean_directory(REPO_DIR)

    filename_to_url: Dict[str, str] = {}
    for addon in ADDONS:
        print(f"Fetching release for {addon['repo']}...")
        result = process_addon(addon, REPO_DIR)
        if result:
            filename_to_url[result["filename"]] = result["archive_url"]

    if not filename_to_url:
        print("No archives downloaded. Aborting.")
        return

    try:
        run_blender_repo_generator(REPO_DIR)
    except subprocess.CalledProcessError as exc:
        print(f"Blender command failed: {exc}")
        return

    generated_index = REPO_DIR / "index.json"
    if not generated_index.exists():
        print(f"Generated index not found at {generated_index}")
        return

    updated_index = rewrite_archive_urls(generated_index, filename_to_url)
    with open(OUTPUT_INDEX, "w", encoding="utf-8") as handle:
        json.dump(updated_index, handle, indent=2)

    print("-" * 50)
    print(f"✓ Repository index written to {OUTPUT_INDEX}")
    print(f"  Packages: {len(updated_index.get('data', []))}")


if __name__ == "__main__":
    main()
