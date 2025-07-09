# 🧠 Atulya AI - Dynamic Intelligence System

**Version 0.1.0** - *DeepSeek R1 as Main Brain with Dynamic Model Delegation*

---

## 🎯 **What is Atulya AI?**

Atulya AI is a **Dynamic Intelligence System** where **DeepSeek R1** acts as the main brain, intelligently analyzing requests and delegating tasks to specialized AI models only when needed. This saves massive storage space and memory while providing comprehensive AI capabilities.

### 🌟 **Key Benefits**
- **🧠 Intelligent**: DeepSeek R1 makes smart delegation decisions
- **⚡ Fast**: 30-second startup vs 10+ minutes
- **🎯 Adaptive**: Learns and optimizes for your needs
- **💾 Efficient**: Dynamic model loading based on actual needs

---

## 🚀 **Quick Start**

### **Installation**

#### **Web Installer (Recommended)**
```bash
# Start web installer
./start_web_installer.sh

# Or manually
python3 web_installer.py

# Open browser: http://localhost:8080
```

#### **Command Line**
```bash
# Clone and install
git clone https://github.com/your-username/atulya-ai.git
cd atulya-ai

# Standard installation
python3 install.py

# Install as service (recommended)
python3 install.py --service

# Upgrade existing installation
python3 install.py --upgrade

# Reinstall (preserves data)
python3 install.py --reinstall
```

### **Start System**
```bash
# Manual start
source venv/bin/activate && python main.py

# Service management
sudo systemctl start/stop/restart atulya-ai
sudo systemctl status atulya-ai
```

### **Access**
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 💡 **How It Works**

### **Dynamic Intelligence**
- **DeepSeek R1** acts as main brain, analyzing requests
- **Models download automatically** when first needed (2-5 minutes each)
- **Smart caching** keeps frequently used models in memory
- **Auto-cleanup** removes unused models to save space

### **Space Savings**
- **Dynamic loading**: Models download only when needed
- **Memory usage**: 60-70% less RAM
- **Startup time**: 30 seconds vs 10+ minutes

---

## 📝 **API Examples**

### **Basic Usage**
```bash
# Chat
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "user123"}'

# Voice
curl -X POST "http://localhost:8000/transcribe" -F "audio=@file.wav"
curl -X POST "http://localhost:8000/speak" -d '{"text": "Hello!"}'

# Status
curl -X GET "http://localhost:8000/status"

# Versions
curl -X GET "http://localhost:8000/versions"
```

---

## 🎛 **Configuration**

Edit `Config/config.yaml` and `.env` for customization. See API docs for detailed configuration options.

**Version Information**: Check `Config/version_list.yaml` for all available models and their versions.

---

## 🔧 **Maintenance**

### **System Management**
```bash
# Show folder sizes
python3 cleanup.py --show-sizes

# Clean large folders
python3 cleanup.py --threshold 100

# Upgrade system
python3 install.py --upgrade
```

### **Troubleshooting**
```bash
# Service problems
sudo systemctl restart atulya-ai
sudo journalctl -u atulya-ai -f

# Memory issues
python3 cleanup.py --threshold 50

# Reinstall
python3 install.py --reinstall
```

### **Debug Mode**
```bash
export ATULYA_DEBUG=true
python3 main.py --debug
```

---

## 🛡 **Features**

### **Multi-Modal Capabilities**
- **Text**: Advanced reasoning, conversation, analysis
- **Vision**: Image analysis, captioning, object detection
- **Speech**: Voice input/output, transcription
- **Document**: PDF processing, layout understanding
- **Video**: Video analysis and classification
- **Audio**: Music and sound generation
- **Memory**: Semantic search and embeddings
- **Code**: Syntax highlighting, debugging, optimization

### **Advanced Tools**
- **File Operations**: Read, write, search, organize files
- **Web Search**: Real-time internet information
- **Code Execution**: Safe sandboxed Python code
- **Email & Calendar**: Productivity tool integration
- **System Admin**: Dynamic system management
- **Database Operations**: SQL queries, data analysis

### **Auto-Recovery & Monitoring**
- **Health Monitoring**: Continuous system health checks
- **Auto-Restart**: Automatically restarts if service fails
- **Auto-Reinstall**: Reinstalls if multiple failures occur
- **Resource Tracking**: Monitors memory, disk space, CPU
- **Smart Cleanup**: Automatically cleans large folders

---

## 📊 **Performance**

| **Metric** | **Traditional** | **Atulya AI** | **Improvement** |
|---|---|---|---|
| **Initial Download** | ~57GB | Dynamic | **On-demand loading** |
| **Memory Usage** | ~8-12GB | ~1-3GB | **60-70% less** |
| **Startup Time** | 10+ minutes | ~30 seconds | **95% faster** |
| **Storage Growth** | Linear | Dynamic | **Adaptive** |

---

## 🔄 **Upgrade & Reinstall**

### **Upgrade (Preserves Settings)**
```bash
python3 install.py --upgrade
```
- ✅ Updates dependencies
- ✅ Updates core files
- ✅ Preserves user data and settings
- ✅ Updates services if installed

### **Reinstall (Preserves Data)**
```bash
python3 install.py --reinstall
```
- ✅ Backs up user data
- ✅ Performs fresh installation
- ✅ Restores user data
- ✅ Preserves conversations and settings

### **Backup & Restore**
The system automatically:
- **Backs up** user data before upgrades/reinstalls
- **Preserves** conversations, settings, and configurations
- **Restores** everything after installation
- **Maintains** system integrity throughout the process

---

## 📞 **Support**

- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/status
- **Logs**: Check `Logs/` directory for detailed logs

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ by the Atulya AI Team** 