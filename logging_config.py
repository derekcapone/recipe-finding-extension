import logging

# Configure the root logger
def setup_logger():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("shared_log.log")
        ]
    )

# Call setup_logger when this module is imported
setup_logger()