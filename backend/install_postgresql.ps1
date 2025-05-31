# Script PowerShell para instalação do PostgreSQL
# Execute como Administrador

Write-Host "🗄️  Instalador do PostgreSQL para Music List System" -ForegroundColor Cyan
Write-Host "=" * 55 -ForegroundColor Cyan

# Verificar se está executando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com o botão direito no PowerShell e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    exit 1
}

# Verificar se Chocolatey está instalado
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Instalando Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Instalar PostgreSQL
Write-Host "🗄️  Instalando PostgreSQL..." -ForegroundColor Yellow
$password = Read-Host "Digite uma senha para o usuário 'postgres'" -AsSecureString
$passwordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

try {
    choco install postgresql --params "/Password:$passwordText" -y
    Write-Host "✅ PostgreSQL instalado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro na instalação do PostgreSQL: $_" -ForegroundColor Red
    exit 1
}

# Aguardar o serviço iniciar
Write-Host "⏳ Aguardando o serviço PostgreSQL iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar se o serviço está rodando
$service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq "Running") {
    Write-Host "✅ Serviço PostgreSQL está rodando!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Serviço PostgreSQL não está rodando. Tentando iniciar..." -ForegroundColor Yellow
    try {
        Start-Service -Name "postgresql*"
        Write-Host "✅ Serviço PostgreSQL iniciado!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erro ao iniciar o serviço PostgreSQL: $_" -ForegroundColor Red
    }
}

# Atualizar PATH
$env:PATH += ";C:\Program Files\PostgreSQL\15\bin"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::Machine)

Write-Host ""
Write-Host "🎉 Instalação concluída!" -ForegroundColor Green
Write-Host "Agora você pode:" -ForegroundColor Cyan
Write-Host "1. Executar: python setup_database.py" -ForegroundColor White
Write-Host "2. Configurar o arquivo .env com PostgreSQL" -ForegroundColor White
Write-Host "3. Instalar psycopg2-binary: pip install psycopg2-binary" -ForegroundColor White
Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 