# 🚀 Quick Setup Guide

## **Prerequisites**
- Python 3.8+
- Node.js 14+
- OpenAI API Key

## **Setup Steps**

### **1. Clone Repository**
```bash
git clone https://github.com/Karthikay2002/arena-chatbott.git
cd arena-chatbott
```

### **2. Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp ../env.example .env
# Edit .env and add your OPENAI_API_KEY
python main.py
```

### **3. Frontend (if needed)**
```bash
# Backend serves built frontend automatically
# System runs at http://localhost:8000
```

### **4. Test Files**
- Upload the included test file: `1980-01-08 09-44-08.bin` (60MB)
- Or use `dronekit_log171.bin` (3MB) for faster testing

## **🎯 Ready to Demo!**
- **URL**: http://localhost:8000
- **Upload**: Any ArduPilot .bin, .log, or .tlog file
- **Chat**: Ask any question about your flight data
- **Visualizations**: Request charts and analysis 