# Script untuk build dan push frontend ke Docker Hub (PowerShell)
# Jalankan script ini dari folder frontend (FE-KoTA106)

# Konfigurasi
$DOCKER_USERNAME = "haalzi"
$IMAGE_NAME = "talentatalk_frontend"
$TAG = "latest"
$FULL_IMAGE_NAME = "${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

# URL API Backend - GUNAKAN URL EKSTERNAL, BUKAN LOCALHOST
$API_BASE_URL = "https://talentatalk-be.cloudias79.com"

Write-Host ""
Write-Host "🔧 Building Docker image for frontend..." -ForegroundColor Cyan
Write-Host "📡 API Base URL: $API_BASE_URL" -ForegroundColor Yellow
Write-Host "📦 Image Name: $FULL_IMAGE_NAME" -ForegroundColor Yellow
Write-Host ""

try {
    # Build Docker image dengan build argument
    Write-Host "🔨 Building Docker image..." -ForegroundColor Green
    docker build --build-arg VITE_API_BASE_URL=$API_BASE_URL -t $FULL_IMAGE_NAME .
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed"
    }
    
    Write-Host "✅ Docker image built successfully: $FULL_IMAGE_NAME" -ForegroundColor Green
    Write-Host ""
    
    # Push image ke Docker Hub
    Write-Host "🚀 Pushing image to Docker Hub..." -ForegroundColor Cyan
    docker push $FULL_IMAGE_NAME
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker push failed"
    }
    
    Write-Host ""
    Write-Host "✅ Frontend image pushed successfully!" -ForegroundColor Green
    Write-Host "📦 Image: $FULL_IMAGE_NAME" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🎯 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Update your docker-compose.yml to use: $FULL_IMAGE_NAME"
    Write-Host "2. Run: docker-compose pull && docker-compose up -d talentatalk_frontend"
    Write-Host "3. Frontend will be available at: http://your-server-ip:3000"
    Write-Host "4. Frontend akan mengakses backend di: $API_BASE_URL"
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "- Make sure Docker is running"
    Write-Host "- Make sure you're logged in: docker login"
    Write-Host "- Check if Dockerfile exists in current directory"
    Write-Host "- Pastikan backend accessible di: $API_BASE_URL"
    Write-Host ""
}

Read-Host "Press Enter to continue"