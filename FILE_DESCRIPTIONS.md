# 📁 Project File Descriptions

## 🏗️ **Core Application Files**

### **Backend (Python/FastAPI)**

| File | Description | Key Features |
|------|-------------|--------------|
| `backend/main.py` | **Main FastAPI application entry point** | API endpoints, CORS setup, static file serving, chat routing |
| `backend/tools.py` | **Core analysis tools and functions** | 50+ analysis functions, visualization generation, data processing |
| `backend/llm.py` | **LLM integration and prompt management** | OpenAI GPT integration, context handling, response generation |
| `backend/log_analyzer.py` | **Core log analysis engine** | pymavlink integration, data extraction, telemetry parsing |
| `backend/telemetry.py` | **Telemetry data processing utilities** | Data type detection, format validation, message parsing |
| `backend/settings.py` | **Configuration management** | Environment variables, upload paths, system settings |
| `backend/requirements.txt` | **Python dependencies** | FastAPI, pymavlink, matplotlib, openai, and 50+ packages |

### **Frontend (Vue.js)**

| File | Description | Key Features |
|------|-------------|--------------|
| `frontend/src/components/` | **Vue.js UI components** | Chat interface, file upload, visualization display |
| `package.json` | **Node.js dependencies and scripts** | Vue.js 3, build tools, development server configuration |
| `vue.config.js` | **Vue.js build configuration** | Development server, proxy settings, build optimization |
| `dist/` | **Built frontend assets** | Production-ready HTML, CSS, JS files served by FastAPI |

## 🔧 **Configuration & Setup Files**

| File | Description | Purpose |
|------|-------------|---------|
| `env.example` | **Environment configuration template** | API keys, server settings, safety thresholds |
| `Dockerfile` | **Docker containerization** | Production deployment configuration |
| `.dockerignore` | **Docker build exclusions** | Excludes dev files from Docker image |
| `.gitignore` | **Git exclusions** | Prevents sensitive files from being committed |
| `babel.config.js` | **JavaScript transpilation** | ES6+ to browser-compatible JavaScript |
| `.eslintrc.js` | **Code quality rules** | JavaScript/Vue.js linting configuration |

## 📊 **Data & Analysis Files**

| File | Description | Content |
|------|-------------|---------|
| `backend/logdocs_dict.json` | **ArduPilot log message documentation** | 166KB of message format specifications |
| `backend/logcodes_dict.json` | **Error code mappings** | Flight mode and error code translations |
| `config_tables.py` | **PX4 database configuration** | Flight modes and error labels for log downloads |
| `download_logs.py` | **Automated log downloader** | Script to fetch sample logs from PX4 database |

## 🧪 **Testing & Development Files**

| File | Description | Testing Focus |
|------|-------------|---------------|
| `backend/test_log_analyzer.py` | **Core analysis testing** | Log parsing, data extraction validation |
| `backend/test_edge_cases.py` | **Edge case testing** | Corrupted files, invalid formats, error handling |
| `backend/create_test_logs.py` | **Test data generation** | Creates synthetic log files for testing |

## 🛠️ **Utility & Helper Files**

| File | Description | Functionality |
|------|-------------|---------------|
| `backend/tool_router.py` | **Smart tool selection** | Context-aware analysis tool routing |
| `backend/mcp_logger.py` | **Logging utilities** | System logging and debugging |
| `backend/anomalies.py` | **Anomaly detection** | Safety issue identification algorithms |
| `backend/metrics.py` | **Performance monitoring** | System performance tracking |
| `backend/flight_awareness.py` | **Flight context analysis** | Flight phase and mode detection |

## 📈 **Data Processing Pipeline**

| File | Description | Pipeline Stage |
|------|-------------|----------------|
| `backend/log_parser.py` | **Raw log parsing** | Stage 1: File format detection and parsing |
| `backend/telemetry.py` | **Data extraction** | Stage 2: Telemetry message extraction |
| `backend/tools.py` | **Analysis processing** | Stage 3: Multi-tool analysis execution |
| `backend/llm.py` | **AI interpretation** | Stage 4: Natural language response generation |

## 🎨 **UI/UX Files**

| File | Description | User Interface |
|------|-------------|----------------|
| `index.html` | **Main HTML template** | Single-page application entry point |
| `static/` | **Static assets** | Images, icons, CSS files |
| `preview.gif` | **Demo animation** | 7.3MB demonstration of system capabilities |

## 🔒 **Security & Validation**

| File | Description | Security Feature |
|------|-------------|------------------|
| `backend/prompt_injector.py` | **Prompt security** | LLM prompt injection prevention |
| `backend/uploaded_files/` | **Secure upload storage** | Isolated file storage with validation |
| `backend/temp_uploads/` | **Temporary processing** | Secure temporary file handling |

## 📦 **Build & Deployment**

| File | Description | Deployment |
|------|-------------|------------|
| `Dockerfile` | **Container definition** | Production Docker image |
| `package-lock.json` | **Dependency lock** | Exact version specifications |
| `build/` | **Build artifacts** | Compiled and optimized files |
| `node_modules/` | **Node.js packages** | Frontend dependencies (excluded from git) |

## 🗂️ **Data Storage Structure**

```
backend/uploaded_files/
├── plots/                    # Generated visualizations
├── reports/                  # Analysis reports
├── *.bin                    # ArduPilot binary logs
├── *.log                    # ArduPilot text logs
└── *.tlog                   # Telemetry logs
```

## 🚫 **Files NOT to Push to GitHub**

### **Sensitive/Generated Files:**
- `.env` (contains API keys)
- `backend/uploaded_files/` (user data)
- `node_modules/` (can be regenerated)
- `__pycache__/` (Python cache)
- `.DS_Store` (macOS system files)
- `venv/` (Python virtual environment)

### **Large/Binary Files:**
- `*.bin` log files (60MB+)
- `backend.zip` (9.4MB archive)
- `preview.gif` (7.3MB - consider compressing)

## 📋 **Files to Include in GitHub Push**

### **Essential Application Files:**
✅ All `backend/*.py` files  
✅ `frontend/src/` directory  
✅ `package.json` and `vue.config.js`  
✅ `README.md` and `DEMO_SCRIPT.md`  
✅ `env.example` (template)  
✅ `requirements.txt`  
✅ Configuration files (`.eslintrc.js`, `babel.config.js`)  
✅ `Dockerfile` and `.dockerignore`  
✅ `LICENSE` file  

### **Documentation:**
✅ `FILE_DESCRIPTIONS.md` (this file)  
✅ API documentation  
✅ Setup instructions  

---

**Total Project Size:** ~15MB (excluding uploaded files and node_modules)  
**Core Codebase:** ~500KB of custom code  
**Dependencies:** 58 Python packages + 145 Node.js packages 