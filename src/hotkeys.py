from pynput.keyboard import GlobalHotKeys


class Hotkeys:

    def __init__(self, main_window):
        # Allows to enable/disable each hotkey
        self.toggle = {
            'play': False,
            'record': True,
            'stop': False,
            'open': True,
            'save': False
        }

        # Use pynput's GlobalHotKeys class to detect hotkey presses across the system
        self.listener = GlobalHotKeys({
            # Bind the callbacks
            # We want the callbacks to run in the main thread, so we just click on
            # the buttons programmatically instead of calling the methods directly
            '<ctrl>+<alt>+p': lambda: self.handle('play', main_window.play_btn.click),
            '<ctrl>+<alt>+r': lambda: self.handle('record', main_window.record_btn.click),
            '<ctrl>+<alt>+s': lambda: self.handle('stop', main_window.stop_btn.click),
            '<ctrl>+<alt>+o': lambda: self.handle('open', main_window.open_btn.click),
            '<ctrl>+<alt>+n': lambda: self.handle('save', main_window.save_btn.click),
        })
        self.listener.start()

    def handle(self, key, func):
        if key in self.toggle and self.toggle[key]:
            func()
