import logging
import os
from datetime import datetime

LOGS_DIR = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOGS_DIR, exist_ok=True)

log_filename = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s"
)

def get_logger(name):
    return logging.getLogger(name)

def demo_logger(message):
    logging.info(f"{message}")