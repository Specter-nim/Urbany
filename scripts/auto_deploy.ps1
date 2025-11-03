param(
  [string]$VpsUser = "root",
  [string]$VpsHost = "178.156.143.222",
  [string]$VpsPass = "",
  [string]$LocalProjectPath = "D:/Escritorio/URBANY-MODULO 03/Urbany",
  [string]$RemoteDir = "/opt/urbany",
  [string]$UsernameForToken = "deploy_admin",
  [switch]$NoConfirm
)

$ErrorActionPreference = "Stop"

# === Validaciones previas (seguras y sin diálogos) ===
if (-not $NoConfirm) { Write-Host "[WARN] Use -NoConfirm para ejecución no interactiva" }
if ([string]::IsNullOrWhiteSpace($VpsPass)) { throw "VpsPass es obligatorio para ejecución autónoma" }
if (-not (Test-Path $LocalProjectPath)) { throw "Ruta local no encontrada: $LocalProjectPath" }

function Require-Tool($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { throw "Herramienta requerida no encontrada: $name" }
}

Require-Tool -name "plink"
Require-Tool -name "pscp"
Require-Tool -name "docker"

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$localLog = Join-Path $env:TEMP "urbany_auto_deploy_$timestamp.log"
"[INFO] Inicio despliegue: $timestamp" | Out-File -FilePath $localLog -Encoding UTF8

function ExecPlink($cmd) {
  $hostkey = "ssh-ed25519 255 SHA256:H0nMJI3T2muPPKySw9MxQcEVJ597BngN+8go/FD/Pso"
  Add-Content -Path $localLog -Value "[CMD] $cmd"
  & plink -batch -hostkey "$hostkey" -pw "$VpsPass" "$VpsUser@$VpsHost" $cmd | Tee-Object -FilePath $localLog -Append | Out-Null
}

function ExecPscpUpload($src, $dest) {
  Add-Content -Path $localLog -Value "[UPLOAD] $src -> $dest"
  $target = "{0}@{1}:{2}" -f $VpsUser, $VpsHost, $dest
  $hostkey = "ssh-ed25519 255 SHA256:H0nMJI3T2muPPKySw9MxQcEVJ597BngN+8go/FD/Pso"
  & pscp -batch -hostkey "$hostkey" -pw "$VpsPass" -r "$src" $target | Tee-Object -FilePath $localLog -Append | Out-Null
}

# === Conectividad segura ===
Try { ExecPlink "echo '[CHECK] Conectividad OK'" } Catch { throw "No se pudo conectar al VPS $VpsHost" }

# === Preparar estructura remota ===
ExecPlink "mkdir -p $RemoteDir $RemoteDir/server $RemoteDir/logs $RemoteDir/media $RemoteDir/static"

# === Subir proyecto ===
ExecPscpUpload "$LocalProjectPath/*" "$RemoteDir/"

# === Ajustar permisos ===
ExecPlink "chown -R root:root $RemoteDir && chmod -R 755 $RemoteDir"

# === Validar y actualizar .env con WEB_TAG ===
ExecPlink "test -f $RemoteDir/.env || (echo '❌ Falta .env' && exit 1)"
ExecPlink "grep -q '^WEB_TAG=' $RemoteDir/.env && sed -i 's/^WEB_TAG=.*/WEB_TAG=$timestamp/' $RemoteDir/.env || echo WEB_TAG=$timestamp >> $RemoteDir/.env"
ExecPlink "grep -q '^WEB_IMAGE=' $RemoteDir/.env || echo WEB_IMAGE=urbany/web >> $RemoteDir/.env"

# === Ejecutar despliegue integral (sin TLS detiene? no; usa fallback HTTP) ===
ExecPlink "chmod +x $RemoteDir/server/deploy_full.sh"
ExecPlink "APP_DIR=$RemoteDir COMPOSE_FILE=docker-compose.prod.yml USERNAME=$UsernameForToken $RemoteDir/server/deploy_full.sh >> $RemoteDir/automation.log 2>&1"

# === Generar API Key y documentación de acceso frontend ===
ExecPlink "chmod +x $RemoteDir/server/generate_acceso_frontend.sh"
ExecPlink "$RemoteDir/server/generate_acceso_frontend.sh $UsernameForToken >> $RemoteDir/automation.log 2>&1"

# === Verificaciones automáticas post-despliegue ===
ExecPlink "cd $RemoteDir && docker compose -f docker-compose.prod.yml ps"
ExecPlink "curl -Ik https://localhost/ || curl -Ik http://localhost/"
ExecPlink "curl -Ik https://localhost/api/docs/ || true"
ExecPlink "curl -Ik https://localhost/api/redoc/ || true"

# === Cierre ===
Add-Content -Path $localLog -Value "[INFO] Despliegue completado: $(Get-Date -Format o)"
Write-Host "[OK] Despliegue automatizado completado. Log local: $localLog"