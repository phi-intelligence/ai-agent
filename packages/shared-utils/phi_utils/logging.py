"""
Structured logging utilities for Phi Agents
Logs in JSON format with context (org_id, agent_id, task_id)
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context if available
        if hasattr(record, "org_id"):
            log_data["org_id"] = record.org_id
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging(service_name: str, level: str = "INFO") -> logging.Logger:
    """Set up structured logging for a service"""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    
    return logger


class ContextLogger:
    """Logger with context (org_id, agent_id, task_id)"""
    
    def __init__(self, base_logger: logging.Logger, **context):
        self.logger = base_logger
        self.context = context
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        """Internal log method with context"""
        extra = kwargs.get("extra", {})
        extra.update(self.context)
        kwargs["extra"] = extra
        
        # Create a new record with context attributes
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, msg, args, None, "", **kwargs
        )
        
        # Add context to record
        for key, value in self.context.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def debug(self, msg: str, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        kwargs["exc_info"] = True
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def with_context(self, **additional_context):
        """Create a new logger with additional context"""
        new_context = {**self.context, **additional_context}
        return ContextLogger(self.logger, **new_context)


