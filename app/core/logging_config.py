import logging
import sys
from pathlib import Path

def setup_logging():
    """Minimal logging setup"""
    
    # Create logs directory
    Path("/app/logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/app/logs/app.log"),
        ]
    )