# Feature Flags and Beta Access

BITS-EASY supports remote feature flag retrieval with a local fallback manifest bundled in the add-on package.

The design goal is magical for users and boring for operations: new capability appears when authorized, while stable users remain predictably safe.

## How It Works

1. On startup, BITS-EASY loads feature flags from the local cache if available.
2. If cache is unavailable, it loads the bundled fallback manifest shipped in the add-on.
3. You can refresh from a remote JSON manifest URL when internet is available.
4. If remote retrieval fails, BITS-EASY automatically falls back to cache, then to bundled fallback.

## Why This Matters

1. Stable users stay on stable features.
2. Beta users can be granted authority with an access code.
3. Feature rollouts can be enabled or disabled without shipping a new add-on package.
4. Disabled features automatically disable associated key bindings.

## Experience Contract

1. No surprise upgrades into risky behavior.
2. No orphan hotkeys for disabled features.
3. No internet dependency for baseline operation.
4. No hidden authority changes.

## Commands

1. cmd.feature.flags.list
2. cmd.feature.flags.enable (flagId)
3. cmd.feature.flags.disable (flagId)
4. cmd.feature.flags.clearOverride (flagId)
5. cmd.feature.flags.refreshManifest (manifestUrl, timeoutSeconds)
6. cmd.feature.flags.grantBeta (accessCode)
7. cmd.feature.flags.setAuthority (stable|beta|internal)

## Manifest Shape (JSON)

```json
{
  "version": "1",
  "source": "fallback",
  "authorityStages": {
    "stable": ["stable"],
    "beta": ["stable", "beta"],
    "internal": ["stable", "beta", "experimental"]
  },
  "flags": [
    {
      "id": "htmlAssistantWizard",
      "name": "HTML Assistant Wizard",
      "description": "Guided HTML assistant flow commands.",
      "stage": "beta",
      "enabledByDefault": false,
      "commandIds": ["cmd.author.html.assistant", "cmd.author.html.assistantList"]
    },
    {
      "id": "tableCaptureGranular",
      "name": "Table Capture Granular",
      "description": "Row/column/header/cell table capture commands.",
      "stage": "beta",
      "enabledByDefault": false,
      "commandIds": [
        "cmd.table.capture.row",
        "cmd.table.capture.column",
        "cmd.table.capture.header",
        "cmd.table.capture.cell"
      ]
    },
    {
      "id": "emojiAssistant",
      "name": "Emoji Assistant",
      "description": "Search and insert emoji by alias.",
      "stage": "beta",
      "enabledByDefault": false,
      "commandIds": ["cmd.emoji.list", "cmd.emoji.insert"]
    }
  ],
  "grants": [
    {
      "name": "preview-2026",
      "sha256": "<sha256-of-access-code>",
      "authority": "beta",
      "enableFlags": ["htmlAssistantWizard", "tableCaptureGranular", "emojiAssistant"]
    }
  ]
}
```

## Remote Retrieval

Use either:

1. Environment variable: BITS_EASY_FEATURE_FLAGS_URL
2. Runtime command: cmd.feature.flags.refreshManifest with manifestUrl

## Bundled Fallback

Bundled file in package:

1. config/features/feature-flags.fallback.v1.json

This guarantees deterministic behavior when internet is not available.
