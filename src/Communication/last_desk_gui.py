import sys
import serial
import struct
import json
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# ----------------------------
# GUI 코드
# ----------------------------
class MainScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()

        self.label = QLabel("User ID : None")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        grid_layout = QGridLayout()
        buttons = {"Mode 1": None, "Mode 2": None, "Mode 3": None, "Control Mode": 1}
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (text, index), pos in zip(buttons.items(), positions):
            btn = QPushButton(text)
            btn.setFixedSize(140, 160)
            if index is not None:
                btn.clicked.connect(lambda _, i=index: self.stacked_widget.setCurrentIndex(i))
            grid_layout.addWidget(btn, *pos)
        layout.addLayout(grid_layout)
        self.setLayout(layout)

class ControlModeScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()

        self.label = QLabel("Control Mode")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        grid_layout = QGridLayout()
        buttons = {"LED": 2, "Desk": 4, "Monitor": 3, "Back": 0}
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (text, index), pos in zip(buttons.items(), positions):
            btn = QPushButton(text)
            btn.setFixedSize(140, 160)
            btn.clicked.connect(lambda _, i=index: self.stacked_widget.setCurrentIndex(i))
            grid_layout.addWidget(btn, *pos)
        layout.addLayout(grid_layout)
        self.setLayout(layout)

class LEDControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer  # static_board에 명령 전송
        layout = QVBoxLayout()

        self.label = QLabel("LED Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # LED 밝기 값을 보여주는 레이아웃 구성
        data_layout = QVBoxLayout()
        self.up_btn = QPushButton("▲")
        self.up_btn.setFixedSize(80, 80)
        data_layout.addWidget(self.up_btn, alignment=Qt.AlignCenter)

        self.data_value = 0  # 초기 LED 밝기 (0~7)
        self.data_label = QLabel(str(self.data_value))
        self.data_label.setAlignment(Qt.AlignCenter)
        self.data_label.setFixedSize(80, 80)
        data_layout.addWidget(self.data_label, alignment=Qt.AlignCenter)

        self.down_btn = QPushButton("▼")
        self.down_btn.setFixedSize(80, 80)
        data_layout.addWidget(self.down_btn, alignment=Qt.AlignCenter)

        layout.addLayout(data_layout)

        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # 버튼 클릭 시 LED 밝기 조절 (내부 업데이트 + static_board에 명령 전송)
        self.up_btn.clicked.connect(self.increase_data)
        self.down_btn.clicked.connect(self.decrease_data)

    def increase_data(self):
        if self.data_value < 7:
            self.data_value += 1
            self.data_label.setText(str(self.data_value))
            packet = struct.pack('BB', 0xFF, self.data_value)
            self.serial_writer.write_command(packet)
            # 즉시 업데이트 후 디버깅 출력
            print(json.dumps({"desk_gui": "LED up clicked", "led_brightness": self.data_value}, indent=4))

    def decrease_data(self):
        if self.data_value > 0:
            self.data_value -= 1
            self.data_label.setText(str(self.data_value))
            packet = struct.pack('BB', 0xFF, self.data_value)
            self.serial_writer.write_command(packet)
            print(json.dumps({"desk_gui": "LED down clicked", "led_brightness": self.data_value}, indent=4))

    # 외부에서 수신된 LED 밝기 값을 업데이트하는 함수
    def update_brightness(self, value):
        self.data_value = value
        self.data_label.setText(str(value))

class DeskControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer
        layout = QVBoxLayout()

        self.label = QLabel("Desk Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        grid_layout = QGridLayout()
        self.btn_up = QPushButton("▲")
        self.btn_up.setFixedSize(120, 120)
        grid_layout.addWidget(self.btn_up, 0, 1)

        self.data_value_label = QLabel("0")
        self.data_value_label.setAlignment(Qt.AlignCenter)
        self.data_value_label.setFixedSize(120, 120)
        grid_layout.addWidget(self.data_value_label, 1, 1)

        self.btn_down = QPushButton("▼")
        self.btn_down.setFixedSize(120, 120)
        grid_layout.addWidget(self.btn_down, 2, 1)

        layout.addLayout(grid_layout)
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.btn_up.clicked.connect(self.send_up_command)
        self.btn_down.clicked.connect(self.send_down_command)

    def send_up_command(self):
        packet = struct.pack('BB', 0xFD, 0)
        self.serial_writer.write_command(packet)

    def send_down_command(self):
        packet = struct.pack('BB', 0xFD, 1)
        self.serial_writer.write_command(packet)

class MonitorControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer
        layout = QVBoxLayout()

        self.label = QLabel("Monitor Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        grid_layout = QGridLayout()
        self.btn_front = QPushButton("Front")
        self.btn_front.setFixedSize(100, 100)
        self.data_label_front_back = QLabel("Data")
        self.data_label_front_back.setAlignment(Qt.AlignCenter)
        self.data_label_front_back.setFixedSize(100, 100)
        self.btn_back = QPushButton("Back")
        self.btn_back.setFixedSize(100, 100)
        self.btn_up = QPushButton("Up")
        self.btn_up.setFixedSize(100, 100)
        self.data_label_up_down = QLabel("Data")
        self.data_label_up_down.setAlignment(Qt.AlignCenter)
        self.data_label_up_down.setFixedSize(100, 100)
        self.btn_down = QPushButton("Down")
        self.btn_down.setFixedSize(100, 100)
        grid_layout.addWidget(self.btn_front, 0, 0)
        grid_layout.addWidget(self.data_label_front_back, 1, 0)
        grid_layout.addWidget(self.btn_back, 2, 0)
        grid_layout.addWidget(self.btn_up, 0, 1)
        grid_layout.addWidget(self.data_label_up_down, 1, 1)
        grid_layout.addWidget(self.btn_down, 2, 1)
        layout.addLayout(grid_layout)
        nav_back_btn = QPushButton("Back")
        nav_back_btn.setFixedSize(120, 50)
        nav_back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(nav_back_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.btn_front.clicked.connect(self.send_front_command)
        self.btn_back.clicked.connect(self.send_back_command)
        self.btn_up.clicked.connect(self.send_up_command)
        self.btn_down.clicked.connect(self.send_down_command)

    def send_front_command(self):
        packet = struct.pack('BB', 0xFC, 1)
        self.serial_writer.write_command(packet)

    def send_back_command(self):
        packet = struct.pack('BB', 0xFC, 0)
        self.serial_writer.write_command(packet)

    def send_up_command(self):
        packet = struct.pack('BB', 0xFB, 1)
        self.serial_writer.write_command(packet)

    def send_down_command(self):
        packet = struct.pack('BB', 0xFB, 0)
        self.serial_writer.write_command(packet)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt GUI Example")
        self.setFixedSize(320, 480)
        self.stacked_widget = QStackedWidget()

        # 동적 보드와 정적 보드의 시리얼 리더 생성
        self.serial_reader1 = SerialReader(port='/dev/ttyACM2', baudrate=115200, board_label="dynamic_board")
        self.serial_reader2 = SerialReader(port='/dev/ttyACM1', baudrate=9600, board_label="static_board")

        self.serial_reader1.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.dataReceived.connect(self.handle_serial_data)

        self.serial_reader1.start()
        self.serial_reader2.start()

        self.main_screen = MainScreen(self.stacked_widget)
        self.control_mode_screen = ControlModeScreen(self.stacked_widget)
        # LEDControlScreen은 정적 보드와 연동 (serial_reader2 사용)
        self.led_control_screen = LEDControlScreen(self.stacked_widget, serial_writer=self.serial_reader2)
        self.monitor_control_screen = MonitorControlScreen(self.stacked_widget, serial_writer=self.serial_reader1)
        self.desk_control_screen = DeskControlScreen(self.stacked_widget, serial_writer=self.serial_reader1)

        self.stacked_widget.addWidget(self.main_screen)           # index 0
        self.stacked_widget.addWidget(self.control_mode_screen)     # index 1
        self.stacked_widget.addWidget(self.led_control_screen)      # index 2
        self.stacked_widget.addWidget(self.monitor_control_screen)  # index 3
        self.stacked_widget.addWidget(self.desk_control_screen)     # index 4

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    @pyqtSlot(str, int, int, int)
    def handle_serial_data(self, board, monitor_height, monitor_tilt, desk_height):
        if board == "dynamic_board":
            self.monitor_control_screen.data_label_up_down.setText(str(monitor_height))
            self.monitor_control_screen.data_label_front_back.setText(str(monitor_tilt))
            self.desk_control_screen.data_value_label.setText(str(desk_height))
            data_dict = {
                "board": board,
                "moniter_height": monitor_height,
                "moniter_tilt": monitor_tilt,
                "desk_height": desk_height
            }
            print(json.dumps(data_dict, indent=4))
        elif board == "static_board":
            # 정적 보드의 LED 밝기 값(0~7)을 LEDControlScreen에 업데이트
            self.led_control_screen.update_brightness(monitor_height)
            data_dict = {
                "board": board,
                "led_brightness": monitor_height
            }
            print(json.dumps(data_dict, indent=4))

# ----------------------------
# 시리얼 리더 (QThread 사용, 쓰기 기능 포함)
# ----------------------------
class SerialReader(QThread):
    dataReceived = pyqtSignal(str, int, int, int)  # board, monitor_height, monitor_tilt, desk_height

    def __init__(self, port, baudrate, board_label, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.board_label = board_label
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
        except Exception as e:
            print(f"Error opening {self.port}: {e}")
            self.ser = None

    def run(self):
        if self.ser is None:
            return
        while True:
            try:
                if self.ser.in_waiting > 0:
                    while self.ser.read(1) != b'\xFF':
                        pass
                    if self.board_label == "static_board":
                        data = self.ser.read(3)
                        if len(data) == 3:
                            led_brightness = data[0]
                            print("Static board raw data:", data)
                            self.dataReceived.emit(self.board_label, led_brightness, 0, 0)
                    else:
                        data = self.ser.read(3)
                        if len(data) == 3:
                            monitor_height, monitor_tilt, desk_height = struct.unpack('BBB', data)
                            self.dataReceived.emit(self.board_label, monitor_height, monitor_tilt, desk_height)
            except Exception as e:
                print(f"Error reading from {self.port}: {e}")
                break

    def write_command(self, data: bytes):
        if self.ser is not None:
            try:
                self.ser.write(data)
                print(f"Sent: {data}")
            except Exception as e:
                print(f"Error writing to {self.port}: {e}")

# ----------------------------
# 메인 실행
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
