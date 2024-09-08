from enum import Enum
from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6 import uic, QtCore
from time import time as get_time, sleep
from pynput.mouse import Listener as MouseListener, Controller as MouseController
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, Key, KeyCode
from threading import Thread
from pickle import dump, load
from os.path import basename
from config_dlg import PlayConfigDialog


# Action type enum for convenience
class ActionType(Enum):
    M_MOVE = 0
    M_CLICK = 1
    M_SCROLL = 2
    K_PRESS = 3
    K_RELEASE = 4


class MainWindow(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/main.ui', self)

        self.actions_list = []  # Store user's recorded actions
        
        # Mouse and keyboard listeners will be stored here
        self.mouse_listener = None
        self.keyboard_listener = None

        # Used to display loaded file name in the status bar
        self.loaded_file = ''

        # Add a flag to make the window stay on top
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.move(50, 50)  # Move the window to the side of the screen

        # Disable the buttons that can't be used now
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        # Connect the callback methods
        self.record_btn.clicked.connect(self.record_callback)
        self.open_btn.clicked.connect(self.open_callback)
        self.stop_btn.clicked.connect(self.stop_callback)
        self.play_btn.clicked.connect(self.play_callback)
        self.save_btn.clicked.connect(self.save_callback)

        # Show a hint in the status bar
        self.status_bar.showMessage('Ready. Use \'Record\' or \'Open from file\'.')
    
    def record_callback(self):
        # Make the stop button the only available one
        self.play_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.open_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.actions_list = []  # Reset the actions list

        # Set up the mouse and keyboard listeners
        time = get_time()  # Used to get the interval between actions
        def add_action(action_type, *args):
            nonlocal time
            now = get_time()
            interval = round(now - time, 4)  # The interval is rounded to 4 decimal places
            time = now
            self.actions_list.append((interval, action_type, *args))
        self.mouse_listener = MouseListener(
            on_move=lambda x, y: add_action(ActionType.M_MOVE, x, y),
            # The x, y parameters are skipped because we already have on_move
            on_click=lambda _, __, button, pressed: add_action(ActionType.M_CLICK, button, pressed),
            on_scroll=lambda _, __, dx, dy: add_action(ActionType.M_SCROLL, dx, dy))
        self.keyboard_listener = KeyboardListener(
            on_press=lambda key: add_action(ActionType.K_PRESS, key),
            on_release=lambda key: add_action(ActionType.K_RELEASE, key))

        # Display a message to notify the user
        self.status_bar.setStyleSheet(self.status_bar.styleSheet() + '\ncolor: red;')
        self.status_bar.showMessage('Recording...')

        # Start listening
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_callback(self):
        # Enable all the buttons except the stop button
        self.play_btn.setEnabled(True)
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.open_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

        # Stop and remove the mouse and keyboard listeners
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        self.mouse_listener = None
        self.keyboard_listener = None

        # Display a message to notify the user
        self.status_bar.setStyleSheet(self.status_bar.styleSheet().replace('\ncolor: red;', ''))
        self.status_bar.showMessage('Stopped. The recording is saved in memory.')

    def play_callback(self):
        # Lock the buttons
        self.play_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        # Summon the config dialog
        dialog = PlayConfigDialog(self)
        dialog.show()
        dialog.exec()

        # Called when the play button ends its work
        def on_end():
            # Unlock the buttons when the loop is over
            self.play_btn.setEnabled(True)
            self.record_btn.setEnabled(True)
            self.open_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            # Display another message
            self.status_bar.setStyleSheet(self.status_bar.styleSheet().replace('\ncolor: green;', ''))
            if self.loaded_file:
                self.status_bar.showMessage('Loaded ' + self.loaded_file)
            else:
                self.status_bar.showMessage('The recording is saved in memory.')

        # Return if user closed the dialog
        if dialog.cancelled:
            on_end()
            return

        # Display a message to notify the user
        self.status_bar.setStyleSheet(self.status_bar.styleSheet() + '\ncolor: green;')
        self.status_bar.showMessage('Replaying... Don\'t touch mouse/keyboard.')

        cancel_key = Key.esc
        loop_cancelled = False
        # Used to detect if the cancel key was pressed or released by the program itself
        software_cancel_press = False

        # Playback loop
        def playback_loop():
            nonlocal software_cancel_press
            mouse = MouseController()
            keyboard = KeyboardController()
            # The loop is configured by user
            i = 0
            while dialog.is_infinite or i < dialog.repetitions:
                i += 1
                for interval, action_type, *args in self.actions_list:
                    # Wait for the interval with the configured speed
                    sleep(interval / dialog.speed)
                    # Stop the loop if cancelled
                    if loop_cancelled:
                        return
                    # Do the action
                    match action_type:
                        case ActionType.M_MOVE:
                            mouse.position = args
                        case ActionType.M_CLICK:
                            button = args[0]
                            pressed = args[1]
                            if pressed: mouse.press(button)
                            else: mouse.release(button)
                        case ActionType.M_SCROLL:
                            mouse.scroll(*args)
                        case ActionType.K_PRESS:
                            key = args[0]
                            software_cancel_press = key == cancel_key
                            keyboard.press(key)
                        case ActionType.K_RELEASE:
                            key = args[0]
                            software_cancel_press = key == cancel_key
                            keyboard.release(key)
            cancel_listener.stop()  # Stop listening to cancel key presses
            on_end()  # Call on_end when the loop is over

        # Listen to cancel key presses
        def detect_cancel(key):
            nonlocal software_cancel_press, loop_cancelled
            if key == cancel_key and not software_cancel_press:
                loop_cancelled = True
                on_end()
                return False
            # Reset the flag
            software_cancel_press = False
        cancel_listener = KeyboardListener(on_press=detect_cancel, on_release=detect_cancel)
        cancel_listener.start()

        # Run the playback loop in a separate thread
        th = Thread(target=playback_loop, daemon=True)
        th.start()

    def save_callback(self):
        # Make the user choose where to save the file
        path, _ = QFileDialog.getSaveFileName(self, 'Save to a file', './file.rec', 'Recording (*.rec)')
        if path:
            # Open the file in binary mode and dump the action list using pickle
            with open(path, 'wb') as f:
                dump(self.actions_list, f)

            # Display a message to notify the user
            self.status_bar.showMessage('Exported to ' + basename(path))

    def open_callback(self):
        # Now make the user choose where to open the file
        path, _ = QFileDialog.getOpenFileName(self, 'Open from file', '', 'Recording (*.rec)')
        if path:
            # Open the file in binary mode and load the action list using pickle
            filename = basename(path)
            try:
                with open(path, 'rb') as f:
                    self.actions_list = load(f)
            except Exception:
                # If any error occurs, display an error message
                self.status_bar.showMessage('Couldn\'t open ' + filename)
                return
            
            # Unlock the buttons
            self.play_btn.setEnabled(True)
            self.record_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.open_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            # Display a message about the success
            self.loaded_file = filename
            self.status_bar.showMessage('Loaded ' + self.loaded_file)

