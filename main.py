"""
Atulya AI - Dynamic FastAPI Server (v0.1.0)
DeepSeek R1 as main brain with intelligent routing and dynamic responses
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import core components
try:
    from Core.agent import intelligent_agent, process_user_input, get_system_status
    AGENT_AVAILABLE = True
    logger.info("Intelligent agent loaded successfully")
except ImportError as e:
    AGENT_AVAILABLE = False
    logger.warning(f"Agent not available: {e}")

# Create FastAPI app
app = FastAPI(
    title="Atulya AI - Dynamic Intelligence",
    description="AI system with DeepSeek R1 as main brain and dynamic capabilities",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"
    context: Optional[Dict[str, Any]] = None
    stream: bool = False

class AdminRequest(BaseModel):
    action: str
    parameters: Optional[Dict[str, Any]] = None
    user_id: str = "admin"

class SystemConfigRequest(BaseModel):
    config_updates: Dict[str, Any]
    restart_required: bool = False

# Global state
active_sessions = {}
system_metrics = {
    "requests_processed": 0,
    "models_loaded": 0,
    "errors_count": 0,
    "start_time": datetime.now().isoformat()
}

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    logger.info("🚀 Atulya AI Dynamic Server starting up...")
    
    if AGENT_AVAILABLE:
        try:
            # Let the agent initialize itself
            status = get_system_status()
            logger.info(f"Agent status: {status}")
            
            # Create necessary directories
            Path("logs").mkdir(exist_ok=True)
            Path("uploads").mkdir(exist_ok=True)
            Path("temp").mkdir(exist_ok=True)
            
            logger.info("✅ Dynamic Intelligence System ready!")
            
        except Exception as e:
            logger.error(f"❌ Startup error: {e}")
    else:
        logger.warning("⚠️ Running in fallback mode - agent not available")

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "service": "Atulya AI - Dynamic Intelligence",
        "version": "0.1.0",
        "next_major": "0.5.0",
        "target_production": "1.0.0",
        "status": "active",
        "agent_available": AGENT_AVAILABLE,
        "main_brain": "DeepSeek R1",
        "capabilities": [
            "text", "vision", "speech", "document", 
            "embedding", "tools", "admin"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    Main chat endpoint - DeepSeek R1 processes and routes intelligently
    """
    try:
        system_metrics["requests_processed"] += 1
        
        if not AGENT_AVAILABLE:
            return {
                "success": False,
                "error": "Agent not available",
                "response": "I'm currently initializing. Please try again in a moment.",
                "fallback": True
            }
        
        # Let the intelligent agent handle the request dynamically
        result = await process_user_input(
            user_input=request.message,
            user_id=request.user_id
        )
        
        # Add session tracking
        if request.user_id not in active_sessions:
            active_sessions[request.user_id] = {
                "start_time": datetime.now().isoformat(),
                "messages_count": 0
            }
        
        active_sessions[request.user_id]["messages_count"] += 1
        active_sessions[request.user_id]["last_activity"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        system_metrics["errors_count"] += 1
        logger.error(f"Chat error: {e}")
        
        return {
            "success": False,
            "error": str(e),
            "response": "I encountered an error. Let me try a different approach.",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/admin")
async def admin_endpoint(request: AdminRequest) -> Dict[str, Any]:
    """
    Dynamic admin endpoint - DeepSeek R1 handles admin tasks intelligently
    """
    try:
        if not AGENT_AVAILABLE:
            return {
                "success": False,
                "error": "Agent not available for admin operations"
            }
        
        # Check admin permissions
        if not await verify_admin_access(request.user_id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Let the intelligent agent handle admin requests
        admin_result = await intelligent_agent.process_admin_request(
            request.action, 
            request.user_id
        )
        
        return admin_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/status")
async def status_endpoint() -> Dict[str, Any]:
    """
    Dynamic system status - comprehensive health check
    """
    try:
        base_status = {
            "service": "Atulya AI",
            "version": "0.1.0",
            "next_major": "0.5.0",
            "target_production": "1.0.0",
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "metrics": system_metrics,
            "active_sessions": len(active_sessions),
            "agent_available": AGENT_AVAILABLE
        }
        
        if AGENT_AVAILABLE:
            # Get detailed status from intelligent agent
            agent_status = get_system_status()
            base_status.update(agent_status)
        
        return base_status
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return {
            "service": "Atulya AI",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/models/load")
async def load_model_endpoint(model_name: str) -> Dict[str, Any]:
    """
    Dynamic model loading - load models on demand
    """
    try:
        if not AGENT_AVAILABLE:
            return {"success": False, "error": "Agent not available"}
        
        # Let the model loader handle this dynamically
        from Core.model_loader import model_loader
        
        model = model_loader.load_model(model_name)
        
        if model:
            system_metrics["models_loaded"] += 1
            return {
                "success": True,
                "model": model_name,
                "type": model.get("type", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Failed to load model: {model_name}"
            }
        
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/models/unload")
async def unload_models_endpoint(keep_models: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Dynamic model cleanup
    """
    try:
        if not AGENT_AVAILABLE:
            return {"success": False, "error": "Agent not available"}
        
        from Core.model_loader import model_loader
        
        model_loader.unload_unused_models(keep_models or ["deepseek-r1"])
        
        return {
            "success": True,
            "message": "Models cleaned up",
            "kept_models": keep_models or ["deepseek-r1"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model cleanup error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/analyze")
async def analyze_endpoint(
    request: ChatRequest,
    analysis_type: str = "full"
) -> Dict[str, Any]:
    """
    Dynamic analysis endpoint - let DeepSeek R1 analyze inputs
    """
    try:
        if not AGENT_AVAILABLE:
            return {"success": False, "error": "Agent not available"}
        
        # Use the model loader's analysis capabilities
        from Core.model_loader import model_loader
        
        analysis = model_loader.analyze_task(
            request.message, 
            request.context or {}
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/sessions")
async def sessions_endpoint() -> Dict[str, Any]:
    """
    Get active sessions information
    """
    return {
        "active_sessions": active_sessions,
        "total_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/sessions/{user_id}")
async def clear_session_endpoint(user_id: str) -> Dict[str, Any]:
    """
    Clear a specific user session
    """
    if user_id in active_sessions:
        del active_sessions[user_id]
        return {
            "success": True,
            "message": f"Session cleared for user: {user_id}"
        }
    else:
        return {
            "success": False,
            "message": f"No active session found for user: {user_id}"
        }

@app.post("/config/update")
async def update_config_endpoint(request: SystemConfigRequest) -> Dict[str, Any]:
    """
    Dynamic configuration updates
    """
    try:
        # Let DeepSeek R1 validate and apply config changes safely
        admin_request = f"Update system configuration: {json.dumps(request.config_updates)}"
        
        if AGENT_AVAILABLE:
            result = await intelligent_agent.process_admin_request(
                admin_request, 
                "system"
            )
            return result
        else:
            return {
                "success": False,
                "error": "Agent not available for config updates"
            }
        
    except Exception as e:
        logger.error(f"Config update error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def verify_admin_access(user_id: str) -> bool:
    """
    Verify admin access - can be made more sophisticated
    """
    # For now, simple check - in production, use proper authentication
    admin_users = ["admin", "system", "root"]
    return user_id in admin_users

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests for monitoring
    """
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    """
    system_metrics["errors_count"] += 1
    
    logger.error(f"Global error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "The system encountered an unexpected error",
            "timestamp": datetime.now().isoformat()
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Atulya AI Dynamic Intelligence"
    }

@app.get("/versions")
async def versions_endpoint() -> Dict[str, Any]:
    """
    Get version information for all components
    """
    try:
        import yaml
        from pathlib import Path
        
        version_file = Path("Config/version_list.yaml")
        if version_file.exists():
            with open(version_file, 'r') as f:
                versions = yaml.safe_load(f)
            
            return {
                "success": True,
                "versions": versions,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Version list file not found",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Version info error: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Dynamic server configuration
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
        "reload": False,  # Set to True for development
        "workers": 1
    }
    
    logger.info(f"🚀 Starting Atulya AI Dynamic Server on {config['host']}:{config['port']}")
    
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        log_level=config["log_level"],
        reload=config["reload"]
    ) 