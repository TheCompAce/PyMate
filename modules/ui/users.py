from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QVBoxLayout
from modules.data.data import User

class UserSelectionWindow(QDialog):
    def __init__(self, session, *args, **kwargs):
        super(UserSelectionWindow, self).__init__(*args, **kwargs)
        self.session = session

        self.setWindowTitle('Select User')

        layout = QVBoxLayout()

        self.user_dropdown = QComboBox()
        users = self.session.query(User).all()
        
        for user in users:
            self.user_dropdown.addItem(user.Name, user.Id)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.user_dropdown)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
    
    def get_selected_user_id(self):
        return self.user_dropdown.currentData()

