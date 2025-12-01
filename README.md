# Blender Extension Catalog Setup

This directory contains the catalog API for your Blender extensions. This allows users to update your addons directly from Blender's extension manager.

## Setup Instructions

### 1. Create a GitHub Pages Repository

Create a new repository (e.g., `your-username.github.io` or `blender-extensions`) and enable GitHub Pages:

1. Go to your repository Settings → Pages
2. Select source: "Deploy from a branch"
3. Choose branch: `main` (or `gh-pages`)
4. Select folder: `/ (root)`
5. Save

### 2. Upload the Catalog File

1. Copy `catalog.json` to your GitHub Pages repository
2. Commit and push to the branch you selected for Pages
3. Your catalog will be available at: `https://your-username.github.io/extension_catalog/catalog.json`

### 3. Configure Your Extensions

For each addon, you need:

1. **Release the addon as a ZIP file** on GitHub Releases
   - The ZIP should contain the addon folder (e.g., `atomic_data_manager/`)
   - Include `blender_manifest.toml` in the root of the addon folder

2. **Update `catalog.json`** with:
   - `id`: Must match the `id` in your `blender_manifest.toml`
   - `version`: Current version (must match manifest)
   - `archive_url`: Direct download URL to the ZIP file (use GitHub Releases)
   - `manifest_url`: URL to the raw `blender_manifest.toml` file

### 4. Add Catalog to Blender

Users (or you) need to add your catalog URL in Blender:

1. Open Blender → Edit → Preferences → Extensions
2. Click "Add Catalog"
3. Enter:
   - **Name**: Your catalog name (e.g., "My Addons")
   - **URL**: `https://your-username.github.io/extension_catalog/catalog.json`
4. Click "Add Catalog"

### 5. Auto-Update Catalog (Optional)

Use the `update_catalog.py` script to automatically generate the catalog from your GitHub releases.

## Catalog Format

The catalog.json follows this structure:

```json
{
  "schema_version": "1.0.0",
  "extensions": [
    {
      "id": "addon_id",
      "version": "1.0.0",
      "archive_url": "https://github.com/user/repo/releases/download/v1.0.0/addon.zip",
      "manifest_url": "https://github.com/user/repo/raw/main/blender_manifest.toml"
    }
  ]
}
```

## Multiple Addons

To add more addons, simply add more entries to the `extensions` array:

```json
{
  "schema_version": "1.0.0",
  "extensions": [
    {
      "id": "atomic_data_manager",
      "version": "2.0.0",
      "archive_url": "https://github.com/grantwilk/atomic-data-manager/releases/download/v2.0.0/atomic_data_manager.zip",
      "manifest_url": "https://github.com/grantwilk/atomic-data-manager/raw/main/blender_manifest.toml"
    },
    {
      "id": "another_addon",
      "version": "1.0.0",
      "archive_url": "https://github.com/user/another-addon/releases/download/v1.0.0/another_addon.zip",
      "manifest_url": "https://github.com/user/another-addon/raw/main/blender_manifest.toml"
    }
  ]
}
```

## Notes

- The `archive_url` must be a direct download link (GitHub Releases provides these)
- The `manifest_url` should point to the raw file on GitHub (use `/raw/` not `/blob/`)
- Version numbers must match between catalog.json and blender_manifest.toml
- Update the catalog.json whenever you release a new version
