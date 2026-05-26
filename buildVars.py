# Build variables for NVDA add-on packaging.

addon_info = {
    "addon_name": "bits-easy",
    "addon_summary": "Efficient Accessibility Shortcuts for You",
    "addon_description": "BITS-EASY delivers efficient accessibility shortcuts, clip slots, and merge workflows for NVDA.",
    "addon_version": "1.0.0",
    "addon_author": "AccessWatch",
    "addon_url": "https://github.com/accesswatch/bits-easy",
    "addon_sourceURL": "https://github.com/accesswatch/bits-easy",
    "addon_changelog": "Rebranded to BITS-EASY (Efficient Accessibility Shortcuts for You) with compatibility aliases and stronger package conformance guards.",
    # The packaged help file currently ships as Markdown under addon/doc/en/readme.md.
    "addon_docFileName": "readme.md",
    "addon_minimumNVDAVersion": "2026.1",
    "addon_lastTestedNVDAVersion": "2026.1",
    "addon_updateChannel": "stable",
    "addon_license": "MIT",
    "addon_licenseURL": "https://opensource.org/licenses/MIT",
}

# Python package directories to include from the repository.
python_sources = [
    "src/bits_easy_runtime",
]

# Data directories included in the add-on package.
data_directories = [
    "config/hotkeys",
]

