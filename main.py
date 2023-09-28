from modules.database import CreateDatabase
from modules.ui.window import InitUI
import logging
import sys

# Configure logging at the very beginning
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(levelname)s:%(message)s'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

logging.debug("Logging setup complete.")

def exception_hook(exc_type, exc_value, exc_traceback):
    logging.error("Exception:", exc_info=(exc_type, exc_value, exc_traceback))

# Set the exception hook
sys.excepthook = exception_hook

logging.debug("Exception hook set.")

def main():
    session = CreateDatabase()
    InitUI(session)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("An error occurred: %s", e)