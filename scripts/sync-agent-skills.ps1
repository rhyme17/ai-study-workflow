$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$source = Join-Path $repo "skills\ai-study-workflow"
$targets = @(
    (Join-Path $repo ".codex\skills\ai-study-workflow"),
    (Join-Path $repo ".claude\skills\ai-study-workflow")
)

if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
    throw "Canonical skill not found: $source"
}

foreach ($target in $targets) {
    $resolvedParent = Resolve-Path (Join-Path $target "..")
    if (-not $resolvedParent.Path.StartsWith($repo.Path)) {
        throw "Refusing to sync outside repository: $target"
    }

    if (Test-Path $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    Copy-Item -Path $source -Destination $resolvedParent -Recurse -Force
}

Get-ChildItem -Path $repo -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Output "Synced ai-study-workflow skill to Codex and Claude Code project skill directories."
