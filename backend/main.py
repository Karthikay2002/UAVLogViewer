from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os, json, tempfile, aiofiles
from uuid import uuid4
from typing import Optional
from backend.settings import UPLOAD_DIR
from backend.tools import TOOLS
from backend.llm import ask_llm
from pathlib import Path

app = FastAPI()

# Allow CORS for frontend - allow all localhost origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Mount static files for serving plots
plots_dir = os.path.join(UPLOAD_DIR, "plots")
reports_dir = os.path.join(UPLOAD_DIR, "reports")
os.makedirs(plots_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)

app.mount("/plots", StaticFiles(directory=plots_dir), name="plots")
app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")

@app.get("/status")
def health():
    return {"status": "Backend is up"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    suffix = f"_{file.filename}"
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix, dir=UPLOAD_DIR)
    os.close(tmp_fd)
    try:
        async with aiofiles.open(tmp_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                await out.write(chunk)
        final_name = f"{uuid4().hex}{suffix}"
        final_path = os.path.join(UPLOAD_DIR, final_name)
        os.replace(tmp_path, final_path)
        return {"filename": final_name}
    except Exception as exc:
        return {"error": f"Upload failed: {exc}"}

@app.get("/uploaded")
def get_uploaded_files():
    return {"files": os.listdir(UPLOAD_DIR)}

@app.get("/api/plots")
def list_plots():
    """List all available plot files"""
    try:
        plot_files = []
        if os.path.exists(plots_dir):
            for file in os.listdir(plots_dir):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    plot_files.append({
                        "filename": file,
                        "url": f"/plots/{file}",
                        "created": os.path.getctime(os.path.join(plots_dir, file))
                    })
        return {"plots": sorted(plot_files, key=lambda x: x["created"], reverse=True)}
    except Exception as e:
        return {"error": f"Failed to list plots: {str(e)}"}

@app.get("/api/reports")
def list_reports():
    """List all available report files"""
    try:
        report_files = []
        if os.path.exists(reports_dir):
            for file in os.listdir(reports_dir):
                if file.endswith(('.json', '.pdf')):
                    report_files.append({
                        "filename": file,
                        "url": f"/reports/{file}",
                        "created": os.path.getctime(os.path.join(reports_dir, file))
                    })
        return {"reports": sorted(report_files, key=lambda x: x["created"], reverse=True)}
    except Exception as e:
        return {"error": f"Failed to list reports: {str(e)}"}

class ChatRequest(BaseModel):
    filename: str
    question: str
    session_id: Optional[str] = None

# LLM-first chat endpoint with smart tool selection
@app.post("/api/chat")
async def chat(request: ChatRequest):
    filename = request.filename
    question = request.question.lower()
    
    # Smart tool selection based on user request
    context = {}
    
    # Check if user is asking for NEW visualizations vs explaining existing ones
    generate_viz_keywords = ["generate", "create", "make", "produce", "build", "show", "display"]
    explain_viz_keywords = ["explain", "describe", "interpret", "analyze", "what does", "tell me about"]
    viz_keywords = ["visualiz", "plot", "chart", "graph", "dashboard", "report", "trend"]
    
    # Simple question keywords that don't need comprehensive analysis
    simple_keywords = ["what was", "when did", "how long", "maximum", "minimum", "highest", "lowest", "first", "last"]
    safety_keywords = ["safety", "anomal", "critical", "error", "problem", "issue", "warning", "failsafe"]
    
    # Determine question type
    is_simple_query = any(keyword in question for keyword in simple_keywords)
    is_safety_query = any(keyword in question for keyword in safety_keywords)
    wants_new_visualizations = (
        any(keyword in question for keyword in viz_keywords) and 
        any(keyword in question for keyword in generate_viz_keywords) and
        not any(keyword in question for keyword in explain_viz_keywords)
    )
    wants_explanation = any(keyword in question for keyword in explain_viz_keywords)
    
    # Select appropriate tools based on question type
    if wants_new_visualizations and not wants_explanation:
        # User wants NEW visualizations - run visualization tools
        selected_tools = [
            "generate_flight_visualizations",
            "generate_advanced_report", 
            "create_trend_analysis"
        ]
    elif is_simple_query and not is_safety_query:
        # Simple factual question - run minimal tools
        if "altitude" in question:
            selected_tools = ["get_max_altitude"]
        elif "duration" in question or "time" in question:
            selected_tools = ["flight_duration"]
        elif "battery" in question:
            selected_tools = ["battery_stats"]
        elif "gps" in question:
            selected_tools = ["gps_lock_lost"]
        else:
            # Default simple tools
            selected_tools = ["get_max_altitude", "flight_duration", "battery_stats"]
    elif is_safety_query:
        # Safety/anomaly question - run safety tools
        selected_tools = [
            "detect_battery_failsafe",
            "detect_motor_failure", 
            "gps_lock_lost",
            "flight_safety_assessment",
            "comprehensive_flight_analysis"
        ]
    else:
        # Complex analysis request - run comprehensive tools
        selected_tools = [
            "get_max_altitude",
            "flight_duration", 
            "battery_stats",
            "detect_battery_failsafe",
            "detect_motor_failure",
            "gps_lock_lost",
            "comprehensive_flight_analysis",
            "flight_safety_assessment",
            "telemetry_health_check"
        ]
    
    # Run selected tools
    for tool in TOOLS:
        if tool["name"] in selected_tools:
            try:
                result = tool["function"](filename)
                context[tool["name"]] = result
            except Exception as e:
                context[tool["name"]] = f"Error: {str(e)}"
    
    # Only run proactive anomaly detection for safety queries or comprehensive analysis
    if is_safety_query or (not is_simple_query and not wants_new_visualizations):
        try:
            from backend.tools import comprehensive_flight_analysis_tool
            anomaly_result = comprehensive_flight_analysis_tool(filename)
            context["proactive_anomaly_detection"] = anomaly_result
            
            # Extract safety score and critical issues for highlighting
            if "comprehensive_analysis" in anomaly_result:
                analysis = anomaly_result["comprehensive_analysis"]
                critical_issues = analysis.get("critical_issues", [])
                warnings = analysis.get("warnings", [])
                
                # Add safety alert to context if issues found
                if critical_issues or len(warnings) > 3:
                    context["safety_alert"] = {
                        "level": "CRITICAL" if critical_issues else "WARNING",
                        "message": f"🚨 SAFETY ALERT: {len(critical_issues)} critical issues and {len(warnings)} warnings detected",
                        "critical_issues": critical_issues,
                        "warnings": warnings[:5]  # Limit to top 5 warnings
                    }
        except Exception as e:
            context["anomaly_detection_error"] = f"Anomaly detection failed: {str(e)}"
    
    # Let the LLM analyze the question with context
    try:
        response = await ask_llm(question, context, filename)
        return {"response": response}
    except Exception as e:
        # Fallback to raw tool results if LLM fails
        return {
            "response": f"⚠️ LLM analysis failed: {str(e)}\n\nRaw analysis results:\n{json.dumps(context, indent=2)}"
        } 

# Mount the built frontend as a Single Page Application
frontend_dist = Path(__file__).parent.parent / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="spa") 