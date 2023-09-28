from PyQt5.QtWidgets import QWidget, QFrame

class ChatContainer(QWidget):
    def __init__(self, parent=None):
        super(ChatContainer, self).__init__(parent)
        # Initialize the chat container here

        # Add an inset border
        self.setStyleSheet("border: 2px inset grey;")

        # Set the background color to white
        self.setStyleSheet(self.styleSheet() + "background-color: white;")

        # Add a frame to the ChatContainer
        self.chat_frame = QFrame(self)
        self.chat_frame.setGeometry(0, 0, self.width(), self.height())
        self.chat_frame.setStyleSheet("border: 1px solid black;")

    def resizeEvent(self, event):
        self.chat_frame.setGeometry(0, 0, self.width(), self.height())