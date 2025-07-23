import sys
import ftd2xx
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QGroupBox, QRadioButton
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# FTDI initialisieren
dev = ftd2xx.open(0)
dev.setBitMode(0xFF, 1)
current_state = 0b0000  # alle Relais aus

def schalteRelais(relaisNr, onOff):
    global current_state
    bit_position = relaisNr - 1
    if onOff:
        current_state |= (1 << bit_position)
    else:
        current_state &= ~(1 << bit_position)
    dev.write(bytes([current_state]))

class LedLabel(QLabel):
    def __init__(self, diameter=18, color="#7f8c8d", parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        self.set_color(color)

    def set_color(self, color):
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {self.diameter//2}px;
            border: 2px solid #444;
        """)

class RelayApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SainSmart 4-Kanal Relais GUI")
        self.setFixedSize(800, 220)  # Fensterbreite erhöht
        self.relay_states = [False] * 4
        self.leds = []
        self.buttons = []
        self.button_styles = [
            {"bg": "#16a085", "hover": "#1abc9c", "border": "#27ae60"},
            {"bg": "#2980b9", "hover": "#3498db", "border": "#2980b9"},
            {"bg": "#8e44ad", "hover": "#9b59b6", "border": "#8e44ad"},
            {"bg": "#e67e22", "hover": "#f39c12", "border": "#e67e22"},
        ]
        self.button_labels = ["Staubsauger", "Luftkuehlung", "MMS", "Beleuchtung"]
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 10)
        main_layout.setSpacing(0)

        # Relais-Panel
        frame = QFrame()
        frame_layout = QHBoxLayout(frame)
        frame_layout.setSpacing(20)
        main_layout.addWidget(frame)

        for i in range(4):
            col_layout = QVBoxLayout()
            col_layout.setAlignment(Qt.AlignTop)
            # LED
            led = LedLabel()
            col_layout.addWidget(led, alignment=Qt.AlignHCenter)
            self.leds.append(led)
            # Button
            btn = QPushButton(self.button_labels[i])
            btn.setFixedSize(150, 40)
            btn.setFont(QFont("Helvetica Neue", 14, QFont.Bold))
            btn.setStyleSheet(self.button_style(i, False))
            btn.clicked.connect(lambda checked, idx=i: self.toggle_relay(idx))
            self.buttons.append(btn)
            col_layout.addWidget(btn, alignment=Qt.AlignHCenter)
            frame_layout.addLayout(col_layout)


        # --- Theme Panel and "Alle Relais AUS" Button ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Theme Panel
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout()
        self.theme_radio_light = QRadioButton("Light")
        self.theme_radio_dark = QRadioButton("Dark")
        self.theme_radio_light.setChecked(True)
        theme_layout.addWidget(self.theme_radio_light)
        theme_layout.addWidget(self.theme_radio_dark)
        theme_group.setLayout(theme_layout)
        bottom_layout.addWidget(theme_group, alignment=Qt.AlignLeft)

        # "Alle Relais AUS"-Button
        all_off_btn = QPushButton("Alle Relais AUS")
        all_off_btn.setFixedSize(220, 36)
        all_off_btn.setFont(QFont("Helvetica Neue", 15, QFont.Bold))
        all_off_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border-radius: 18px;
                border: 2px solid #e74c3c;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        all_off_btn.clicked.connect(self.all_off)
        bottom_layout.addWidget(all_off_btn, alignment=Qt.AlignLeft)

        main_layout.addLayout(bottom_layout)
        main_layout.setSpacing(18)

        # Theme switching
        self.theme_radio_light.toggled.connect(self.set_light_theme)
        self.theme_radio_dark.toggled.connect(self.set_dark_theme)

    def button_style(self, idx, active):
        style = self.button_styles[idx]
        if active:
            return f"""
                QPushButton {{
                    background-color: {style['bg']};
                    color: white;
                    border-radius: 20px;
                    border: 3px solid {style['border']};
                }}
                QPushButton:hover {{
                    background-color: {style['hover']};
                }}
            """
        else:
            return """
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border-radius: 20px;
                    border: 3px solid #7f8c8d;
                }
                QPushButton:hover {
                    background-color: #b0b0b0;
                }
            """

    def toggle_relay(self, idx):
        state = self.relay_states[idx]
        self.relay_states[idx] = not state
        schalteRelais(idx + 1, not state)
        self.update_light(idx)

    def update_light(self, idx):
        # LED-Farbe
        color = "#FFFF00" if self.relay_states[idx] else "#7f8c8d"
        self.leds[idx].set_color(color)
        # Button-Farbe
        self.buttons[idx].setStyleSheet(self.button_style(idx, self.relay_states[idx]))

    def all_off(self):
        global current_state
        current_state = 0b0000
        dev.write(bytes([current_state]))
        for i in range(4):
            self.relay_states[i] = False
            self.update_light(i)

    def closeEvent(self, event):
        self.all_off()
        dev.close()
        event.accept()

    def set_light_theme(self):
        if self.theme_radio_light.isChecked():
            self.setStyleSheet("""
                QGroupBox { border: 1px solid #bbb; border-radius: 12px; margin-top: 6px; }
                QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
                QPushButton:hover { background-color: #cce6ff; color: #003366; border: 2px solid #3399ff; }
                QLabel { color: #222; }
            """)

    def set_dark_theme(self):
        if self.theme_radio_dark.isChecked():
            self.setStyleSheet("""
                QWidget { background-color: #232629; color: #f0f0f0; }
                QLineEdit, QPlainTextEdit, QTextEdit { background-color: #31363b; color: #f0f0f0; }
                QPushButton { background-color: #31363b; color: #f0f0f0; border: 1px solid #555; }
                QPushButton:hover { background-color: #0078d7; color: #ffffff; border: 2px solid #00aaff; }
                QGroupBox { border: 1px solid #555; border-radius: 12px; margin-top: 6px; }
                QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RelayApp()
    window.show()
    sys.exit(app.exec())
