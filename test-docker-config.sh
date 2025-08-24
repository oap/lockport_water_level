#!/bin/bash

# Docker configuration test script

echo "🧪 Testing Docker configuration..."

# Check if required files exist
echo "📁 Checking required files..."

files=("Dockerfile" "docker-compose.yml" ".dockerignore" "requirements.txt" "app.py")
missing_files=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        missing_files=$((missing_files + 1))
    fi
done

# Check if data directory exists
if [ -d "data" ]; then
    echo "  ✅ data/ directory exists"
else
    echo "  ❌ data/ directory missing"
    missing_files=$((missing_files + 1))
fi

# Validate Dockerfile syntax
echo "🔍 Validating Dockerfile..."
if grep -q "FROM python:" Dockerfile && grep -q "EXPOSE 80" Dockerfile; then
    echo "  ✅ Dockerfile appears valid"
else
    echo "  ❌ Dockerfile may have issues"
    missing_files=$((missing_files + 1))
fi

# Check docker-compose.yml
echo "🔍 Validating docker-compose.yml..."
if grep -q "version:" docker-compose.yml && grep -q "80:80" docker-compose.yml; then
    echo "  ✅ docker-compose.yml appears valid"
else
    echo "  ❌ docker-compose.yml may have issues"
    missing_files=$((missing_files + 1))
fi

# Check app.py for correct port
echo "🔍 Checking Flask app configuration..."
if grep -q "port=80" app.py; then
    echo "  ✅ Flask app configured for port 80"
else
    echo "  ❌ Flask app not configured for port 80"
    missing_files=$((missing_files + 1))
fi

# Summary
echo ""
if [ $missing_files -eq 0 ]; then
    echo "🎉 All Docker configuration tests passed!"
    echo "📝 Ready for deployment with: ./deploy.sh"
else
    echo "⚠️  Found $missing_files issues that need to be fixed"
fi
