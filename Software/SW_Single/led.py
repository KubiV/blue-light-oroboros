import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QSlider, QPushButton, QLineEdit, QLabel, QWidget, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
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

        self.layout = QVBoxLayout()

        # Serial port selection
        self.port_selector = QComboBox()
        self.refresh_ports()
        self.port_selector.currentTextChanged.connect(self.connect_to_port)
        self.layout.addWidget(QLabel("Select Serial Port"))
        self.layout.addWidget(self.port_selector)

        # Brightness Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.valueChanged.connect(self.send_brightness)
        self.layout.addWidget(QLabel("Brightness Slider"))
        self.layout.addWidget(self.slider)

        # Text input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter brightness (0-255)")
        self.layout.addWidget(self.input_field)

        # Submit Button
        self.submit_button = QPushButton("Set Brightness")
        self.submit_button.clicked.connect(self.set_brightness_from_input)
        self.layout.addWidget(self.submit_button)

        # Connect Enter key to the Submit Button
        self.input_field.returnPressed.connect(self.submit_button.click)

        # Control Buttons
        self.button_min = QPushButton("Set Min Brightness")
        self.button_min.clicked.connect(lambda: self.update_slider_and_send(0))
        self.layout.addWidget(self.button_min)

        self.button_mid = QPushButton("Set Mid Brightness")
        self.button_mid.clicked.connect(lambda: self.update_slider_and_send(128))
        self.layout.addWidget(self.button_mid)

        self.button_max = QPushButton("Set Max Brightness")
        self.button_max.clicked.connect(lambda: self.update_slider_and_send(255))
        self.layout.addWidget(self.button_max)

        self.setLayout(self.layout)

        # Serial connection
        self.arduino = None
        self.serial_thread = None

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

    def set_brightness_from_input(self):
        """Send brightness value from text input."""
        if not self.arduino or not self.arduino.is_open:
            QMessageBox.warning(self, "No Connection", "Please connect to a serial port first.")
            return

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

    def closeEvent(self, event):
        """Stop the serial thread on application exit."""
        if self.serial_thread:
            self.serial_thread.stop()
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        super().closeEvent(event)


app = QApplication(sys.argv)
window = LEDControlApp()
window.show()
sys.exit(app.exec_())