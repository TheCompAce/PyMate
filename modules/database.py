# Import required libraries
from enum import Enum
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from PyQt5.QtCore import QPoint, QSize

from modules.data.data import User
from modules.data.data import WindowSettings
from modules.data.data import ensure_default_user

# Define an Enum for dock areas
class DockArea(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'

def CreateDatabase():
    """
    Create a SQLite database with the User table
    """

    # Create data folder in the root directory if it does not exist
    data_folder_path = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_folder_path):
        os.makedirs(data_folder_path)

    # Define the database name and path
    db_name = "system.db"
    db_path = os.path.join(data_folder_path, db_name)

    # Create a SQLite database engine
    engine = create_engine(f'sqlite:///{db_path}')

    User.metadata.create_all(engine)
    WindowSettings.metadata.create_all(engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    # Ensure a default user exists
    ensure_default_user(session)

    return session

# Add this line in your CreateDatabase() function to create the WindowSettings table


# Add this method to save window settings
def save_window_settings(session, settings):
    dock_location = settings.get('dock_location', None)
    if dock_location:
        dock_location = dock_location.value if isinstance(dock_location, Enum) else dock_location

    # Check if 'position' key exists before trying to access it
    if 'position' in settings:
        position_x = settings['position'].x()
        position_y = settings['position'].y()
    else:
        position_x, position_y = 0, 0  # Default to (0, 0) if 'position' is not available

    # Check if 'size' key exists before trying to access it
    if 'size' in settings:
        size_width = settings['size'].width()
        size_height = settings['size'].height()
    else:
        size_width, size_height = 800, 600  # Default to (800, 600) if 'size' is not available


    new_setting = WindowSettings(
        position_x=position_x,
        position_y=position_y,
        size_width=size_width,
        size_height=size_height,
        is_docked=settings['is_docked'],
        is_on_top=settings['is_on_top'],
        dock_location=dock_location,
        dock_width=settings['dock_width'],
        dock_height=settings['dock_height']
    )

    new_setting_dict = new_setting.to_dict()

    logging.debug(f"Saved window settings: {json.dumps(new_setting_dict)}")

    session.add(new_setting)
    session.commit()

def get_window_settings(session):
    latest_settings = session.query(WindowSettings).order_by(WindowSettings.id.desc()).first()

    if latest_settings:
        dock_location = latest_settings.dock_location
        if dock_location:
            dock_location = DockArea(dock_location)

        
            
        settings = {
            'position': QPoint(latest_settings.position_x, latest_settings.position_y),
            'size': QSize(latest_settings.size_width, latest_settings.size_height),
            'is_docked': latest_settings.is_docked,
            'is_on_top': latest_settings.is_on_top,
            'dock_location': dock_location,
            'dock_width': latest_settings.dock_width,
            'dock_height': latest_settings.dock_height
        }

        logging.debug(f"Loaded window settings: {settings}")

        return settings
    
    logging.debug(f" Window settings not found")

    return {}