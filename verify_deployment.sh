#!/bin/bash
# Resume Screening AI - Deployment Verification Script

echo "🔍 Running Deployment Verification..."
echo "======================================"

# Test 1: Check Service Status
echo "📊 Test 1: Checking service status..."
sudo systemctl status resume-screening.service --no-pager

# Test 2: Check API Root
echo ""
echo "🌐 Test 2: Testing API root endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:8003/)
echo "$ROOT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ROOT_RESPONSE"

# Test 3: Check Collection Info
echo ""
echo "📁 Test 3: Checking collection info..."
COLLECTION_RESPONSE=$(curl -s http://localhost:8003/collection-info)
echo "$COLLECTION_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$COLLECTION_RESPONSE"

# Test 4: Upload Sample JD
echo ""
echo "📝 Test 4: Uploading sample job description..."
JD_RESPONSE=$(curl -s -X POST http://localhost:8003/upload-jd \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We need a Python developer with FastAPI and ML experience.",
    "skills_required": ["python", "fastapi", "docker"],
    "experience_years": 3,
    "education": "bachelors"
  }')
echo "$JD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$JD_RESPONSE"

# Test 5: Check Root Again (should show JD title)
echo ""
echo "🔄 Test 5: Checking root endpoint after JD upload..."
ROOT_RESPONSE_2=$(curl -s http://localhost:8003/)
echo "$ROOT_RESPONSE_2" | python3 -m json.tool 2>/dev/null || echo "$ROOT_RESPONSE_2"

# Test 6: Resource Usage
echo ""
echo "💾 Test 6: Checking resource usage..."
echo "Memory:"
free -h
echo ""
echo "Disk:"
df -h
echo ""
echo "CPU:"
top -bn1 | head -10

# Test 7: Service Logs (last 20 lines)
echo ""
echo "📋 Test 7: Last 20 lines of service logs..."
sudo journalctl -u resume-screening.service -n 20 --no-pager

echo ""
echo "======================================"
echo "✅ Verification Complete!"
echo "======================================"
