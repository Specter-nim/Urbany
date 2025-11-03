param(
  [string]$VpsUser = "root",
  [string]$VpsHost = "178.156.143.222",
  [string]$LocalProjectPath = "D:/Escritorio/URBANY-MODULO 03/Urbany",
  [string]$RemoteDir = "/opt/urbany",
  [string]$VpsPass = ""
)

$ErrorActionPreference = "Stop"

Write-Host "📁 Validando ruta local del proyecto: $LocalProjectPath"
if (-not (Test-Path $LocalProjectPath)) {
  Write-Error "No existe la ruta local $LocalProjectPath"
}

Write-Host "📁 Creando estructura de carpetas en el VPS..."
if ((Get-Command plink -ErrorAction SilentlyContinue) -and $VpsPass) {
  plink -pw "$VpsPass" "$VpsUser@$VpsHost" "mkdir -p $RemoteDir && mkdir -p $RemoteDir/server && mkdir -p $RemoteDir/logs && mkdir -p $RemoteDir/media && mkdir -p $RemoteDir/static"
} else {
  ssh "$VpsUser@$VpsHost" "mkdir -p $RemoteDir && mkdir -p $RemoteDir/server && mkdir -p $RemoteDir/logs && mkdir -p $RemoteDir/media && mkdir -p $RemoteDir/static"
}

Write-Host "⬆️ Subiendo proyecto completo al VPS..."
if ((Get-Command pscp -ErrorAction SilentlyContinue) -and $VpsPass) {
  pscp -pw "$VpsPass" -r "$LocalProjectPath/*" "$VpsUser@$VpsHost:$RemoteDir/"
} else {
  scp -r "$LocalProjectPath/." "$VpsUser@$VpsHost:$RemoteDir/"
}

Write-Host "🔒 Configurando permisos..."
if ((Get-Command plink -ErrorAction SilentlyContinue) -and $VpsPass) {
  plink -pw "$VpsPass" "$VpsUser@$VpsHost" "chown -R root:root $RemoteDir && chmod -R 755 $RemoteDir"
} else {
  ssh "$VpsUser@$VpsHost" "chown -R root:root $RemoteDir && chmod -R 755 $RemoteDir"
}

$remoteScript = @'
cd /opt/urbany

echo "✅ Validando docker-compose.prod.yml..."
if [ ! -f "docker-compose.prod.yml" ]; then
  echo "❌ Error: no se encontró docker-compose.prod.yml en /opt/urbany"
  exit 1
fi

echo "🛑 Deteniendo contenedores previos (si existen)..."
docker compose -f docker-compose.prod.yml down || true

echo "⚙️ Construyendo imágenes Docker (esto puede tardar unos minutos)..."
docker compose -f docker-compose.prod.yml build

echo "🚀 Iniciando servicios con docker compose..."
docker compose -f docker-compose.prod.yml up -d

echo "\n📦 Estado final de contenedores:"
docker compose -f docker-compose.prod.yml ps

echo "\n🧾 Logs iniciales (últimas 50 líneas de 'web'):"
docker compose -f docker-compose.prod.yml logs --tail=50 web || true

echo "\n📁 Contenido actual de /opt/urbany:"
ls -lah /opt/urbany
'@

Write-Host "🐳 Construyendo y levantando contenedores en el VPS..."
if ((Get-Command plink -ErrorAction SilentlyContinue) -and $VpsPass) {
  $tempScriptPath = [System.IO.Path]::GetTempFileName()
  [System.IO.File]::WriteAllText($tempScriptPath, $remoteScript)
  plink -pw "$VpsPass" -m $tempScriptPath "$VpsUser@$VpsHost"
  Remove-Item $tempScriptPath -Force
} else {
  ssh "$VpsUser@$VpsHost" "$remoteScript"
}

Write-Host "✅ Despliegue completado. Usa /opt/urbany/server/generate_acceso_frontend.sh para generar ACCESO_FRONTEND.md."