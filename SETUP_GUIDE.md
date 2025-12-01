# Quick Setup Guide: Blender Extension Catalog

This guide will help you set up your own Blender extension catalog on GitHub Pages so users can update your addons directly from Blender.

## Step-by-Step Setup

### Step 1: Create a GitHub Pages Repository

1. Create a new repository on GitHub (e.g., `blender-extensions` or `your-username.github.io`)
2. Clone it locally:
   ```bash
   git clone https://github.com/your-username/blender-extensions.git
   cd blender-extensions
   ```

### Step 2: Copy the Catalog Files

Copy the `extension_catalog` folder contents to your new repository:

```bash
# From your atomic_data_manager directory
cp -r extension_catalog/* /path/to/blender-extensions/
```

### Step 3: Configure Your Addons

Edit `update_catalog.py` and update the `ADDONS` list:

```python
ADDONS = [
    {
        "id": "atomic_data_manager",
        "repo": "grantwilk/atomic-data-manager",
        "manifest_branch": "main",
    },
    {
        "id": "your_other_addon",
        "repo": "your-username/your-other-addon",
        "manifest_branch": "main",
    },
]
```

### Step 4: Generate Initial Catalog

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the update script:
   ```bash
   python update_catalog.py
   ```

3. This creates/updates `catalog.json` with your addons.

### Step 5: Enable GitHub Pages

1. Go to your repository → Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: `main` (or `gh-pages`)
4. Folder: `/ (root)`
5. Save

Your catalog will be available at:
`https://your-username.github.io/blender-extensions/catalog.json`

### Step 6: Test in Blender

1. Open Blender → Edit → Preferences → Extensions
2. Click "Add Catalog"
3. Enter:
   - **Name**: "My Addons" (or your choice)
   - **URL**: `https://your-username.github.io/blender-extensions/catalog.json`
4. Click "Add Catalog"
5. Your addons should appear in the Extensions list!

### Step 7: Set Up Auto-Updates (Optional)

The GitHub Actions workflow will automatically update the catalog:

1. The workflow runs daily to check for new releases
2. You can also manually trigger it: Actions → "Update Extension Catalog" → "Run workflow"
3. When a new release is published, the catalog updates automatically

## Publishing New Versions

When you release a new version of an addon:

1. **Create a GitHub Release** with a ZIP file containing your addon
   - Tag format: `v2.0.0` or `2.0.0` (both work)
   - Upload a ZIP file or let GitHub create the source archive

2. **Update your `blender_manifest.toml`** with the new version:
   ```toml
   version = "2.0.0"
   ```

3. **The catalog will auto-update** (if using GitHub Actions) or run:
   ```bash
   python update_catalog.py
   git add catalog.json
   git commit -m "Update catalog for v2.0.0"
   git push
   ```

## Troubleshooting

### Catalog not showing in Blender
- Check the catalog URL is accessible in a browser
- Verify the JSON is valid: https://jsonlint.com/
- Ensure `schema_version` is `"1.0.0"`

### Updates not appearing
- Make sure the version in `catalog.json` is higher than the installed version
- Check that `archive_url` is a direct download link (not a redirect)
- Verify `manifest_url` uses `/raw/` not `/blob/`

### ZIP file issues
- The ZIP should contain the addon folder (e.g., `atomic_data_manager/`)
- Include `blender_manifest.toml` in the addon root
- Test the ZIP by manually installing it in Blender first

## Multiple Repositories

If your addons are in different repositories, just add them all to the `ADDONS` list in `update_catalog.py`. The script will fetch releases from all of them and combine them into one catalog.

## Security Notes

- GitHub Pages serves static files only (no server-side code)
- The catalog is public JSON (anyone can read it)
- Users download directly from your GitHub Releases
- No authentication required (Blender extension system doesn't support it)
