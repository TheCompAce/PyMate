import logging
import sys

from PyQt5.QtWidgets import QDialog, QApplication
from modules.database import CreateDatabase
from modules.ui.users import UserSelectionWindow
from modules.ui.window import InitUI


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
    app = QApplication([])

    session = CreateDatabase()
    # Initialize User Selection
    user_selection = UserSelectionWindow(session)
    result = user_selection.exec_()

    if result == QDialog.Accepted:
        selected_user_id = user_selection.get_selected_user_id()
        # Fetch settings and load main window based on selected_user_id
        InitUI(session, selected_user_id)
        sys.exit(app.exec_())
    else:
        sys.exit(0)  # Exit the application if 'Cancel' is clicked

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("An error occurred: %s", e)