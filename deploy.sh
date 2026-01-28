#!/bin/bash

# Render Deployment Script for Growny-AI
echo "🚀 Starting deployment process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend && npm install

# Build frontend for production
echo "🔨 Building frontend for production..."
npm run build

# Copy built frontend to backend static folder
echo "📁 Copying frontend build to backend..."
mkdir -p ../backend/static
cp -r dist/* ../backend/static/

echo "✅ Build complete!"
echo "🌐 Starting FastAPI server..."
cd ../backend && python main.py
