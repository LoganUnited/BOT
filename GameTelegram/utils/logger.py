import logging
import sys
import os
from pathlib import Path
 
def setup_logger():
    """Настройка логгера с поддержкой UTF-8"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.encoding = 'utf-8'
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )
    
    return logging.getLogger(__name__)