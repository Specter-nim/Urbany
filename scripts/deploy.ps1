param(
  [ValidateSet("build","up","status","logs","down")]
  [string]$Action = "up"
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Path $PSScriptRoot -Parent
Set-Location $ProjectDir

function Build {
  Write-Host "[deploy] Construyendo imágenes..."
  docker compose build
}

function Up {
  Write-Host "[deploy] Levantando contenedores..."
  docker compose up -d
}

function Status {
  Write-Host "[deploy] Estado de servicios:"
  docker compose ps
}

function Logs {
  Write-Host "[deploy] Logs de 'web' (Ctrl+C para salir)"
  docker compose logs -f web
}

function Down {
  Write-Host "[deploy] Deteniendo contenedores..."
  docker compose down
}

switch ($Action) {
  "build" { Build }
  "up" { Build; Up; Status }
  "status" { Status }
  "logs" { Logs }
  "down" { Down }
}