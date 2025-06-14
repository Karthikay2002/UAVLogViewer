# 🚁 UAV Log Analysis System with LLM Integration

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-brightgreen.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

A comprehensive UAV flight log analysis system that combines traditional telemetry analysis with AI-powered insights. This system processes ArduPilot log files (.bin, .log, .tlog) and provides intelligent analysis, visualization, and safety assessments through an intuitive web interface.

## 🎯 **Project Overview**

This project transforms raw UAV flight data into actionable insights through:
- **Intelligent Log Processing**: Automated parsing of ArduPilot telemetry data
- **AI-Powered Analysis**: LLM integration for natural language queries and explanations
- **Proactive Safety Monitoring**: Automatic anomaly detection and safety scoring
- **Dynamic Visualizations**: Real-time chart generation based on available data types
- **Professional Web Interface**: Modern Vue.js frontend with responsive design

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   FastAPI        │    │   Analysis      │
│   Frontend      │◄──►│   Backend        │◄──►│   Engine        │
│                 │    │                  │    │                 │
│ • File Upload   │    │ • API Endpoints  │    │ • pymavlink     │
│ • Chat Interface│    │ • Tool Router    │    │ • Data Parser   │
│ • Visualizations│    │ • LLM Integration│    │ • Anomaly Det.  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 **Key Features**

### 📊 **Intelligent Data Analysis**
- **Multi-Format Support**: .bin, .log, .tlog file compatibility
- **Smart Data Detection**: Automatic identification of available telemetry types
- **Dynamic Visualization**: Charts generated based on detected data (Battery, GPS, Altitude, Attitude)
- **Comprehensive Dashboards**: Multi-system analysis with professional styling

### 🤖 **AI-Powered Insights**
- **Natural Language Queries**: Ask questions in plain English
- **Contextual Responses**: Smart tool selection based on query type
- **Proactive Analysis**: Automatic safety assessments and anomaly detection
- **Explanation Engine**: AI interpretation of technical data

### 🛡️ **Safety & Monitoring**
- **Real-time Anomaly Detection**: Automatic identification of critical issues
- **Safety Scoring**: Comprehensive flight safety assessment (0-100 scale)
- **Proactive Warnings**: Immediate alerts for battery, GPS, and system failures
- **Recommendation Engine**: Actionable maintenance and safety suggestions

## 🛠️ **Technical Implementation**

### **Backend Stack**
- **FastAPI**: High-performance async API framework
- **pymavlink**: ArduPilot log parsing and telemetry extraction
- **matplotlib/plotly**: Dynamic visualization generation
- **OpenAI GPT**: LLM integration for intelligent analysis
- **Python 3.8+**: Core processing engine

### **Frontend Stack**
- **Vue.js 3**: Modern reactive frontend framework
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live data streaming and visualization updates
- **Professional UI/UX**: Clean, intuitive user experience

### **Data Processing Pipeline**
1. **File Upload & Validation**: Secure file handling with format verification
2. **Telemetry Extraction**: pymavlink-based data parsing
3. **Data Type Detection**: Automatic identification of available metrics
4. **Analysis Engine**: Multi-tool processing based on query context
5. **Visualization Generation**: Dynamic chart creation with professional styling
6. **LLM Integration**: AI-powered interpretation and response generation

## 📈 **Project Journey & Challenges Overcome**

### **🔥 Major Challenges Faced**

#### **1. Corrupted Sample Data Crisis**
**Problem**: Initially tested with multiple log files that appeared to be valid ArduPilot .bin files but were actually corrupted HTML content served by GitHub's web interface.

**Symptoms**:
- Files showed "bad header" errors during parsing
- No analyzable telemetry data extracted
- Identical "No Analyzable Data Found" responses for different files

**Solution**:
- Implemented robust file validation and header checking
- Created comprehensive error handling for corrupted data
- Sourced real ArduPilot logs from verified repositories
- Added data quality assessment tools

#### **2. Format Compatibility Issues**
**Problem**: Downloaded PX4 logs (.ulg format) were incompatible with ArduPilot-focused system.

**Technical Details**:
- PX4 uses .ulg format (binary log format specific to PX4)
- ArduPilot uses .bin/.log/.tlog formats with MAVLink protocol
- pymavlink library only supports ArduPilot formats

**Solution**:
- Focused on ArduPilot ecosystem compatibility
- Implemented format detection and validation
- Created clear error messages for unsupported formats
- Documented supported file types

#### **3. Visualization Duplication Bug**
**Problem**: System generated duplicate charts with identical content, cluttering the interface.

**Root Cause**: Multiple timestamp-based file generation within the same second

**Solution**:
- Implemented smart visualization management
- Added deduplication logic for chart generation
- Optimized file naming conventions

#### **4. Over-Analysis for Simple Queries**
**Problem**: Simple questions like "What was the maximum altitude?" triggered comprehensive analysis, making responses unnecessarily verbose.

**Solution**:
- Implemented intelligent query classification
- Created context-aware tool selection
- Developed response optimization based on query complexity

### **🎯 Technical Innovations**

#### **Smart Tool Router**
```python
# Intelligent tool selection based on query analysis
if is_simple_query and not is_safety_query:
    # Minimal tools for factual questions
    selected_tools = ["get_max_altitude", "flight_duration"]
elif is_safety_query:
    # Comprehensive safety analysis
    selected_tools = ["detect_battery_failsafe", "comprehensive_flight_analysis"]
```

#### **Proactive Anomaly Detection**
- Automatic safety scoring (0-100 scale)
- Real-time critical issue identification
- Predictive maintenance recommendations
- Multi-system health monitoring

#### **Dynamic Visualization Engine**
- Data-driven chart generation
- Professional styling with health indicators
- Responsive design for multiple screen sizes
- Export capabilities for reports

## 🔧 **Installation & Setup**

### **Prerequisites**
```bash
Python 3.8+
Node.js 14+
npm or yarn
```

### **Backend Setup**
```bash
cd UAVLogViewer/backend
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python main.py
```

### **Frontend Setup**
```bash
cd UAVLogViewer
npm install
npm run serve
```

### **Environment Configuration**
Create `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
UPLOAD_DIR=./uploaded_files
MAX_FILE_SIZE=100MB
DEBUG=True
```

## 🎮 **Usage Examples**

### **Simple Queries**
- "What was the highest altitude reached during the flight?"
- "How long was the total flight time?"
- "What was the maximum battery voltage?"

### **Safety Analysis**
- "Are there any anomalies or safety issues in this flight data?"
- "List all critical errors that happened mid-flight"
- "What's the overall safety score for this flight?"

### **Visualization Generation**
- "Generate comprehensive flight visualizations"
- "Create battery performance charts"
- "Show me altitude and GPS tracking plots"

### **Technical Analysis**
- "Analyze the battery discharge rate throughout the flight"
- "How stable was the altitude control?"
- "Compare GPS accuracy throughout the flight"

## 📊 **Supported Data Types**

| Data Type | Description | Visualizations |
|-----------|-------------|----------------|
| **Battery** | Voltage, current, power consumption | Voltage trends, discharge rates, health indicators |
| **GPS** | Position, satellites, accuracy | Satellite count, HDOP accuracy, GPS lock status |
| **Altitude** | Barometric, GPS altitude | Altitude profiles, stability metrics |
| **Attitude** | Roll, pitch, yaw orientation | Attitude trends, stability analysis |

## 🛡️ **Safety Features**

### **Automatic Anomaly Detection**
- **Critical Battery Issues**: Low voltage, rapid discharge, failsafe triggers
- **GPS Problems**: Lock loss, poor accuracy, satellite count drops
- **Flight Instability**: Rapid altitude changes, excessive vibration
- **System Failures**: Motor issues, sensor malfunctions

### **Safety Scoring System**
- **90-100**: Excellent - No significant issues
- **70-89**: Good - Minor issues requiring monitoring
- **50-69**: Fair - Several issues requiring attention
- **30-49**: Poor - Multiple problems, inspection needed
- **0-29**: Critical - Immediate action required

## 🔄 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | System health check |
| `/upload` | POST | File upload endpoint |
| `/api/chat` | POST | LLM chat interface |
| `/api/plots` | GET | List generated visualizations |
| `/api/reports` | GET | List analysis reports |

## 📁 **Project Structure**

```
UAVLogViewer/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry point
│   ├── tools.py            # Analysis tools and functions
│   ├── llm.py              # LLM integration and prompting
│   ├── log_analyzer.py     # Core log analysis engine
│   ├── telemetry.py        # Telemetry data processing
│   ├── settings.py         # Configuration management
│   └── requirements.txt    # Python dependencies
├── frontend/               # Vue.js frontend
│   └── src/
│       └── components/     # Vue components
├── dist/                   # Built frontend assets
├── config/                 # Environment configurations
├── package.json           # Node.js dependencies
└── README.md              # This file
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 **License**

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **ArduPilot Community**: For comprehensive documentation and log format specifications
- **pymavlink**: Essential library for MAVLink protocol handling
- **DroneKit**: Sample log files for testing and validation
- **OpenAI**: GPT integration for intelligent analysis
- **FastAPI & Vue.js**: Excellent frameworks for rapid development

## 📞 **Support**

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the [ArduPilot documentation](https://ardupilot.org/copter/docs/logmessages.html)
- Review the API documentation at `/docs` when running the server

---

**Built with ❤️ for the UAV community**
