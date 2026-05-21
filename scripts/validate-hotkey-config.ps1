$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot

$schemaDir = Join-Path $repoRoot 'schemas/hotkeys'
$configDir = Join-Path $repoRoot 'config/hotkeys'

$commandSchema = Join-Path $schemaDir 'command-metadata.schema.json'
$globalKeymapSchema = Join-Path $schemaDir 'global-keymap.schema.json'
$profileSchema = Join-Path $schemaDir 'profile-overrides.schema.json'

$commandCatalogFile = Join-Path $configDir 'commands/tier1-commands.v1.json'
$globalKeymapFile = Join-Path $configDir 'global-keymap.v1.json'
$profileFiles = @(
    (Join-Path $configDir 'profiles/beginner.json'),
    (Join-Path $configDir 'profiles/balanced.json'),
    (Join-Path $configDir 'profiles/expert.json')
)

$errors = New-Object System.Collections.Generic.List[string]

function Add-ValidationError {
    param([string]$Message)
    $errors.Add($Message)
}

function Validate-JsonSyntax {
    param([string]$FilePath)
    try {
        $content = Get-Content -Raw -Path $FilePath
        $null = $content | Test-Json
    }
    catch {
        Add-ValidationError("Invalid JSON syntax in '$FilePath': $($_.Exception.Message)")
    }
}

function Validate-AgainstSchema {
    param(
        [string]$FilePath,
        [string]$SchemaPath
    )

    try {
        $content = Get-Content -Raw -Path $FilePath
        $isValid = $content | Test-Json -SchemaFile $SchemaPath
        if (-not $isValid) {
            Add-ValidationError("Schema validation failed for '$FilePath' against '$SchemaPath'.")
        }
    }
    catch {
        Add-ValidationError("Schema validation error for '$FilePath': $($_.Exception.Message)")
    }
}

function Validate-CommandCatalog {
    param(
        [string]$CatalogPath,
        [string]$SchemaPath
    )

    try {
        $catalog = Get-Content -Raw -Path $CatalogPath | ConvertFrom-Json
        if ($catalog -isnot [System.Collections.IEnumerable]) {
            Add-ValidationError("Command catalog must be an array: '$CatalogPath'.")
            return
        }

        $index = 0
        foreach ($command in $catalog) {
            $index += 1
            $json = $command | ConvertTo-Json -Depth 10
            $isValid = $json | Test-Json -SchemaFile $SchemaPath
            if (-not $isValid) {
                Add-ValidationError("Command catalog item $index failed schema validation in '$CatalogPath'.")
            }
        }

        $ids = @($catalog | ForEach-Object { $_.id })
        $duplicateIds = $ids | Group-Object | Where-Object { $_.Count -gt 1 }
        foreach ($dup in $duplicateIds) {
            Add-ValidationError("Duplicate command id '$($dup.Name)' found in '$CatalogPath'.")
        }
    }
    catch {
        Add-ValidationError("Unable to parse command catalog '$CatalogPath': $($_.Exception.Message)")
    }
}

function Validate-KeymapReferences {
    param(
        [string]$CatalogPath,
        [string]$KeymapPath
    )

    try {
        $catalog = Get-Content -Raw -Path $CatalogPath | ConvertFrom-Json
        $keymap = Get-Content -Raw -Path $KeymapPath | ConvertFrom-Json

        $ids = @{}
        foreach ($command in $catalog) {
            $ids[$command.id] = $true
        }

        foreach ($binding in $keymap.bindings) {
            if (-not $ids.ContainsKey($binding.commandId)) {
                Add-ValidationError("Keymap references unknown command id '$($binding.commandId)' in '$KeymapPath'.")
            }
        }
    }
    catch {
        Add-ValidationError("Unable to validate cross-file references: $($_.Exception.Message)")
    }
}

$allFiles = @(
    $commandSchema,
    $globalKeymapSchema,
    $profileSchema,
    $commandCatalogFile,
    $globalKeymapFile
) + $profileFiles

foreach ($file in $allFiles) {
    if (-not (Test-Path -Path $file)) {
        Add-ValidationError("Missing required file: '$file'.")
    }
}

if ($errors.Count -eq 0) {
    Validate-JsonSyntax -FilePath $commandSchema
    Validate-JsonSyntax -FilePath $globalKeymapSchema
    Validate-JsonSyntax -FilePath $profileSchema

    Validate-JsonSyntax -FilePath $commandCatalogFile
    Validate-JsonSyntax -FilePath $globalKeymapFile
    foreach ($profile in $profileFiles) {
        Validate-JsonSyntax -FilePath $profile
    }

    Validate-AgainstSchema -FilePath $globalKeymapFile -SchemaPath $globalKeymapSchema
    foreach ($profile in $profileFiles) {
        Validate-AgainstSchema -FilePath $profile -SchemaPath $profileSchema
    }

    Validate-CommandCatalog -CatalogPath $commandCatalogFile -SchemaPath $commandSchema
    Validate-KeymapReferences -CatalogPath $commandCatalogFile -KeymapPath $globalKeymapFile
}

if ($errors.Count -gt 0) {
    Write-Host ''
    Write-Host 'Hotkey config validation failed:' -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host " - $err" -ForegroundColor Red
    }
    exit 1
}

Write-Host 'Hotkey config validation passed.' -ForegroundColor Green
