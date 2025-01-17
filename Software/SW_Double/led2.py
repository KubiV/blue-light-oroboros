import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLineEdit, QLabel, QWidget,
    QComboBox, QMessageBox, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import serial
from serial.tools import list_ports


class SerialReaderThread(QThread):
    brightness_received = pyqtSignal(str, int)  # Signal for LED ID and brightness value

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True

    def run(self):
        while self.running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    line = self.serial_port.readline().decode().strip()
                    if line.startswith("BRIGHTNESS1:") or line.startswith("BRIGHTNESS2:"):
                        led_id, value = line.split(":")
                        self.brightness_received.emit(led_id, int(value))
                except (ValueError, IndexError, serial.SerialException):
                    continue

    def stop(self):
        self.running = False
        self.wait()


class LEDControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LED Brightness Control")

        # Main layout
        self.main_layout = QVBoxLayout()

        # Section: Port settings
        self.port_group = QGroupBox("Port Settings")
        self.port_layout = QVBoxLayout()
        self.port_selector = QComboBox()
        self.refresh_ports()
        self.port_selector.currentTextChanged.connect(self.connect_to_port)
        self.port_layout.addWidget(QLabel("Select Serial Port:"))
        self.port_layout.addWidget(self.port_selector)
        self.port_group.setLayout(self.port_layout)
        self.main_layout.addWidget(self.port_group)

        # LED controls
        self.led_controls = {}
        self.timers = {}  # Store separate timers for each LED
        self.remaining_times = {}  # Dictionary to store remaining times for each LED

        led_layout = QHBoxLayout()  # Layout to place LED controls side by side
        for led_id in [1, 2]:  # Add controls for LED 1 and LED 2
            self.led_controls[led_id] = self.create_led_controls(led_id)
            led_layout.addWidget(self.led_controls[led_id]["group"])

        self.main_layout.addLayout(led_layout)

        # New section: Combined Timer for both LEDs
        self.combined_timer_group = QGroupBox("Combined Timer for Both LEDs")
        self.combined_timer_layout = QVBoxLayout()

        self.sync_brightness_checkbox = QCheckBox("Sync Brightness for Both LEDs")
        self.sync_brightness_checkbox.stateChanged.connect(self.toggle_sync_brightness)
        self.combined_timer_layout.addWidget(self.sync_brightness_checkbox)

        brightness_layout_1 = QHBoxLayout()
        brightness_layout_1.addWidget(QLabel("LED 1"))
        self.combined_brightness_input_1 = QLineEdit()
        self.combined_brightness_input_1.setPlaceholderText("Brightness for LED 1 (0-255):")
        brightness_layout_1.addWidget(self.combined_brightness_input_1)
        self.combined_timer_layout.addLayout(brightness_layout_1)

        brightness_layout_2 = QHBoxLayout()
        brightness_layout_2.addWidget(QLabel("LED 2"))
        self.combined_brightness_input_2 = QLineEdit()
        self.combined_brightness_input_2.setPlaceholderText("Brightness for LED 2 (0-255):")
        brightness_layout_2.addWidget(self.combined_brightness_input_2)
        self.combined_timer_layout.addLayout(brightness_layout_2)

        self.sync_time_checkbox = QCheckBox("Sync Timer Duration for Both LEDs")
        self.sync_time_checkbox.stateChanged.connect(self.toggle_sync_time)
        self.combined_timer_layout.addWidget(self.sync_time_checkbox)

        duration_layout_1 = QHBoxLayout()
        duration_layout_1.addWidget(QLabel("LED 1"))
        self.combined_duration_input_1 = QLineEdit()
        self.combined_duration_input_1.setPlaceholderText("Timer duration for LED 1 (minutes):")
        duration_layout_1.addWidget(self.combined_duration_input_1)
        self.combined_timer_layout.addLayout(duration_layout_1)

        duration_layout_2 = QHBoxLayout()
        duration_layout_2.addWidget(QLabel("LED 2"))
        self.combined_duration_input_2 = QLineEdit()
        self.combined_duration_input_2.setPlaceholderText("Timer duration for LED 2 (minutes):")
        duration_layout_2.addWidget(self.combined_duration_input_2)
        self.combined_timer_layout.addLayout(duration_layout_2)

        self.combined_timer_start_button = QPushButton("Start Combined Timer")
        self.combined_timer_start_button.clicked.connect(self.start_combined_timer)
        self.combined_timer_layout.addWidget(self.combined_timer_start_button)

        # Add pause and reset buttons for combined timer
        combined_timer_buttons_layout = QHBoxLayout()
        self.combined_timer_pause_button = QPushButton("Pause Combined Timer")
        self.combined_timer_pause_button.clicked.connect(self.pause_combined_timer)
        combined_timer_buttons_layout.addWidget(self.combined_timer_pause_button)

        self.combined_timer_reset_button = QPushButton("Reset Combined Timer")
        self.combined_timer_reset_button.clicked.connect(self.reset_combined_timer)
        combined_timer_buttons_layout.addWidget(self.combined_timer_reset_button)

        self.combined_timer_layout.addLayout(combined_timer_buttons_layout)

        self.combined_timer_group.setLayout(self.combined_timer_layout)
        self.main_layout.addWidget(self.combined_timer_group)

        self.setLayout(self.main_layout)

        # Serial connection
        self.arduino = None
        self.serial_thread = None

        # Combined timer
        self.combined_timer = None
        self.combined_remaining_time = 0

    def create_led_controls(self, led_id):
        """Create controls for a single LED."""
        group = QGroupBox(f"LED {led_id} Controls")
        layout = QVBoxLayout()

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 255)
        slider.valueChanged.connect(lambda value: self.send_brightness(value, led_id))
        layout.addWidget(QLabel(f"LED {led_id} Brightness Slider:"))
        layout.addWidget(slider)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter brightness (0-255):")
        layout.addWidget(input_field)

        submit_button = QPushButton(f"Set Brightness for LED {led_id}")
        submit_button.clicked.connect(
            lambda: self.set_brightness_from_input(input_field, slider, led_id)
        )
        layout.addWidget(submit_button)

        # Buttons for setting brightness directly
        brightness_buttons_layout = QHBoxLayout()
        brightness_zero_button = QPushButton("Set to 0")
        brightness_zero_button.clicked.connect(lambda: self.update_slider_and_send(0, slider, input_field, led_id))
        brightness_buttons_layout.addWidget(brightness_zero_button)

        brightness_full_button = QPushButton("Set to 255")
        brightness_full_button.clicked.connect(lambda: self.update_slider_and_send(255, slider, input_field, led_id))
        brightness_buttons_layout.addWidget(brightness_full_button)

        layout.addLayout(brightness_buttons_layout)

        # Timer group
        timer_group = QGroupBox("Timer")
        timer_layout = QVBoxLayout()
        timer_countdown_label = QLabel("Time remaining: 00:00")
        timer_layout.addWidget(timer_countdown_label)

        timer_brightness_input = QLineEdit()
        timer_brightness_input.setPlaceholderText("Brightness for timer (0-255):")
        timer_layout.addWidget(timer_brightness_input)

        timer_duration_input = QLineEdit()
        timer_duration_input.setPlaceholderText("Timer duration (minutes):")
        timer_layout.addWidget(timer_duration_input)

        timer_buttons_layout = QHBoxLayout()
        timer_start_button = QPushButton("Start")
        timer_start_button.clicked.connect(
            lambda: self.start_timer(
                slider, timer_brightness_input, timer_duration_input, timer_countdown_label, led_id
            )
        )
        timer_buttons_layout.addWidget(timer_start_button)

        timer_pause_button = QPushButton("Pause")
        timer_pause_button.clicked.connect(lambda: self.pause_timer(timer_pause_button, led_id))
        timer_buttons_layout.addWidget(timer_pause_button)

        timer_reset_button = QPushButton("Reset")
        timer_reset_button.clicked.connect(lambda: self.reset_timer(led_id, slider, timer_countdown_label))
        timer_buttons_layout.addWidget(timer_reset_button)

        timer_layout.addLayout(timer_buttons_layout)
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)

        group.setLayout(layout)

        return {
            "group": group,
            "slider": slider,
            "input_field": input_field,
            "timer_countdown_label": timer_countdown_label,
            "timer_brightness_input": timer_brightness_input,
            "timer_duration_input": timer_duration_input,
            "timer_pause_button": timer_pause_button,
        }

    def refresh_ports(self):
        ports = list_ports.comports()
        self.port_selector.clear()
        self.port_selector.addItem("Select a port...")
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_to_port(self, port_name):
        if port_name == "Select a port...":
            return
        try:
            if self.arduino:
                self.arduino.close()
            self.arduino = serial.Serial(port=port_name, baudrate=9600, timeout=1)
            QMessageBox.information(self, "Connection Successful", f"Connected to {port_name}")

            if self.serial_thread:
                self.serial_thread.stop()
            self.serial_thread = SerialReaderThread(self.arduino)
            self.serial_thread.brightness_received.connect(self.update_slider_from_signal)
            self.serial_thread.start()
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
            self.arduino = None

    def send_brightness(self, value, led_id):
        if self.arduino and self.arduino.is_open:
            self.arduino.write(f"SET{led_id}:{value}\n".encode())

    def start_timer(self, slider, brightness_input, duration_input, countdown_label, led_id):
        try:
            brightness = int(brightness_input.text())
            duration_minutes = float(duration_input.text())
            self.remaining_times[led_id] = int(duration_minutes * 60 * 1000)
            brightness = max(0, min(255, brightness))

            self.update_slider_and_send(brightness, slider, brightness_input, led_id)

            if led_id in self.timers:
                self.timers[led_id].stop()

            self.timers[led_id] = QTimer()
            self.timers[led_id].timeout.connect(
                lambda: self.update_timer_countdown(led_id, slider, countdown_label)
            )
            self.timers[led_id].start(1000)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Enter valid brightness and duration.")

    def update_timer_countdown(self, led_id, slider, countdown_label):
        self.remaining_times[led_id] -= 1000
        if self.remaining_times[led_id] <= 0:
            self.timers[led_id].stop()
            self.update_slider_and_send(0, slider, None, led_id)
            countdown_label.setText("Time remaining: 00:00")
            QMessageBox.information(self, f"LED {led_id} Timer Finished", f"LED {led_id} Timer has finished. Brightness reset to 0.")
        else:
            minutes, seconds = divmod(self.remaining_times[led_id] // 1000, 60)
            countdown_label.setText(f"Time remaining: {minutes:02}:{seconds:02}")

    def pause_timer(self, pause_button, led_id):
        if led_id in self.timers and self.timers[led_id].isActive():
            self.timers[led_id].stop()
            pause_button.setText("Resume")
        elif led_id in self.timers:
            self.timers[led_id].start(1000)
            pause_button.setText("Pause")

    def reset_timer(self, led_id, slider, countdown_label):
        if led_id in self.timers:
            self.timers[led_id].stop()
        self.update_slider_and_send(0, slider, None, led_id)
        countdown_label.setText("Time remaining: 00:00")

    def update_slider_and_send(self, value, slider, input_field, led_id):
        slider.setValue(value)
        if input_field:
            input_field.setText(str(value))
        self.send_brightness(value, led_id)

    def update_slider_from_signal(self, led_id, value):
        led_id = int(led_id[-1])
        controls = self.led_controls.get(led_id)
        if controls:
            slider = controls["slider"]
            input_field = controls["input_field"]
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            input_field.setText(str(value))

    def set_brightness_from_input(self, input_field, slider, led_id):
        try:
            value = int(input_field.text())
            if 0 <= value <= 255:
                self.update_slider_and_send(value, slider, input_field, led_id)
            else:
                QMessageBox.warning(self, "Invalid Input", "Brightness must be between 0 and 255.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Enter a valid integer for brightness.")

    def toggle_sync_brightness(self, state):
        if state == Qt.Checked:
            self.combined_brightness_input_2.setDisabled(True)
            self.combined_brightness_input_2.setText(self.combined_brightness_input_1.text())
        else:
            self.combined_brightness_input_2.setDisabled(False)

    def toggle_sync_time(self, state):
        if state == Qt.Checked:
            self.combined_duration_input_2.setDisabled(True)
            self.combined_duration_input_2.setText(self.combined_duration_input_1.text())
        else:
            self.combined_duration_input_2.setDisabled(False)

    def start_combined_timer(self):
        try:
            brightness_1 = int(self.combined_brightness_input_1.text())
            brightness_2 = int(self.combined_brightness_input_2.text()) if not self.sync_brightness_checkbox.isChecked() else brightness_1
            duration_1 = float(self.combined_duration_input_1.text())
            duration_2 = float(self.combined_duration_input_2.text()) if not self.sync_time_checkbox.isChecked() else duration_1

            self.remaining_times[1] = int(duration_1 * 60 * 1000)
            self.remaining_times[2] = int(duration_2 * 60 * 1000)

            self.update_slider_and_send(brightness_1, self.led_controls[1]["slider"], self.combined_brightness_input_1, 1)
            self.update_slider_and_send(brightness_2, self.led_controls[2]["slider"], self.combined_brightness_input_2, 2)

            if self.combined_timer:
                self.combined_timer.stop()

            self.combined_timer = QTimer()
            self.combined_timer.timeout.connect(self.update_combined_timer_countdown)
            self.combined_timer.start(1000)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Enter valid brightness and duration for both LEDs.")

    def update_combined_timer_countdown(self):
        self.remaining_times[1] -= 1000
        self.remaining_times[2] -= 1000
        if self.remaining_times[1] <= 0 and self.remaining_times[2] <= 0:
            self.combined_timer.stop()
            self.update_slider_and_send(0, self.led_controls[1]["slider"], None, 1)
            self.update_slider_and_send(0, self.led_controls[2]["slider"], None, 2)
            self.led_controls[1]["timer_countdown_label"].setText("Time remaining: 00:00")
            self.led_controls[2]["timer_countdown_label"].setText("Time remaining: 00:00")
            QMessageBox.information(self, "Combined Timer Finished", "Combined Timer has finished. Brightness reset to 0 for both LEDs.")
        else:
            minutes_1, seconds_1 = divmod(self.remaining_times[1] // 1000, 60)
            self.led_controls[1]["timer_countdown_label"].setText(f"Time remaining: {minutes_1:02}:{seconds_1:02}")
            minutes_2, seconds_2 = divmod(self.remaining_times[2] // 1000, 60)
            self.led_controls[2]["timer_countdown_label"].setText(f"Time remaining: {minutes_2:02}:{seconds_2:02}")

    def pause_combined_timer(self):
        if self.combined_timer and self.combined_timer.isActive():
            self.combined_timer.stop()
            self.combined_timer_pause_button.setText("Resume Combined Timer")
        elif self.combined_timer:
            self.combined_timer.start(1000)
            self.combined_timer_pause_button.setText("Pause Combined Timer")

    def reset_combined_timer(self):
        if self.combined_timer:
            self.combined_timer.stop()
        self.remaining_times[1] = 0
        self.remaining_times[2] = 0
        self.update_slider_and_send(0, self.led_controls[1]["slider"], None, 1)
        self.update_slider_and_send(0, self.led_controls[2]["slider"], None, 2)
        self.led_controls[1]["timer_countdown_label"].setText("Time remaining: 00:00")
        self.led_controls[2]["timer_countdown_label"].setText("Time remaining: 00:00")

    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        super().closeEvent(event)


app = QApplication(sys.argv)
window = LEDControlApp()
window.show()
sys.exit(app.exec_())