# PPT Pro Studio — one-click installer (MIT-0) for Windows (PowerShell).
# Copies this skill folder into the first detected agent "skills" directory,
# or into a path you pass as the first argument.
#
# Usage:
#   .\install.ps1                 # auto-detect target skills dir
#   .\install.ps1 C:\path\to\skills  # explicit target dir
$ErrorActionPreference = "Stop"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SkillName  = "ppt-pro-studio"

$Target = $args[0]
if (-not $Target) {
    $cands = @(
        "$env:USERPROFILE\.workbuddy\skills",
        "$env:USERPROFILE\.claude\skills",
        "$env:USERPROFILE\.cursor\skills",
        "$env:USERPROFILE\.codex\skills"
    )
    foreach ($d in $cands) { if (Test-Path $d) { $Target = $d; break } }
}
if (-not $Target) { $Target = "$env:USERPROFILE\.workbuddy\skills" }

New-Item -ItemType Directory -Force -Path $Target | Out-Null
Copy-Item -Path $ScriptDir -Destination (Join-Path $Target $SkillName) -Recurse -Force

Write-Host "Installed PPT Pro Studio -> $(Join-Path $Target $SkillName)"
Write-Host ""
Write-Host "Requirements:"
Write-Host "  - python3 + python-pptx   (pip install python-pptx)   [primary renderer + ⑥-B]"
Write-Host "  - node >= 18              (for the optional MCP server)"
Write-Host ""
Write-Host "Premium path ⑥-B (SVG->PPTX) is self-contained: vendor/ppt-master-scripts is bundled."
Write-Host ""
Write-Host "Quick start:"
Write-Host "  python3 $(Join-Path $Target $SkillName)\scripts\ppt_studio_generate.py $(Join-Path $Target $SkillName)\examples\sample-brief.json --out deck.pptx"
