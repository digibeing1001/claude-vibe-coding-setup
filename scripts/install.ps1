param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ArgsForInstaller
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & py -3 (Join-Path $Root "scripts\install-universal.py") @ArgsForInstaller
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python (Join-Path $Root "scripts\install-universal.py") @ArgsForInstaller
    exit $LASTEXITCODE
}

throw "Python 3 is required to run the portable installer."
