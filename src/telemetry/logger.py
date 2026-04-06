import logging
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

# Standardizing the log directory relative to the project structure
# Or use your absolute path: "D:/VINAILAB/Lab3-GR03/logs"
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")

class IndustryLogger:
    def __init__(self, name: str = "AI-Lab-Agent", log_dir: str = DEFAULT_LOG_DIR):
        self.logger = logging.getLogger(name)
        # Avoid adding duplicate handlers if the logger is re-initialized
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Ensure directory exists
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # Generate filename: 2026-04-06.log
            log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            
            # 1. File Handler (UTF-8 encoding is vital for JSON data)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(file_formatter)
            
            # 2. Console Handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Logs an event with a timestamp and type."""
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "data": data
        }
        # Logging as a single line JSON (JSONL)
        self.logger.info(json.dumps(payload, ensure_ascii=False))

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str, exc_info=True):
        self.logger.error(msg, exc_info=exc_info)

# Global logger instance - you can pass your D:/ path here if preferred
logger = IndustryLogger()