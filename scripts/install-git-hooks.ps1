param(
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

Push-Location $RepoRoot
try {
    $git = Get-Command git -ErrorAction Stop
    & $git.Source config core.hooksPath .githooks
    Write-Host "Configured git hooks path to .githooks"
    Write-Host "Pre-commit hook will rebuild the addon package before each commit."
}
finally {
    Pop-Location
}
