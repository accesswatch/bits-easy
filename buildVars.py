# Build variables for NVDA add-on packaging.

addon_info = {
    "addon_name": "spellforgeHotkeys",
    "addon_summary": "Spellforge Hotkeys and Selection Toolkit",
    "addon_description": "Selection-first hotkeys, clip slots, and merge workflows for NVDA.",
    "addon_version": "1.0.0",
    "addon_author": "AccessWatch",
    "addon_url": "https://github.com/accesswatch/bits-easy",
    "addon_sourceURL": "https://github.com/accesswatch/bits-easy",
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2026.1",
    "addon_lastTestedNVDAVersion": "2026.1",
    "addon_updateChannel": "stable",
    "addon_license": "MIT",
    "addon_licenseURL": "https://opensource.org/licenses/MIT",
}

# Python package directories to include from the repository.
python_sources = [
    "src/spellforge_runtime",
]

# Data directories included in the add-on package.
data_directories = [
    "config/hotkeys",
]
