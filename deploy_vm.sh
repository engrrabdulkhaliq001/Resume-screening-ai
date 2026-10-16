#!/bin/bash
# Resume Screening AI - OCI Ubuntu VM Deployment Script
# Target: OCI Ubuntu ARM (158.101.106.119, Port: 8003)

set -e  # Exit on error

echo "🚀 Starting Resume Screening AI Deployment..."
echo "================================================"

# Phase 1: System Update
echo "📦 Phase 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
python3 --version

# Phase 2: Add Swap Space
echo "💾 Phase 2: Adding 4GB swap space..."
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
free -h

# Phase 3: Clone Repository
echo "📁 Phase 3: Cloning repository..."
cd ~
if [ -d "Resume-screening-ai" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd Resume-screening-ai
    git pull
else
    git clone https://github.com/engrrabdulkhaliq001/Resume-screening-ai.git
    cd Resume-screening-ai
fi

# Phase 4: Setup Virtual Environment
echo "🐍 Phase 4: Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Phase 5: Install Dependencies
echo "📦 Phase 5: Installing dependencies..."
pip install -r requirements.txt
pip list | grep -E "fastapi|uvicorn|chromadb|sentence|flashrank|groq"

# Phase 6: Configure Environment
echo "🔑 Phase 6: Configuring environment variables..."
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file - PLEASE EDIT WITH YOUR GROQ_API_KEY"
    cat > .env << 'EOF'
GROQ_API_KEY=your_actual_groq_api_key_here
EOF
    echo "❗ IMPORTANT: Edit .env file and add your Groq API key!"
    echo "   Get your key from: https://console.groq.com"
    read -p "Press Enter after you've updated the .env file with your API key..."
fi

# Phase 7: Pre-download Models
echo "🤖 Phase 7: Pre-downloading ML models..."
cat > download_models.py << 'EOF'
import os
os.environ["HF_HOME"] = "./models_cache"
os.environ["TRANSFORMERS_CACHE"] = "./models_cache"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "./models_cache"

print("Downloading SentenceTransformer model (all-MiniLM-L6-v2)...")
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ SentenceTransformer downloaded successfully")

print("Downloading FlashRank model...")
from flashrank import Ranker
reranker = Ranker()
print("✓ FlashRank downloaded successfully")

print("\n✅ All models downloaded and cached!")
EOF

python download_models.py
rm download_models.py
ls -lh models_cache/

# Phase 8: Create Systemd Service
echo "🔥 Phase 8: Creating systemd service..."
sudo tee /etc/systemd/system/resume-screening.service > /dev/null << 'EOF'
[Unit]
Description=Resume Screening AI Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/Resume-screening-ai/backend
Environment="PATH=/home/ubuntu/Resume-screening-ai/backend/venv/bin"
ExecStart=/home/ubuntu/Resume-screening-ai/backend/venv/bin/gunicorn \
    backend:fapp \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8003 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable resume-screening.service

# Phase 9: Open Firewall Port
echo "🔓 Phase 9: Opening firewall port 8003..."
sudo iptables -I INPUT -p tcp --dport 8003 -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo apt install -y iptables-persistent
sudo netfilter-persistent save
sudo iptables -L -n -v | grep 8003

# Phase 10: Start Service
echo "🚀 Phase 10: Starting service..."
sudo systemctl start resume-screening.service
sleep 10
sudo systemctl status resume-screening.service

# Phase 11: Health Check
echo "✅ Phase 11: Running health check..."
curl http://localhost:8003/

echo ""
echo "================================================"
echo "🎉 Deployment Complete!"
echo "================================================"
echo "📍 API URL: http://158.101.106.119:8003"
echo "📊 Service logs: sudo journalctl -u resume-screening.service -f"
echo "🔧 Restart service: sudo systemctl restart resume-screening.service"
echo "📈 Check status: sudo systemctl status resume-screening.service"
echo ""
echo "Test from external machine:"
echo "curl http://158.101.106.119:8003/"
echo "================================================"
