from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QMessageBox, QToolBar, QToolButton, QWidget, QSizePolicy, QCheckBox, QTextEdit, QPushButton, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer
import sys
import logging
import json
from enum import Enum

from modules.database import save_window_settings, get_window_settings
from modules.ui.settings import SettingsWindow

just_undocked = False
is_startup = True
is_on_top = False

QWIDGETSIZE_MAX = 16777215

class MyMainWindow(QMainWindow):
    def __init__(self, session, selected_user_id, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)
        self.session = session
        self.userId = selected_user_id
        self.setWindowTitle('PyMate')
        self.setWindowIcon(QIcon('res/icon.png'))
        QTimer.singleShot(100, self.post_show_init)

        self.always_on_top_checkbox = QCheckBox("Always On-Top")
        self.always_on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)

         # Import and add ChatContainer
        from modules.ui.chat import ChatContainer
        self.chat_container = ChatContainer(self)
        self.chat_container.setGeometry(0, 20, self.width(), self.height() - 140)
        self.chat_container.show()
        self.chat_container.repaint()

        self.rich_textbox = QTextEdit(self)
        self.rich_textbox.setGeometry(0, self.height() - 100, self.width() - 100, 100)
        # Create an "Ask" button next to the textbox
        self.ask_button = QPushButton("Ask", self)
        self.ask_button.setGeometry(self.width() - 100, self.height() - 100, 100, 100)


        self.settings_button = QToolButton(self)
        self.settings_button.setText('Settings')
        self.settings_button.move(0, self.height() - self.settings_button.height())
        self.settings_button.clicked.connect(self.open_settings_window)

        self.chat_container.raise_()

    def resizeEvent(self, event):
        global is_startup
        self.chat_container.setGeometry(5, 25, self.width() - 10, self.height() - 155)
        self.chat_container.show()
        self.chat_container.repaint()
        self.rich_textbox.setGeometry(10, self.height() - 120, self.width() - 110, 100)
        self.ask_button.setGeometry(self.width() - 95, self.height() - 115, 90, 90)
        

        if not is_startup:
            save_window_settings_after_resize(self.session, self)


    def open_settings_window(self):
        logging.debug("Triggered: open_settings_window")
        # Create and show the settings dialog
        
        self.settings_dialog = SettingsWindow(self)
        self.settings_dialog.show()

    def toggle_always_on_top(self, state):
        global is_on_top
        global is_startup
        if is_startup:
            return
        
        existing_settings = get_window_settings(self.session)
        
        if state == Qt.Checked:
            is_on_top = True
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            is_on_top = False
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

        existing_settings["is_on_top"] = is_on_top
    
        save_window_settings(self.session, existing_settings)

    def post_init(self):
        # Called after the window is created
        restore_window_settings(self.session, self)
        self.show()  # You need to show the window again after changing window flags
    
            
    def post_show_init(self):
        # Called after the window is shown
        restore_window_settings(self.session, self) 

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def moveEvent(self, event):
        save_window_settings_after_resize(self.session, self)

# Define an Enum for dock areas
class DockArea(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'

current_dock_location = DockArea.RIGHT
is_docked = False
   
def InitUI(session, selected_user_id):
    logging.debug("InitUI")
    # Initialize QApplication
    app = QApplication(sys.argv)

    # Initialize QMainWindow
    main_window = MyMainWindow(session, selected_user_id)
    main_window.setWindowTitle('PyMate')
    # restore_window_settings(session, main_window)
    

    # Initialize QToolBar and add it to the bottom of QMainWindow
    toolbar = QToolBar()
    main_window.addToolBar(Qt.TopToolBarArea, toolbar)

    # Add the "Always On-Top" checkbox to the toolbar
    toolbar.addWidget(main_window.always_on_top_checkbox)
    
    # Initialize QToolBar and add it to the bottom of QMainWindow
    toolbar = QToolBar()
    main_window.addToolBar(Qt.BottomToolBarArea, toolbar)

    # Add the "Settings" button to the toolbar
    toolbar.addWidget(main_window.settings_button)

    # Initialize QToolButton for docking and add it to the right of the toolbar
    dock_button = QToolButton()
    dock_button.setText('Dock')

    # Add a spacer to push the button to the right
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    toolbar.addWidget(spacer)
    toolbar.addWidget(dock_button)

    # Initialize QMenu for docking options
    dock_menu = QMenu()
    
    def dock_top():
        set_docking(True, main_window, session, DockArea.TOP)

    def dock_bottom():
        set_docking(True, main_window, session, DockArea.BOTTOM)

    def dock_left():
        set_docking(True, main_window, session, DockArea.LEFT)

    def dock_right():
        set_docking(True, main_window, session, DockArea.RIGHT)

    def undock():
        set_docking(False, main_window, session)

    dock_menu.addAction('Top', dock_top)
    dock_menu.addAction('Bottom', dock_bottom)
    dock_menu.addAction('Left', dock_left)
    dock_menu.addAction('Right', dock_right)
    dock_menu.addAction('Undock', undock)

    # Attach QMenu to QToolButton
    dock_button.setMenu(dock_menu)
    dock_button.setPopupMode(QToolButton.InstantPopup)

    # Initialize System Tray Icon and set its properties
    tray_icon = QSystemTrayIcon(QIcon('res/icon_white.png'))
    tray_icon.setVisible(True)
    
    # Initialize QMenu (context menu for tray icon)
    tray_menu = QMenu()

    # Function to toggle window visibility and docking
    def toggle_window():
        if main_window.isVisible():
            main_window.hide()
        else:
            main_window.show()
            # set_docking(is_docked, main_window, session, current_dock_location)

    
    # Add "Show/Hide" action
    toggle_action = QAction("Show/Hide")
    toggle_action.triggered.connect(toggle_window)
    tray_menu.addAction(toggle_action)
    
    # Add "Exit" action with confirmation
    exit_action = QAction("Exit")
    def confirm_exit():
        reply = QMessageBox.question(None, 'Confirm Exit', 'Are you sure you want to exit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()
    exit_action.triggered.connect(confirm_exit)
    tray_menu.addAction(exit_action)
    
    # Set the context menu for the tray icon
    tray_icon.setContextMenu(tray_menu)
    
    # Connect double-click signal to toggle_window
    tray_icon.activated.connect(lambda reason: toggle_window() if reason == QSystemTrayIcon.DoubleClick else None)
    
    # def trigger_resize():
    #    logging.debug("Manually triggering resizeEvent")
    #    main_window.resizeEvent(None)

    def clear_startup_var():
        global is_startup
        is_startup = False
        
    
    QTimer.singleShot(1000, clear_startup_var) 

    # is_startup = False
    # Main Loop to keep the app running
    app.exec_()

def save_window_settings_after_resize(session, main_window):
    global is_docked
    global just_undocked
    global is_startup

    if is_startup:
        return

    logging.debug("Triggered: save_window_settings_after_resize")
    logging.debug(f"Is Docked: {is_docked}, Just Undocked: {just_undocked}")
    
    # Retrieve existing settings from the database (assuming a function 'get_window_settings' exists)
    existing_settings = get_window_settings(session)
    
    if is_docked:  # If the window is docked (frameless)
        settings = {
            'is_docked': is_docked,
            'is_on_top': is_on_top,
            'dock_location': existing_settings.get('dock_location', DockArea.RIGHT),
            'dock_width': main_window.width() if current_dock_location in [DockArea.LEFT, DockArea.RIGHT] else existing_settings['dock_width'],
            'dock_height': main_window.height() if current_dock_location in [DockArea.TOP, DockArea.BOTTOM] else existing_settings['dock_height'],
            'position': existing_settings['position'],
            'size': existing_settings['size']
        }
    else:  # If the window is not docked
        # if just_undocked:
        #    just_undocked = False  # Reset the flag
        #    logging.debug(f"just_undocked set to False")
                
        #    # Apply the saved settings to the window here
        #    prev_pos = existing_settings.get('position', QPoint())
        #    prev_size = existing_settings.get('size', QSize(800, 600))
            
        #    main_window.setGeometry(prev_pos.x(), prev_pos.y(), prev_size.width(), prev_size.height())
        #    main_window.setFixedSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)  # Reset to allow resizing
        # else:
            settings = {
                'is_docked': is_docked,
                'is_on_top': is_on_top,
                'dock_location': existing_settings.get('dock_location', DockArea.RIGHT),
                'dock_width': existing_settings.get('dock_width', 400),
                'dock_height': existing_settings.get('dock_height', 400),
                'position': main_window.pos(),
                'size': main_window.size()
            }

            logging.debug(f"Saving Settings: {settings}")
            save_window_settings(session, settings)
            logging.debug("Settings Saved")


# Function to restore window settings
def restore_window_settings(session, main_window):
    global is_docked  # Declare the global variable
    global is_on_top  # Declare the global variable
    logging.debug("Triggered: restore_window_settings")
    
    # Retrieve existing settings from the database (assuming a function 'get_window_settings' exists)
    existing_settings = get_window_settings(session)
    
    is_on_top = existing_settings.get('is_on_top', False)

    # Retrieve the dock location, dock width, and dock height from the existing settings
    # dock_location = existing_settings.get('dock_location', DockArea.RIGHT)
    # dock_width = existing_settings.get('dock_width', 400)
    # dock_height = existing_settings.get('dock_height', 400)

    # Retrieve and set the docked state
    is_docked = existing_settings.get('is_docked', False)

    main_window.always_on_top_checkbox.setChecked(is_on_top)

    # New Line: Log the restored settings
    logging.debug(f"Restored Settings: {existing_settings}")

    main_window.show()
        
    if is_docked:
        # save_window_settings(session, existing_settings)
        set_docking(True, main_window, session, existing_settings.get('dock_location', DockArea.RIGHT))
    else:
        set_docking(False, main_window, session)

    logging.debug("Restoration Complete")

# Function to set/unset docking
def set_docking(set_is_docked, main_window, session, dock_area=None):
    global current_dock_location
    global is_docked
    global just_undocked
    logging.debug("Triggered: set_docking")

    existing_settings = get_window_settings(session)

    is_docked = set_is_docked

    logging.debug(f"Set Docking - Is Docked: {is_docked}, Dock Area: {dock_area}")
    logging.debug(f"Set Docking - Existing Settings: {existing_settings}")

    if not is_docked:  # If we're undocking
        just_undocked = True  # Set the flag here
        logging.debug(f"just_undocked set to True")

    existing_settings["is_docked"] = is_docked
    
    if dock_area is not None:
        existing_settings["dock_location"] = dock_area

    if "dock_location" not in existing_settings:
        existing_settings["dock_location"] = DockArea.RIGHT


    if "dock_width" not in existing_settings:
        existing_settings["dock_width"] = 400
    
    if "dock_height" not in existing_settings:
        existing_settings["dock_height"] = 400

    dock_width = existing_settings.get('dock_width', 400)
    dock_height = existing_settings.get('dock_height', 400)

    if dock_width is None:
        dock_width = 400  # Set to default or some other value
    if dock_height is None:
        dock_height = 400  # Set to default or some other value

    logging.debug(f"Set Docking - Is Docked: {is_docked}, Dock Area: {dock_area}")
    logging.debug(f"Set Docking - Existing Settings: {existing_settings}")
    logging.debug(f"Set Docking - Just Undocked: {just_undocked}")

    if is_docked:
        logging.debug(f"Before Geometry Set - Window Geometry: {main_window.geometry()}")
    
        # Get screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        current_dock_location = dock_area
        existing_settings['position'] = main_window.pos()
        existing_settings['size'] = main_window.size()
        
        logging.debug(f"Is Window Visible: {main_window.isVisible()}")

        main_window.show()
        
        def apply_undocked_geometry():
            if dock_area in [DockArea.TOP, DockArea.BOTTOM]:
                main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)
            else: # DockArea.LEFT or DockArea.RIGHT
                main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)

            main_window.setWindowFlags(main_window.windowFlags() | Qt.FramelessWindowHint)
            
            main_window.show()  # Refresh the window state after changing flags and geometry
            logging.debug(f"New Window Geometry: {main_window.geometry()}")

            x, y = 0, 0  # Initialize coordinates

            if dock_area == DockArea.TOP:
                main_window.setGeometry(x, y, screen_geometry.width(), dock_height)
                main_window.setFixedSize(screen_geometry.width(), dock_height)
            elif dock_area == DockArea.BOTTOM:
                y = screen_geometry.height() - dock_height
                main_window.setGeometry(x, y, screen_geometry.width(), dock_height)
                main_window.setFixedSize(screen_geometry.width(), dock_height)
            elif dock_area == DockArea.LEFT:
                main_window.setGeometry(x, y, dock_width, screen_geometry.height())
                main_window.setFixedSize(dock_width, screen_geometry.height())
            elif dock_area == DockArea.RIGHT:
                x = screen_geometry.width() - dock_width
                main_window.setGeometry(x, y, dock_width, screen_geometry.height())
                main_window.setFixedSize(dock_width, screen_geometry.height())
            main_window.show()

            logging.debug(f"After Geometry Set - Window Geometry: {main_window.geometry()}")
        
            if not is_startup:
                save_window_settings(session, existing_settings)
        
        QTimer.singleShot(100, apply_undocked_geometry)
    else:
        # Temporarily hide the main window to set new flags and geometry
        main_window.hide()

        logging.debug(f"Before Reset - Window Geometry: {main_window.geometry()}")  # Debug line

        # Reset window flags to default (this will remove the frameless window hint)
        main_window.setWindowFlags(Qt.Window)

        # Retrieve and set the previous position and size
        prev_pos = existing_settings.get('position', QPoint())
        prev_size = existing_settings.get('size', QSize(800, 600))

        # Restore the geometry
        # main_window.setGeometry(prev_pos.x(), prev_pos.y(), prev_size.width(), prev_size.height())
        
        # Explicitly allow resizing
        main_window.setFixedSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)

        logging.debug(f"After Reset - Window Geometry: {main_window.geometry()}")  # Debug line

        def apply_geometry():
            # Explicitly reapply the saved position after showing the window
            main_window.move(prev_pos)
            # Explicitly reapply the saved geometry after showing the window
            main_window.resize(prev_size.width(), prev_size.height())
            logging.debug(f"Final - Window Geometry: {main_window.geometry()}")  # Debug line to confirm final state
        

        # Show the window to apply the new settings
        main_window.show()

        # Use a QTimer to apply the geometry after a slight delay
        QTimer.singleShot(100, apply_geometry)

        logging.debug(f"After Show - Window Geometry: {main_window.geometry()}")  # Debug line
        if not is_startup:
            save_window_settings(session, existing_settings)

    logging.debug(f"New Docking Geometry: {main_window.geometry()}")