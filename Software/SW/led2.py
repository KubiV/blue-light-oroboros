import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLineEdit, QLabel, QWidget,
    QComboBox, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import serial
from serial.tools import list_ports


class SerialReaderThread(QThread):
    brightness_received = pyqtSignal(int)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True

    def run(self):
        while self.running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    line = self.serial_port.readline().decode().strip()
                    if line.startswith("BRIGHTNESS:"):
                        value = int(line.split(":")[1])
                        self.brightness_received.emit(value)
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

        # Section: Brightness settings
        self.brightness_group = QGroupBox("Brightness Settings")
        self.brightness_layout = QVBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.valueChanged.connect(self.send_brightness)
        self.brightness_layout.addWidget(QLabel("Brightness Slider:"))
        self.brightness_layout.addWidget(self.slider)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter brightness (0-255):")
        self.brightness_layout.addWidget(self.input_field)

        self.submit_button = QPushButton("Set Brightness")
        self.submit_button.clicked.connect(self.set_brightness_from_input)
        self.brightness_layout.addWidget(self.submit_button)

        self.input_field.returnPressed.connect(self.submit_button.click)

        self.brightness_buttons_layout = QHBoxLayout()
        self.brightness_zero_button = QPushButton("Set to 0")
        self.brightness_zero_button.clicked.connect(lambda: self.update_slider_and_send(0))
        self.brightness_buttons_layout.addWidget(self.brightness_zero_button)

        self.brightness_half_button = QPushButton("Set to 128")
        self.brightness_half_button.clicked.connect(lambda: self.update_slider_and_send(128))
        self.brightness_buttons_layout.addWidget(self.brightness_half_button)

        self.brightness_full_button = QPushButton("Set to 255")
        self.brightness_full_button.clicked.connect(lambda: self.update_slider_and_send(255))
        self.brightness_buttons_layout.addWidget(self.brightness_full_button)

        self.brightness_layout.addLayout(self.brightness_buttons_layout)
        self.brightness_group.setLayout(self.brightness_layout)
        self.main_layout.addWidget(self.brightness_group)

        # Section: Timer
        self.timer_group = QGroupBox("Timer")
        self.timer_layout = QVBoxLayout()
        self.timer_countdown_label = QLabel("Time remaining: 00:00")
        self.timer_layout.addWidget(self.timer_countdown_label)

        self.timer_brightness_input = QLineEdit()
        self.timer_brightness_input.setPlaceholderText("Brightness for timer (0-255):")
        self.timer_layout.addWidget(self.timer_brightness_input)

        self.timer_duration_input = QLineEdit()
        self.timer_duration_input.setPlaceholderText("Timer duration (minutes):")
        self.timer_layout.addWidget(self.timer_duration_input)

        self.timer_buttons_layout = QHBoxLayout()
        self.timer_button = QPushButton("Start")
        self.timer_button.clicked.connect(self.start_timer)
        self.timer_buttons_layout.addWidget(self.timer_button)

        self.timer_pause_button = QPushButton("Pause")
        self.timer_pause_button.clicked.connect(self.pause_timer)
        self.timer_buttons_layout.addWidget(self.timer_pause_button)

        self.timer_reset_button = QPushButton("Reset")
        self.timer_reset_button.clicked.connect(self.reset_timer)
        self.timer_buttons_layout.addWidget(self.timer_reset_button)

        self.timer_layout.addLayout(self.timer_buttons_layout)
        self.timer_group.setLayout(self.timer_layout)
        self.main_layout.addWidget(self.timer_group)

        self.setLayout(self.main_layout)

        # Serial connection
        self.arduino = None
        self.serial_thread = None

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_countdown)
        self.remaining_time_ms = 0

    def refresh_ports(self):
        """Detect available serial ports and populate the combo box."""
        ports = list_ports.comports()
        self.port_selector.clear()
        self.port_selector.addItem("Select a port...")
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_to_port(self, port_name):
        """Attempt to connect to the selected serial port."""
        if port_name == "Select a port...":
            return
        try:
            if self.arduino:
                self.arduino.close()
            self.arduino = serial.Serial(port=port_name, baudrate=9600, timeout=1)
            QMessageBox.information(self, "Connection Successful", f"Connected to {port_name}")

            # Start the serial reader thread
            if self.serial_thread:
                self.serial_thread.stop()
            self.serial_thread = SerialReaderThread(self.arduino)
            self.serial_thread.brightness_received.connect(self.update_slider_and_text_field)
            self.serial_thread.start()
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
            self.arduino = None

    def send_brightness(self, value=None):
        """Send brightness value to Arduino."""
        if self.arduino and self.arduino.is_open:
            if value is None:
                value = self.slider.value()
            self.arduino.write(f"SET:{value}\n".encode())
            print("Brightness: "+str(value))

    def set_brightness_from_input(self):
        """Send brightness value from text input."""
        try:
            value = int(self.input_field.text())
            value = max(0, min(255, value))
            self.update_slider_and_send(value)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number between 0 and 255.")

    def update_slider_and_send(self, value):
        """Update slider position, text field, and send brightness."""
        self.slider.setValue(value)
        self.input_field.setText(str(value))
        self.send_brightness(value)

    def update_slider_and_text_field(self, value):
        """Update slider and text field based on Arduino input."""
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.input_field.setText(str(value))

    def start_timer(self):
        """Start a timer to set brightness and reset it after duration."""
        try:
            brightness = int(self.timer_brightness_input.text())
            duration_minutes = float(self.timer_duration_input.text())
            self.remaining_time_ms = int(duration_minutes * 60 * 1000)
            brightness = max(0, min(255, brightness))

            self.update_slider_and_send(brightness)
            self.timer.start(1000)  # Update every second
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid brightness and duration.")

    def pause_timer(self):
        """Pause or resume the timer."""
        if self.timer.isActive():
            self.timer.stop()
            self.timer_pause_button.setText("Resume")
        else:
            self.timer.start(1000)
            self.timer_pause_button.setText("Pause")

    def reset_timer(self):
        """Reset the timer and brightness."""
        self.timer.stop()
        self.remaining_time_ms = 0
        self.update_slider_and_send(0)
        self.timer_countdown_label.setText("Time remaining: 00:00")
        self.timer_pause_button.setText("Pause")
        #QMessageBox.information(self, "Timer Reset", "Timer has been reset. Brightness set to 0.")

    def update_timer_countdown(self):
        """Update the countdown label with the remaining time."""
        self.remaining_time_ms -= 1000
        if self.remaining_time_ms <= 0:
            self.timer.stop()
            self.update_slider_and_send(0)
            self.timer_countdown_label.setText("Time remaining: 00:00")
            QMessageBox.information(self, "Timer Finished", "Timer has finished. Brightness reset to 0.")
        else:
            minutes, seconds = divmod(self.remaining_time_ms // 1000, 60)
            self.timer_countdown_label.setText(f"Time remaining: {minutes:02}:{seconds:02}")

    def closeEvent(self, event):
        """Stop the serial thread on application exit."""
        if self.serial_thread:
            self.serial_thread.stop()
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        self.timer.stop()
        super().closeEvent(event)


app = QApplication(sys.argv)
window = LEDControlApp()
window.show()
sys.exit(app.exec_())