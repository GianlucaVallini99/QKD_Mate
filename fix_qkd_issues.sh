#!/bin/bash

echo "==============================================="
echo "🔧 QKD_Mate Issue Resolution Commands"
echo "==============================================="
echo ""
echo "Run these commands on your Ubuntu server:"
echo ""

echo "1. 📋 First, let's examine the cert_manager.py file:"
echo "   cd ~/QKD_mate/QKD_Mate"
echo "   head -20 cert_manager.py"
echo "   grep -n 'cert_templates' cert_manager.py"
echo "   grep -n 'common' cert_manager.py"
echo ""

echo "2. 🌐 Test basic network connectivity:"
echo "   ping -c 3 8.8.8.8"
echo "   ping -c 3 78.40.171.143"
echo "   telnet 78.40.171.143 443"
echo "   curl -v --connect-timeout 10 https://78.40.171.143:443"
echo ""

echo "3. 🔍 Check current configuration:"
echo "   cat node_config.yaml"
echo "   ls -la certs/"
echo ""

echo "4. 📝 List all Python files to understand the structure:"
echo "   ls -la *.py"
echo ""

echo "==============================================="
echo "💡 After running these, we can fix the issues!"
echo "==============================================="