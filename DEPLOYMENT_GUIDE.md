# 🚀 Resume Screening AI - OCI Ubuntu VM Deployment Guide

**Target VM:** OCI Ubuntu ARM (158.101.106.119, Port: 8003)
**RAM:** 6 GB ARM (with Squarely and ClearWay services running)

---

## 📋 Phase 1: Code Architecture Analysis Summary

### ✅ What We Found:
- **Backend:** FastAPI with ChromaDB, SentenceTransformers, FlashRank, Groq LLaMA 3
- **Dependencies:** Missing critical packages in requirements.txt (chromadb, sentence-transformers, flashrank, numpy, gunicorn)
- **Models:** Local models (all-MiniLM-L6-v2 ~80MB, FlashRank ~150MB) need download
- **Issues Fixed:**
  - Added missing dependencies to requirements.txt
  - Added HuggingFace cache directory control to manage disk space
  - Created .env.example template
  - Optimized for single-worker deployment (prevents ChromaDB SQLite locking)

### ⚠️ ARM VM Constraints:
- 6 GB RAM - must use single Gunicorn worker
- Other services running - need swap space for model loading
- Must pre-download models to avoid timeout during startup

---

## 📦 Phase 2: SSH into VM & Setup Environment

```bash
# SSH into your OCI Ubuntu VM
ssh ubuntu@158.101.106.119

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ and pip (if not already installed)
sudo apt install -y python3 python3-pip python3-venv git

# Verify Python version
python3 --version
```

---

## 💾 Phase 3: Add Swap Space (Critical for 6 GB RAM)

```bash
# Check current swap
free -h

# Create 4GB swap file
sudo fallocate -l 4G /swapfile

# Set permissions
sudo chmod 600 /swapfile

# Create swap space
sudo mkswap /swapfile

# Enable swap
sudo swapon /swapfile

# Make swap permanent (add to fstab)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify swap is active
free -h

# Optimize swappiness (reduce swap usage to 10%)
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

## 📁 Phase 4: Clone & Setup Project

```bash
# Navigate to home directory
cd ~

# Clone the repository (replace with your actual repo URL)
git clone https://github.com/engrrabdulkhaliq001/Resume-screening-ai.git

# Navigate to backend directory
cd Resume-screening-ai/backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

---

## 📦 Phase 5: Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Verify critical packages
pip list | grep -E "fastapi|uvicorn|chromadb|sentence|flashrank|groq"
```

---

## 🔑 Phase 6: Configure Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
GROQ_API_KEY=your_actual_groq_api_key_here
EOF

# IMPORTANT: Replace 'your_actual_groq_api_key_here' with your real Groq API key
# Get your key from: https://console.groq.com

# Verify .env file
cat .env
```

---

## 🤖 Phase 7: Pre-download Models (Prevents Timeout)

```bash
# Create Python script to pre-download models
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

# Run the download script
python download_models.py

# Verify models are cached
ls -lh models_cache/
```

---

## 🔥 Phase 8: Create Systemd Service

```bash
# Create systemd service file
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

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable resume-screening.service

# Start the service
sudo systemctl start resume-screening.service

# Check service status
sudo systemctl status resume-screening.service
```

---

## 🔓 Phase 9: Open Firewall Port (iptables)

```bash
# Allow port 8003
sudo iptables -I INPUT -p tcp --dport 8003 -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Save iptables rules (persist across reboots)
sudo apt install -y iptables-persistent
sudo netfilter-persistent save

# Verify rules
sudo iptables -L -n -v | grep 8003
```

---

## ✅ Phase 10: Verification & Health Check

```bash
# Wait 10 seconds for service to fully start
sleep 10

# Check service logs
sudo journalctl -u resume-screening.service -f --no-pager

# In another terminal, test the API
curl http://localhost:8003/

# Expected response:
# {
#   "status": "running",
#   "resumes_indexed": 0,
#   "jd_title": "None",
#   "model": "llama-3.3-70b-versatile",
#   "embed_model": "all-MiniLM-L6-v2",
#   "chroma_path": "./chroma_db"
# }

# Test from external machine (replace with your VM IP)
curl http://158.101.106.119:8003/
```

---

## 🧪 Phase 11: Full API Testing

```bash
# Test 1: Upload Job Description
curl -X POST http://158.101.106.119:8003/upload-jd \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We need a Python developer with FastAPI and ML experience.",
    "skills_required": ["python", "fastapi", "docker"],
    "experience_years": 3,
    "education": "bachelors"
  }'

# Expected response:
# {"jd_id": "abc123", "title": "Senior Python Developer"}

# Test 2: Check Collection Info
curl http://158.101.106.119:8003/collection-info

# Test 3: Check Root Status
curl http://158.101.106.119:8003/
```

---

## 🔧 Phase 12: Service Management Commands

```bash
# View real-time logs
sudo journalctl -u resume-screening.service -f

# Restart service
sudo systemctl restart resume-screening.service

# Stop service
sudo systemctl stop resume-screening.service

# Start service
sudo systemctl start resume-screening.service

# Check status
sudo systemctl status resume-screening.service

# View last 100 lines of logs
sudo journalctl -u resume-screening.service -n 100 --no-pager
```

---

## 📊 Phase 13: Monitor Resource Usage

```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check running processes
ps aux | grep gunicorn

# Check CPU usage
top -bn1 | head -20
```

---

## 🚨 Troubleshooting

### Issue: Service fails to start
```bash
# Check detailed logs
sudo journalctl -u resume-screening.service -n 50 --no-pager

# Common fixes:
# 1. Verify GROQ_API_KEY is set in .env
# 2. Verify all dependencies are installed
# 3. Check if port 8003 is already in use
sudo lsof -i :8003
```

### Issue: Out of memory during model loading
```bash
# Increase swap to 8GB if needed
sudo swapoff /swapfile
sudo fallocate -l 8G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: ChromaDB locking errors
```bash
# We're using single worker (-w 1) to prevent this
# If you still see errors, clear the database:
curl -X DELETE http://localhost:8003/clear
```

### Issue: Port not accessible from external
```bash
# Verify firewall rules
sudo iptables -L -n -v | grep 8003

# Check if service is listening
sudo netstat -tlnp | grep 8003
```

---

## 📝 Summary of Key Optimizations

1. **Single Gunicorn Worker**: Prevents ChromaDB SQLite concurrency issues
2. **Swap Space**: 4GB swap added to handle model loading on 6GB RAM
3. **Model Pre-download**: Models cached before service starts
4. **Cache Directory Control**: HuggingFace models stored in local directory
5. **Auto-restart**: Systemd service with 10-second restart delay
6. **Timeout Extension**: 300-second timeout for ML operations
7. **Journal Logging**: All logs stored in systemd journal for debugging

---

## 🎯 Next Steps After Deployment

1. **Test with real resume files** via the `/upload-resume` endpoint
2. **Monitor memory usage** during first few operations
3. **Set up monitoring** (optional: Prometheus/Grafana)
4. **Configure backup** for ChromaDB data directory
5. **Consider external vector DB** (Pinecone/Weaviate) for production scale

---

## 📞 Support

If you encounter issues:
1. Check service logs: `sudo journalctl -u resume-screening.service -f`
2. Verify dependencies: `pip list`
3. Check resource usage: `free -h` and `df -h`
4. Test API locally: `curl http://localhost:8003/`

---

**Deployment Complete! 🎉**
