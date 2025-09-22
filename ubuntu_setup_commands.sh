#!/bin/bash

echo "==============================================="
echo "🔧 QKD_Mate Ubuntu Server Setup Commands"
echo "==============================================="
echo ""
echo "Run these commands on your Ubuntu server (46.62.149.253):"
echo ""

echo "1. 📦 Install pip and update system:"
echo "   sudo apt update"
echo "   sudo apt install -y python3-pip python3-venv"
echo ""

echo "2. 🔐 Fix certificate permissions:"
echo "   cd ~/QKD_mate/QKD_Mate"
echo "   chmod 600 certs/client_Alice2.key"
echo "   chmod 600 certs/client_Bob2.key"
echo ""

echo "3. 🐍 Install Python dependencies:"
echo "   pip3 install --upgrade pip"
echo "   pip3 install requests urllib3 pyyaml cryptography"
echo ""

echo "4. ✅ Run the setup again:"
echo "   python3 quick_start.py"
echo ""

echo "==============================================="
echo "Alternative: If pip3 doesn't work, try:"
echo "   python3 -m pip install --upgrade pip"
echo "   python3 -m pip install requests urllib3 pyyaml cryptography"
echo "==============================================="