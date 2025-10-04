import json
import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Any

from .utils.database import Database
from .alert_manager import AlertManager
from .decision_engine import DecisionEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration Loading ---
def load_config():
    try:
        with open('main_server/config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"FATAL: Could not load main_server/config.json. Error: {e}")
        exit(1)

config = load_config()

# --- Application Components ---
try:
    db = Database(config['DATABASE_URL'])
    alert_manager = AlertManager(config)
    decision_engine = DecisionEngine(config, db, alert_manager)
except Exception as e:
    logger.error(f"FATAL: Failed to initialize application components. Error: {e}")
    exit(1)

# --- FastAPI Application ---
app = FastAPI(
    title="CryptoSentinel AI - Main Server",
    description="Receives data from agents, processes it, and sends alerts."
)

# --- Pydantic Model for Incoming Data ---
class ReportData(BaseModel):
    timestamp: str
    type: str
    source: str
    impact: str
    details: Any
    confidence: float = Field(..., ge=0.0, le=1.0)
    sentiment: str | None = None
    event: str | None = None

# --- API Endpoints ---
@app.post("/report")
async def handle_report(report: ReportData, background_tasks: BackgroundTasks):
    """
    Endpoint to receive data from all agents.
    It validates the data, stores it, and triggers the decision engine.
    """
    try:
        logger.info(f"Received report from source: {report.source}, type: {report.type}")

        # Convert Pydantic model to dictionary for consistent processing
        report_dict = report.model_dump()

        # 1. Store the event in the database
        db.add_event(report_dict)

        # 2. Trigger the decision engine in the background
        # This allows us to return a response to the agent immediately.
        background_tasks.add_task(decision_engine.process_new_event, report_dict)

        return {"status": "success", "message": "Report received and is being processed."}

    except Exception as e:
        logger.error(f"Error processing report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while processing report.")

@app.get("/")
def read_root():
    return {"message": "CryptoSentinel AI Main Server is running."}

# --- Background Task for Database Cleanup ---
async def cleanup_task():
    """Periodically cleans up old events from the database."""
    while True:
        await asyncio.sleep(3600) # Run every hour
        logger.info("Running periodic database cleanup task...")
        try:
            db.cleanup_old_events(config.get("EVENT_EXPIRATION_SECONDS", 3600) * 2) # Clean up anything older than 2x the normal context window
        except Exception as e:
            logger.error(f"Error during scheduled cleanup task: {e}")

@app.on_event("startup")
async def startup_event():
    """Actions to perform on server startup."""
    # Start the background cleanup task
    asyncio.create_task(cleanup_task())
    logger.info("Main Server has started successfully.")

@app.on_event("shutdown")
def shutdown_event():
    """Actions to perform on server shutdown."""
    logger.info("Main Server is shutting down.")

# To run the server, use the command:
# uvicorn main_server.app:app --host 0.0.0.0 --port 8000 --reload