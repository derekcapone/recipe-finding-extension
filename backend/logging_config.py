import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_FILE = PROJECT_ROOT / "application_log.log"

# Configure the root logger
def setup_logger():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(module)s: %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE)
        ]
    )

# Call setup_logger when this module is imported
setup_logger()