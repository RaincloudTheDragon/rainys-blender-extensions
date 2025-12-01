#!/usr/bin/env python3
"""
Script to automatically update the Blender extension catalog from GitHub releases.

This script fetches release information from GitHub repositories and generates
a catalog.json file for Blender's extension system.

Usage:
    python update_catalog.py

Requirements:
    pip install requests

Configuration:
    Edit the ADDONS list below with your addon information.
"""

import json
import requests
from typing import List, Dict, Optional

# Configuration: Add your addons here
ADDONS = [
    {
        "id": "atomic_data_manager",
        "repo": "grantwilk/atomic-data-manager",
        "manifest_branch": "main",  # Branch where blender_manifest.toml is located
    },
    # Add more addons here:
    # {
    #     "id": "another_addon",
    #     "repo": "username/repo-name",
    #     "manifest_branch": "main",
    # },
]


def get_latest_release(repo: str) -> Optional[Dict]:
    """Get the latest release from a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching release for {repo}: {e}")
        return None


def get_manifest_url(repo: str, branch: str, manifest_path: str = "blender_manifest.toml") -> str:
    """Generate the raw manifest URL."""
    return f"https://github.com/{repo}/raw/{branch}/{manifest_path}"


def get_archive_url(release: Dict, repo: str) -> Optional[str]:
    """Get the ZIP archive URL from a release."""
    if not release or "assets" not in release:
        return None
    
    # Look for a ZIP file in the release assets
    for asset in release.get("assets", []):
        if asset.get("content_type") == "application/zip" or asset.get("name", "").endswith(".zip"):
            return asset.get("browser_download_url")
    
    # Fallback: use the source code ZIP
    tag = release.get("tag_name", "")
    if tag:
        return f"https://github.com/{repo}/archive/refs/tags/{tag}.zip"
    
    return None


def parse_version_from_tag(tag: str) -> str:
    """Extract version from git tag (removes 'v' prefix if present)."""
    return tag.lstrip("v")


def generate_catalog(addons: List[Dict]) -> Dict:
    """Generate the catalog JSON from addon configurations."""
    extensions = []
    
    for addon in addons:
        repo = addon["repo"]
        addon_id = addon["id"]
        branch = addon.get("manifest_branch", "main")
        
        print(f"Processing {addon_id} from {repo}...")
        
        release = get_latest_release(repo)
        if not release:
            print(f"  Warning: No release found for {repo}, skipping...")
            continue
        
        tag = release.get("tag_name", "")
        version = parse_version_from_tag(tag)
        archive_url = get_archive_url(release, repo)
        manifest_url = get_manifest_url(repo, branch)
        
        if not archive_url:
            print(f"  Warning: No ZIP archive found for {repo}, skipping...")
            continue
        
        extension = {
            "id": addon_id,
            "version": version,
            "archive_url": archive_url,
            "manifest_url": manifest_url,
        }
        
        extensions.append(extension)
        print(f"  ✓ Added {addon_id} v{version}")
    
    return {
        "schema_version": "1.0.0",
        "extensions": extensions,
    }


def main():
    """Main function to generate and save the catalog."""
    print("Generating Blender extension catalog...")
    print("-" * 50)
    
    catalog = generate_catalog(ADDONS)
    
    output_file = "catalog.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print(f"✓ Catalog generated: {output_file}")
    print(f"  Found {len(catalog['extensions'])} extensions")


if __name__ == "__main__":
    main()
