"""Logging configuration for RiskBench Suite."""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

def setup_logging(log_dir: Optional[str] = None) -> None:
    """Set up logging configuration.
    
    Args:
        log_dir: Directory to store log files. If None, logs to console only.
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': str(log_path / 'riskbench.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        config['loggers']['']['handlers'].append('file')
    
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
