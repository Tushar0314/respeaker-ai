#!/bin/bash

# Run this script ON THE SERVER (echo.cooperativepaddling.com)
# SSH to server first: ssh root@echo.cooperativepaddling.com
# Then run: bash server_test.sh

echo "🔍 Testing Server-Side Configuration..."
echo ""

# Test 1: Check if nginx is running
echo "1️⃣ Checking nginx status..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx is NOT running"
    echo "   Run: systemctl start nginx"
fi
echo ""

# Test 2: Check if port 8080 is listening
echo "2️⃣ Checking if port 8080 is listening..."
if netstat -tlnp | grep -q ":8080"; then
    echo "✅ Port 8080 is listening:"
    netstat -tlnp | grep ":8080"
else
    echo "❌ Port 8080 is NOT listening"
    echo "   SSH tunnel may not be connected"
fi
echo ""

# Test 3: Test local access to stream
echo "3️⃣ Testing local access to stream endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/stream)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Stream accessible at localhost:8080/stream (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "❌ Cannot connect to localhost:8080"
    echo "   SSH tunnel is not forwarding properly"
else
    echo "⚠️  Got HTTP $HTTP_CODE from localhost:8080/stream"
fi
echo ""

# Test 4: Check nginx configuration
echo "4️⃣ Checking nginx configuration..."
if nginx -t 2>&1 | grep -q "syntax is ok"; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors:"
    nginx -t
fi
echo ""

# Test 5: Test public access
echo "5️⃣ Testing public access..."
PUBLIC_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://echo.cooperativepaddling.com/stream)
echo "   Public URL returns HTTP $PUBLIC_CODE"
echo ""

echo "📋 If stream is working locally but not publicly:"
echo "   1. Check nginx config: cat /etc/nginx/sites-available/default"
echo "   2. Restart nginx: systemctl restart nginx"
echo "   3. Check logs: tail -f /var/log/nginx/error.log"
