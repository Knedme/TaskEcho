from PyQt6.QtWidgets import QDialog
from PyQt6 import uic


class PlayConfigDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/config.ui', self)

        # Save user's chocie
        self.cancelled = True
        self.is_fixed = False
        self.repetitions = 0
        self.is_infinite = False
        self.speed = 0

        # Connect the callback methods
        self.fixed_radio.toggled.connect(self.fixed_option_callback)
        self.infinite_radio.toggled.connect(self.infinite_option_callback)
        self.button_box.accepted.connect(self.accept_callback)

    def fixed_option_callback(self):
        if self.fixed_radio.isChecked():
            # Enable the spin box
            self.fixed_spin.setEnabled(True)

    def infinite_option_callback(self):
        if self.infinite_radio.isChecked():
            # Disable the spin box for 'fixed' if another option is selected
            self.fixed_spin.setEnabled(False)

    def accept_callback(self):
        # Fill in user's choice when the dialog is accepted
        self.cancelled = False
        self.is_fixed = self.fixed_radio.isChecked()
        self.repetitions = self.fixed_spin.value()
        self.is_infinite = self.infinite_radio.isChecked()

        # Convert the speed slider's value to an actual one
        val = self.speed_slider.value()
        if val <= 4:
            self.speed = val / 4
        else:
            self.speed = (val - 4) * 2

