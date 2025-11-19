#!/bin/bash

# Script untuk build dan push frontend ke Docker Hub
# Jalankan script ini dari folder frontend (Front-End-English-Manajemen)

set -e  # Exit jika ada error

# Konfigurasi
DOCKER_USERNAME="haalzi"
IMAGE_NAME="talentatalk_frontend"
TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

# URL API Backend - GUNAKAN URL EKSTERNAL, BUKAN LOCALHOST
API_BASE_URL="https://talentatalk-be.cloudias79.com"

echo ""
echo "🔧 Building Docker image for frontend..."
echo "📡 API Base URL: ${API_BASE_URL}"
echo "📦 Image Name: ${FULL_IMAGE_NAME}"
echo ""

# Build Docker image dengan build argument
echo "🔨 Building Docker image..."
docker build \
  --build-arg VITE_API_BASE_URL=${API_BASE_URL} \
  -t ${FULL_IMAGE_NAME} \
  .

echo "✅ Docker image built successfully: ${FULL_IMAGE_NAME}"

# Login ke Docker Hub (pastikan sudah login sebelumnya dengan: docker login)
echo "🔐 Checking Docker Hub authentication..."
if ! docker info | grep -q "Username"; then
    echo "❌ Please login to Docker Hub first: docker login"
    exit 1
fi

# Push image ke Docker Hub
echo "🚀 Pushing image to Docker Hub..."
docker push ${FULL_IMAGE_NAME}

echo ""
echo "✅ Frontend image pushed successfully!"
echo "📦 Image: ${FULL_IMAGE_NAME}"
echo ""
echo "🎯 Next steps:"
echo "1. Update your docker-compose.yml to use: ${FULL_IMAGE_NAME}"
echo "2. Run: docker-compose pull && docker-compose up -d talentatalk_frontend"
echo "3. Frontend will be available at: http://your-server-ip:3000"
echo "4. Frontend akan mengakses backend di: ${API_BASE_URL}"
echo ""