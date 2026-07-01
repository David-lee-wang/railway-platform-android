#!/bin/bash
set -e
echo "=== Railway Platform Deployment Script ==="
echo "Step 1: Install Python dependencies..."
pip3.8 install --upgrade pip 2>&1 | tail -2
pip3.8 install flask sqlalchemy werkzeug flask-login 2>&1 | tail -3

echo ""
echo "Step 2: Create app directory..."
mkdir -p /opt/railway_platform
cd /opt/railway_platform

echo ""
echo "Step 3: Download project files..."
# We'll upload via SCP after SSH works
echo "Waiting for files..."

echo ""
echo "Step 4: Check Nginx..."
which nginx 2>/dev/null && echo "Nginx found" || echo "Installing nginx..." && yum install -y nginx 2>&1 | tail -2

echo ""
echo "=== Environment Ready ==="
