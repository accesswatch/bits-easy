# BITS-EASY Release Notes Draft

## Version
- Version: 1.0.0
- Date: 2026-05-27
- Commit: c8e7fde

## Summary
This release finalizes NVDA add-on guideline parity work and prepares an offline Leasey documentation set for feature comparison and review.

## User-facing Improvements
- Improved spoken and braille announcement routing for runtime narration payloads.
- Added browse-style help rendering support for long virtual-view content.
- Expanded settings and command-surface messaging consistency.

## Accessibility and Localization
- Added translation initialization in add-on modules.
- Wrapped user-facing add-on strings for translation readiness.
- Added locale scaffolding at addon/locale/en/LC_MESSAGES.
- Added translated manifest template support.

## Packaging and Compliance
- Updated add-on metadata to GPL v2 and aligned license URL.
- Added GPL v2 license text file and ensured packaging includes it.
- Updated build and staging scripts to include locale and license assets.
- Hardened ignore rules for downloaded reference material and build/test artifacts.

## Offline Parity Research Assets
- Added an offline Leasey documentation mirror under docs/downloads/leasey/hartgenscripts.
- Added SOURCES.txt manifest mapping source URLs to local files.

## Validation
- Build: python scripts/build_addon.py --output-dir dist
- Tests: pytest tests/test_dispatcher_integration.py -q
- Artifact verified: dist/bits-easy-1.0.0.nvda-addon includes COPYING.txt

## Compatibility
- minimumNVDAVersion: 2026.1
- lastTestedNVDAVersion: 2026.1

## Notes for Final Release Edit
- Confirm whether release notes should list all internal files or only user-visible changes.
- Confirm whether Leasey mirror files should remain in repository history or move to an external archive.
- Confirm whether this draft should be copied into changelog fields for add-on store submission.
