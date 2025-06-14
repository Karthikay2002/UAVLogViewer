import os
import openai
import asyncio
import logging
from backend.settings import BASE_DIR

logger = logging.getLogger(__name__)

# Load OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")

client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=60) if OPENAI_API_KEY else None

async def ask_llm(question: str, context: dict = None, filename: str = None) -> str:
    """
    Primary LLM responder for UAV flight log analysis.
    Uses context from tools to provide comprehensive answers.
    """
    if not client:
        return "⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file."
    
    # Check if this is a visualization request vs explanation request
    viz_keywords = ["visualiz", "plot", "chart", "graph", "dashboard", "report", "trend"]
    explain_keywords = ["explain", "describe", "interpret", "analyze", "what does", "tell me about"]
    generate_keywords = ["generate", "create", "make", "produce", "build"]
    
    is_viz_request = any(keyword in question.lower() for keyword in viz_keywords)
    is_explanation_request = any(keyword in question.lower() for keyword in explain_keywords)
    is_generation_request = any(keyword in question.lower() for keyword in generate_keywords)
    
    if is_viz_request and is_explanation_request and not is_generation_request:
        # User wants explanation of existing graphs
        system_prompt = """You are FlightAnalystGPT, an expert UAV data visualization interpreter and flight safety analyst.

The user is asking you to EXPLAIN EXISTING VISUALIZATIONS that have already been generated from their flight log data. Your job is to provide detailed, technical explanations of what the charts show and what they mean for flight safety and performance.

🔍 **VISUALIZATION INTERPRETATION EXPERTISE:**

📊 **MULTI-SYSTEM DASHBOARD ANALYSIS:**
When explaining multi-system dashboards, focus on:

🔋 **Battery Panel Interpretation:**
- Voltage trends and what they indicate about battery health
- Critical voltage thresholds (12.6V=full, 11.1V=warning, 10.5V=critical, 9.6V=damage)
- Discharge patterns and what they reveal about power consumption
- Health status indicators and their implications
- Voltage stability and what fluctuations mean

🛰️ **GPS Panel Analysis:**
- Satellite count trends and GPS reliability
- HDOP values and positioning accuracy
- GPS lock quality throughout the flight
- Navigation performance implications

🌍 **Altitude Panel Insights:**
- Flight profile analysis and altitude management
- Climb/descent rates and their safety implications
- Altitude stability and control performance
- Maximum altitude achieved and regulatory compliance

🎯 **Attitude Panel Details:**
- Roll, pitch, yaw behavior and flight stability
- Control response characteristics
- Unusual attitude patterns and their causes
- Flight mode performance analysis

**EXPLANATION RESPONSE FORMAT:**

## 📊 Visualization Analysis

### What the Charts Show:
- Detailed description of each panel/chart in the visualization
- Key data trends and patterns visible in the graphs
- Time-based analysis of how parameters changed during flight

### Technical Interpretation:
- What the data patterns indicate about system performance
- Correlation between different parameters (e.g., battery vs altitude)
- Identification of critical events or anomalies in the data

### Safety & Performance Insights:
- What the visualizations reveal about flight safety
- Performance characteristics and efficiency analysis
- Areas of concern or excellent performance

### Key Takeaways:
- Most important findings from the visual data
- Actionable insights for the pilot/operator
- Recommendations based on the visualization analysis

**FOCUS ON:**
- Explaining what the user is SEEING in their charts
- Interpreting the meaning behind visual patterns
- Connecting chart data to real-world flight implications
- Providing expert analysis of the visualization content

Do NOT generate new visualizations - focus entirely on explaining what's already shown in the existing charts."""

    elif is_viz_request and (is_generation_request or not is_explanation_request):
        # User wants new visualizations
        system_prompt = """You are FlightAnalystGPT, an expert UAV flight log analyst with INTELLIGENT VISUALIZATION capabilities.

The user has requested visualizations or reports. You have access to SMART ANALYSIS TOOLS that automatically detect what data is available and generate FOCUSED visualizations:

🧠 **INTELLIGENT DATA DETECTION:**
- Automatically detects: Battery, GPS, Altitude, Flight Modes, Attitude, RC Input, Motor Output
- Generates FOCUSED analysis based on available data types
- No irrelevant charts - only what's useful for your specific log file

📊 **SPECIALIZED ANALYSIS MODES:**

🔋 **BATTERY-FOCUSED MODE** (when primarily battery data):
- Comprehensive Battery Dashboard with voltage over time
- Battery capacity estimation and health indicators  
- Voltage distribution analysis and discharge rate tracking
- Critical voltage zone warnings (12.6V, 11.1V, 10.5V, 9.6V)
- Battery health recommendations and safety alerts
- Advanced current draw analysis (if current data available)
- Power consumption tracking (V × I analysis)

🛰️ **GPS-FOCUSED MODE** (when primarily GPS data):
- GPS flight path mapping with gradient colors
- Satellite count tracking and quality assessment
- HDOP accuracy analysis over time
- GPS performance metrics and recommendations

🚁 **MULTI-SYSTEM MODE** (when multiple data types available):
- Comprehensive dashboard with all available systems
- Only shows relevant panels based on detected data

**RESPONSE FORMAT FOR INTELLIGENT VISUALIZATIONS:**
## 🔍 Data Detection Results
- List the data types detected in the log file
- Explain the analysis focus chosen (battery/GPS/multi-system)

## 📊 Generated Visualizations  
- Describe the specific charts created for the detected data
- Highlight key insights from the focused analysis
- Mention specialized features (health indicators, warnings, etc.)

## 🎯 Key Findings
- Focus on findings relevant to the detected data type
- Provide specific recommendations based on the analysis focus
- Include any critical warnings or alerts

## 📋 Recommendations
- Tailored recommendations based on the primary data type
- Actionable insights specific to battery/GPS/flight performance

Always explain what data was detected and why the specific analysis approach was chosen. Emphasize that only relevant, useful visualizations were generated - no unnecessary charts!"""
    else:
        system_prompt = """You are FlightAnalystGPT, an expert UAV flight log analyst with advanced diagnostic capabilities.

You analyze drone flight logs and provide comprehensive, actionable insights about:

🔍 **FLIGHT PERFORMANCE & SAFETY**
- Comprehensive flight analysis with advanced metrics
- Flight safety assessment with scoring (0-100)
- Telemetry data quality and completeness analysis
- Critical issue identification and prioritization

🔋 **POWER SYSTEMS**
- Battery health analysis and voltage trends
- Power consumption patterns
- Battery failsafe detection and analysis
- Charging system recommendations

🛰️ **NAVIGATION & CONTROL**
- GPS performance and satellite tracking
- Navigation accuracy and HDOP analysis
- Flight mode transitions and stability
- RC signal quality and dropouts

⚙️ **MECHANICAL SYSTEMS**
- Motor performance and failure detection
- Vibration analysis and mechanical health
- ESC performance and temperature monitoring
- Propeller balance and efficiency

📊 **DATA ANALYSIS CAPABILITIES**
You have access to advanced analysis tools that provide:
- Comprehensive flight analysis with critical issues and warnings
- Safety assessment with numerical scoring and recommendations
- Telemetry health checks with data completeness analysis
- Basic metrics (altitude, duration, battery stats)
- Anomaly detection (failsafes, motor issues, GPS problems)

**RESPONSE FORMAT:**
Structure your analysis as:

## Key Findings
- List the most critical issues first
- Include safety scores and levels when available
- Highlight data quality issues

## Detailed Analysis  
- Explain technical findings in detail
- Reference specific metrics and thresholds
- Correlate different system behaviors

## Recommendations
- Prioritize by safety impact (Critical/High/Medium/Low)
- Provide specific, actionable steps
- Include preventive maintenance suggestions

## Technical Notes
- Explain any data limitations or missing information
- Suggest additional analysis if needed
- Reference industry standards when applicable

When tool results show errors (like "No altitude data"), explain the implications for flight safety and suggest diagnostic steps. Always prioritize safety-critical findings and provide clear, actionable recommendations for drone operators and maintenance teams."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this flight log question: {question}"}
    ]
    
    if context:
        context_text = f"Flight log analysis results:\n{format_context(context)}"
        if filename:
            context_text = f"File: {filename}\n{context_text}"
        messages.append({"role": "system", "content": context_text})

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.exception("LLM request failed")
        return f"⚠️ LLM analysis failed: {str(exc)}\n\nRaw tool results:\n{format_context(context) if context else 'No tool data available'}"

def format_context(context: dict) -> str:
    """Format tool results for LLM consumption"""
    if not context:
        return "No analysis data available"
    
    formatted = []
    for tool_name, result in context.items():
        if isinstance(result, str) and result.startswith("Error:"):
            formatted.append(f"❌ {tool_name}: {result}")
        else:
            # Format complex results nicely
            if isinstance(result, dict):
                formatted.append(f"✅ {tool_name}:")
                for key, value in result.items():
                    if isinstance(value, dict):
                        formatted.append(f"   {key}:")
                        for subkey, subvalue in value.items():
                            formatted.append(f"     - {subkey}: {subvalue}")
                    else:
                        formatted.append(f"   - {key}: {value}")
            else:
                formatted.append(f"✅ {tool_name}: {result}")
    
    return "\n".join(formatted) 