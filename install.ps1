# Install this skill and its slash commands on Windows for Claude Code and/or Codex CLI.
#
# Usage (PowerShell, from the repo folder):
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 [claude|codex|all]   (default: all)
#
#   Claude Code: ~\.claude\skills\job-hunting  +  ~\.claude\commands\<cmd>.md
#   Codex CLI:   ~\.codex\skills\job-hunting   +  ~\.codex\prompts\<cmd>.md
#
# The skill folder is a directory junction (no admin rights needed), so
# `git pull` updates it. Command files are copied, so rerun this after a pull.
param([ValidateSet("claude", "codex", "all")][string]$Target = "all")
$ErrorActionPreference = "Stop"

$Src = $PSScriptRoot

function Install-To($HomeDir, $CmdSub) {
    $skills = Join-Path $HomeDir "skills"
    $cmds = Join-Path $HomeDir $CmdSub
    New-Item -ItemType Directory -Force -Path $skills, $cmds | Out-Null

    $link = Join-Path $skills "job-hunting"
    if (Test-Path $link) { (Get-Item $link).Delete() }   # removes the junction, not the repo
    New-Item -ItemType Junction -Path $link -Target $Src | Out-Null

    Copy-Item (Join-Path $Src "commands\*.md") $cmds -Force
    Write-Host "installed -> $link and $cmds"
}

$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
if ($Target -in "claude", "all") { Install-To (Join-Path $HOME ".claude") "commands" }
if ($Target -in "codex", "all")  { Install-To $codexHome "prompts" }

# Python venv with openpyxl, same location ensure_venv.sh uses.
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) { Write-Warning "Python not found. Install Python 3.9+ from python.org, then rerun."; exit 1 }

$venv = Join-Path $Src ".venv"
$vpy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $vpy)) { & $py.Source -m venv $venv }
& $vpy -m pip install --quiet --upgrade pip 2>$null
& $vpy -m pip install --quiet openpyxl
Write-Host "python venv ready: $vpy"

if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
    Write-Warning "bash not found. render.sh, new_packet.sh and ensure_venv.sh need Git Bash (comes with Git for Windows: https://git-scm.com/download/win)."
}
