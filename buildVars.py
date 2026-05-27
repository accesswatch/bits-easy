# Build variables for NVDA add-on packaging.


def _(message: str) -> str:
    return message

addon_info = {
    "addon_name": "bits-easy",
    # Translators: Add-on title shown in Add-on Store and installation UI.
    "addon_summary": _("Efficient Accessibility Shortcuts for You"),
    # Translators: Add-on description shown in Add-on Store details.
    "addon_description": _("BITS-EASY delivers efficient accessibility shortcuts, clip slots, and merge workflows for NVDA."),
    "addon_version": "1.0.0",
    "addon_author": "AccessWatch",
    "addon_url": "https://github.com/accesswatch/bits-easy",
    "addon_sourceURL": "https://github.com/accesswatch/bits-easy",
    # Translators: Short changelog shown for this add-on release in Add-on Store.
    "addon_changelog": _("Rebranded to BITS-EASY (Efficient Accessibility Shortcuts for You) with compatibility aliases and stronger package conformance guards."),
    # The packaged help file currently ships as Markdown under addon/doc/en/readme.md.
    "addon_docFileName": "readme.md",
    "addon_minimumNVDAVersion": "2026.1",
    "addon_lastTestedNVDAVersion": "2026.1",
    "addon_updateChannel": "stable",
    "addon_license": "GPL v2",
    "addon_licenseURL": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
}

# Python sources to include in NVDA add-on packaging and translation extraction.
pythonSources = [
    "addon/globalPlugins/*.py",
    "addon/bits_easy_settings.py",
    "addon/installTasks.py",
    "src/bits_easy_runtime/*.py",
]
python_sources = pythonSources

# Data directories included in the add-on package.
data_directories = [
    "config/hotkeys",
    "config/features",
]

# Files containing strings that should be extracted for translation.
i18nSources = [
    "addon/globalPlugins/*.py",
    "addon/bits_easy_settings.py",
    "addon/installTasks.py",
    "buildVars.py",
]
i18n_sources = i18nSources

# Base language for UI and documentation strings.
baseLanguage = "en"
base_language = baseLanguage

# Markdown build extensions for add-on documentation.
markdownExtensions = []
markdown_extensions = markdownExtensions

