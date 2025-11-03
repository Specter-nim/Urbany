param(
  [string]$VpsHost = "178.156.143.222",
  [string]$VpsUser = "root",
  [string]$RemoteDir = "/opt/urbany",
  [string]$ComposeFile = "docker-compose.prod.yml"
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Path $PSScriptRoot -Parent
Set-Location $ProjectDir

Write-Host "[deploy_vps] Construyendo imágenes locales..."
docker compose build

Write-Host "[deploy_vps] Guardando imágenes como tar..."
New-Item -ItemType Directory -Force -Path "$ProjectDir/dist" | Out-Null
docker save urbany/web:latest -o "$ProjectDir/dist/urbany-web.tar"
docker save urbany/celery:latest -o "$ProjectDir/dist/urbany-celery.tar"
docker save urbany/celery-beat:latest -o "$ProjectDir/dist/urbany-celery-beat.tar"

Write-Host "[deploy_vps] Creando directorio remoto: $RemoteDir"
ssh "$VpsUser@$VpsHost" "mkdir -p $RemoteDir $RemoteDir/docker $RemoteDir/dist"

Write-Host "[deploy_vps] Copiando archivos al VPS..."
scp "$ProjectDir/$ComposeFile" "$VpsUser@$VpsHost:$RemoteDir/"
scp "$ProjectDir/docker/nginx.conf" "$VpsUser@$VpsHost:$RemoteDir/docker/nginx.conf"
scp "$ProjectDir/.env" "$VpsUser@$VpsHost:$RemoteDir/.env"
scp "$ProjectDir/dist/urbany-web.tar" "$VpsUser@$VpsHost:$RemoteDir/dist/"
scp "$ProjectDir/dist/urbany-celery.tar" "$VpsUser@$VpsHost:$RemoteDir/dist/"
scp "$ProjectDir/dist/urbany-celery-beat.tar" "$VpsUser@$VpsHost:$RemoteDir/dist/"

Write-Host "[deploy_vps] Cargando imágenes en el VPS..."
ssh "$VpsUser@$VpsHost" "docker load -i $RemoteDir/dist/urbany-web.tar && docker load -i $RemoteDir/dist/urbany-celery.tar && docker load -i $RemoteDir/dist/urbany-celery-beat.tar"

Write-Host "[deploy_vps] Levantando servicios en el VPS..."
ssh "$VpsUser@$VpsHost" "cd $RemoteDir && docker compose -f $ComposeFile up -d"

Write-Host "[deploy_vps] Estado en el VPS:"
ssh "$VpsUser@$VpsHost" "cd $RemoteDir && docker compose -f $ComposeFile ps"

Write-Host "[deploy_vps] Despliegue completado."