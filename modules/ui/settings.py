from PyQt5.QtWidgets import QDialog, QTabWidget, QWidget, QPushButton

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)

        # Configure dialog settings
        self.setWindowTitle('Settings')
        self.setModal(True)
        
        # Set the size of the dialog
        self.resize(800, 600)
        self.setFixedSize(800, 600)

        # Create a Tab Panel
        self.tab_panel = QTabWidget(self)

        # Add tabs to the Tab Panel
        self.general_tab = QWidget()
        self.users_tab = QWidget()
        self.ai_tab = QWidget()

        self.tab_panel.addTab(self.general_tab, "General")
        self.tab_panel.addTab(self.users_tab, "Users")
        self.tab_panel.addTab(self.ai_tab, "AI")

        # Resize the Tab Panel to make space for the buttons
        self.tab_panel.setGeometry(0, 0, 800, 550)

        # Create "Cancel" and "Apply" buttons
        self.cancel_button = QPushButton("Cancel", self)
        self.apply_button = QPushButton("Apply", self)

        # Position the buttons at the bottom right
        self.cancel_button.move(20, 560)
        self.apply_button.move(700, 560)

        self.cancel_button.clicked.connect(self.close_window)

    def close_window(self):
        self.close()