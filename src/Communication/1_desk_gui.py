import sys
import serial
import struct
import json
import threading
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socketio

# MainScreen: RFID 읽기 및 모드 선택 화면
class MainScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer  # static_board로 명령 전송
        layout = QVBoxLayout()

        self.label = QLabel("User ID : None")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # RFID 읽기 기능을 Mode 버튼에 할당 (각 버튼마다 다른 블록 번호 사용)
        grid_layout = QGridLayout()
        # "Mode 1": 블록 4, "Mode 2": 블록 5, "Mode 3": 블록 6, "Control Mode": 화면 전환
        buttons = {
            "Mode 1": 4,
            "Mode 2": 5,
            "Mode 3": 6,
            "Control Mode": None
        }
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (text, block), pos in zip(buttons.items(), positions):
            btn = QPushButton(text)
            btn.setFixedSize(140, 160)
            if block is not None:
                btn.clicked.connect(lambda _, b=block: self.send_rfid_read_command(b))
            else:
                btn.clicked.connect(lambda _, i=1: self.stacked_widget.setCurrentIndex(i))
            grid_layout.addWidget(btn, *pos)
        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def send_rfid_read_command(self, block):
        # RFID 읽기 명령: 헤더 0xFD, 기능코드 0x04, 블록번호
        packet = struct.pack('BBB', 0xFD, 0x04, block)
        self.serial_writer.write_command(packet)
        print(f"RFID Read 명령 전송: {packet} (블록 {block})")

# ControlModeScreen: 제어 모드 선택 화면
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

# LEDControlScreen: LED 제어 화면 (정적 보드만 업데이트)
class LEDControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer  # static_board에 명령 전송
        self.main_window = main_window

        layout = QVBoxLayout()
        self.label = QLabel("LED Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        data_layout = QVBoxLayout()
        self.up_btn = QPushButton("▲")
        self.up_btn.setFixedSize(80, 80)
        data_layout.addWidget(self.up_btn, alignment=Qt.AlignCenter)

        self.data_value = 0
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

        self.up_btn.clicked.connect(self.increase_data)
        self.down_btn.clicked.connect(self.decrease_data)

    def increase_data(self):
        if self.data_value < 7:
            self.data_value += 1
            self.data_label.setText(str(self.data_value))
            packet = struct.pack('BB', 0xFF, self.data_value)
            self.serial_writer.write_command(packet)
            print(json.dumps({"desk_gui": "LED up clicked", "light": self.data_value}, indent=4))
            self.main_window.current_led_brightness = self.data_value
            self.main_window.send_data_to_server()
            # 정적 보드만 업데이트
            self.main_window.update_static_board()

    def decrease_data(self):
        if self.data_value > 0:
            self.data_value -= 1
            self.data_label.setText(str(self.data_value))
            packet = struct.pack('BB', 0xFF, self.data_value)
            self.serial_writer.write_command(packet)
            print(json.dumps({"desk_gui": "LED down clicked", "light": self.data_value}, indent=4))
            self.main_window.current_led_brightness = self.data_value
            self.main_window.send_data_to_server()
            self.main_window.update_static_board()

    def update_brightness(self, value):
        self.data_value = value
        self.data_label.setText(str(value))

# DeskControlScreen: 책상 높낮이 제어 화면 (동적 보드 업데이트)
class DeskControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer
        self.main_window = main_window

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
        # 상대 명령 전송 (동적 보드에서 임시 처리)
        packet = struct.pack('BB', 0xFD, 0)
        self.serial_writer.write_command(packet)
        self.main_window.current_desk_height += 1
        self.data_value_label.setText(str(self.main_window.current_desk_height))
        self.main_window.send_data_to_server()
        self.main_window.update_dynamic_board()

    def send_down_command(self):
        packet = struct.pack('BB', 0xFD, 1)
        self.serial_writer.write_command(packet)
        if self.main_window.current_desk_height > 0:
            self.main_window.current_desk_height -= 1
        self.data_value_label.setText(str(self.main_window.current_desk_height))
        self.main_window.send_data_to_server()
        self.main_window.update_dynamic_board()

# MonitorControlScreen: 모니터 각도 및 높낮이 제어 화면 (동적 보드 업데이트)
class MonitorControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer
        self.main_window = main_window

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

        self.data_label_front_back.setText(str(self.main_window.current_monitor_angle))
        self.data_label_up_down.setText(str(self.main_window.current_monitor_height))

    def send_front_command(self):
        new_angle = self.main_window.current_monitor_angle + 1
        if new_angle > 255:
            new_angle = 255
        packet = struct.pack('BB', 0xFC, 1)
        self.serial_writer.write_command(packet)
        self.main_window.current_monitor_angle = new_angle
        self.data_label_front_back.setText(str(new_angle))
        self.main_window.send_data_to_server()
        self.main_window.update_dynamic_board()

    def send_back_command(self):
        new_angle = max(0, self.main_window.current_monitor_angle - 1)
        packet = struct.pack('BB', 0xFC, 0)
        self.serial_writer.write_command(packet)
        self.main_window.current_monitor_angle = new_angle
        self.data_label_front_back.setText(str(new_angle))
        self.main_window.send_data_to_server()
        self.main_window.update_dynamic_board()

    def send_up_command(self):
        new_height = self.main_window.current_monitor_height + 1
        if new_height > 255:
            new_height = 255
        packet = struct.pack('BB', 0xFB, 1)
        self.serial_writer.write_command(packet)
        self.main_window.current_monitor_height = new_height
        self.data_label_up_down.setText(str(new_height))
        self.main_window.send_data_to_server()
        self.main_window.update_dynamic_board()

    def send_down_command(self):
        new_height = max(0, self.main_window.current_monitor_height - 1)
        packet = struct.pack('BB', 0xFB, 0)
        self.serial_writer.write_command(packet)
        self.main_window.current_monitor_height = new_height
        self.data_label_up_down.setText(str(new_height))
        self.main_window.send_data_to_server()
        self.main_window.update_dynamic_board()

# MainWindow: 전체 UI 관리 및 서버와 시리얼 통신 처리
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desk GUI Integrated")
        self.setFixedSize(320, 480)
        self.stacked_widget = QStackedWidget()

        # Socket.IO 클라이언트 생성 및 서버 연결
        self.sio = socketio.Client()
        try:
            self.sio.connect("http://192.168.0.45:2000")
            print("Socket.IO connected to server.")
        except Exception as e:
            print("Socket.IO connection failed:", e)

        @self.sio.on('desk_update')
        def on_desk_update(data):
            print("📡 Desk GUI received update from server:", data)
            self.current_led_brightness = data.get("light", self.current_led_brightness)
            self.current_monitor_height = data.get("monitor_height", self.current_monitor_height)
            self.current_monitor_angle = data.get("monitor_angle", self.current_monitor_angle)
            self.current_desk_height = data.get("desk_height", self.current_desk_height)

            self.led_control_screen.update_brightness(self.current_led_brightness)
            self.monitor_control_screen.data_label_up_down.setText(str(self.current_monitor_height))
            self.monitor_control_screen.data_label_front_back.setText(str(self.current_monitor_angle))
            self.desk_control_screen.data_value_label.setText(str(self.current_desk_height))
            # 서버 업데이트 시, 두 보드를 모두 갱신
            self.update_static_board()
            self.update_dynamic_board()

        # 초기 상태 변수
        self.current_led_brightness = 0
        self.current_monitor_height = 90   # 예시 초기값
        self.current_monitor_angle = 90    # 예시 초기값
        self.current_desk_height = 0

        # 시리얼 포트 (예시 포트 번호, 환경에 맞게 수정)
        self.serial_reader1 = SerialReader(port='/dev/ttyACM1', baudrate=115200, board_label="dynamic_board")
        self.serial_reader2 = SerialReader(port='/dev/ttyACM0', baudrate=9600, board_label="static_board")

        self.serial_reader1.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.rfidReceived.connect(self.handle_rfid_data)
        self.serial_reader2.rfidDataReceived.connect(self.handle_rfid_mode_data)

        self.serial_reader1.start()
        self.serial_reader2.start()

        self.main_screen = MainScreen(self.stacked_widget, serial_writer=self.serial_reader2)
        self.control_mode_screen = ControlModeScreen(self.stacked_widget)
        self.led_control_screen = LEDControlScreen(self.stacked_widget, serial_writer=self.serial_reader2, main_window=self)
        self.monitor_control_screen = MonitorControlScreen(self.stacked_widget, serial_writer=self.serial_reader1, main_window=self)
        self.desk_control_screen = DeskControlScreen(self.stacked_widget, serial_writer=self.serial_reader1, main_window=self)

        self.stacked_widget.addWidget(self.main_screen)             # index 0
        self.stacked_widget.addWidget(self.control_mode_screen)       # index 1
        self.stacked_widget.addWidget(self.led_control_screen)        # index 2
        self.stacked_widget.addWidget(self.monitor_control_screen)    # index 3
        self.stacked_widget.addWidget(self.desk_control_screen)       # index 4

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def send_data_to_server(self):
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "light": self.current_led_brightness,
            "monitor_height": self.current_monitor_height,
            "monitor_angle": self.current_monitor_angle,
            "desk_height": self.current_desk_height
        }
        if self.sio.connected:
            self.sio.emit('send_data', data)
            print("Sent data to server:", data)
        else:
            print("Socket.IO not connected. Could not send data.")

    def update_static_board(self):
        # 정적 보드: LED 밝기 업데이트 (헤더 0xFF)
        packet_led = struct.pack('BBBB', 0xFF, self.current_led_brightness, 0, 0)
        self.serial_reader2.write_command(packet_led)
        print("Static board updated: LED brightness =", self.current_led_brightness)

    def update_dynamic_board(self):
        # 동적 보드: 모니터 높이, 모니터 틸트, 책상 높이 업데이트 (헤더 0xFE)
        packet_dyn = struct.pack('BBBB', 0xFE, self.current_monitor_height, self.current_monitor_angle, self.current_desk_height)
        self.serial_reader1.write_command(packet_dyn)
        print("Dynamic board updated:",
              self.current_monitor_height,
              self.current_monitor_angle,
              self.current_desk_height)

    @pyqtSlot(str, int, int, int)
    def handle_serial_data(self, board, monitor_height, monitor_tilt, desk_height):
        if board == "dynamic_board":
            self.monitor_control_screen.data_label_up_down.setText(str(monitor_height))
            self.monitor_control_screen.data_label_front_back.setText(str(monitor_tilt))
            self.desk_control_screen.data_value_label.setText(str(desk_height))

            self.current_monitor_height = monitor_height
            self.current_monitor_angle = monitor_tilt
            self.current_desk_height = desk_height

            data_dict = {
                "board": board,
                "monitor_height": monitor_height,
                "monitor_angle": monitor_tilt,
                "desk_height": desk_height
            }
            print(json.dumps(data_dict, indent=4))
            self.send_data_to_server()
        elif board == "static_board":
            self.led_control_screen.update_brightness(monitor_height)
            self.current_led_brightness = monitor_height

            data_dict = {
                "board": board,
                "light": monitor_height
            }
            print(json.dumps(data_dict, indent=4))
            self.send_data_to_server()

    @pyqtSlot(str)
    def handle_rfid_data(self, uid):
        self.main_screen.label.setText(f"User ID : {uid}")
        print(json.dumps({"desk_gui": "RFID UID updated", "uid": uid}, indent=4))

    @pyqtSlot(str)
    def handle_rfid_mode_data(self, data_str):
        try:
            parts = data_str.split(',')
            mode = int(parts[0].split(':')[1].strip())
            brightness_val = int(parts[1].split(':')[1].strip())
            monitor_part = parts[2].split(':')[1].strip()  # "H/T"
            monitor_height, monitor_tilt = [int(x.strip()) for x in monitor_part.split('/')]
            desk_height_val = int(parts[3].split(':')[1].strip())
        except Exception as e:
            print("RFID 데이터 파싱 에러:", e)
            return

        self.led_control_screen.update_brightness(brightness_val)
        self.monitor_control_screen.data_label_up_down.setText(str(monitor_height))
        self.monitor_control_screen.data_label_front_back.setText(str(monitor_tilt))
        self.desk_control_screen.data_value_label.setText(str(desk_height_val))

        self.current_led_brightness = brightness_val
        self.current_monitor_height = monitor_height
        self.current_monitor_angle = monitor_tilt
        self.current_desk_height = desk_height_val

        led_packet = struct.pack('BB', 0xFF, brightness_val)
        self.serial_reader2.write_command(led_packet)
        print("Sent LED brightness command to static board:", led_packet)

        monitor_updown_packet = struct.pack('BB', 0xFB, monitor_height)
        self.serial_reader1.write_command(monitor_updown_packet)
        print("Sent monitor up/down command to dynamic board:", monitor_updown_packet)

        monitor_frontback_packet = struct.pack('BB', 0xFC, monitor_tilt)
        self.serial_reader1.write_command(monitor_frontback_packet)
        print("Sent monitor front/back command to dynamic board:", monitor_frontback_packet)

        current_text = self.main_screen.label.text()
        new_text = current_text + "\nMode: " + str(mode)
        self.main_screen.label.setText(new_text)
        print(json.dumps({"desk_gui": "RFID ModeData updated", "mode": mode}, indent=4))
        self.send_data_to_server()

# SerialReader: 시리얼 포트로부터 데이터 수신 및 명령 전송
class SerialReader(QThread):
    dataReceived = pyqtSignal(str, int, int, int)
    rfidReceived = pyqtSignal(str)
    rfidDataReceived = pyqtSignal(str)

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
                    header = self.ser.read(1)
                    if header == b'\xFF':
                        if self.board_label == "static_board":
                            data = self.ser.read(3)
                            if len(data) == 3:
                                led_brightness = data[0]
                                self.dataReceived.emit(self.board_label, led_brightness, 0, 0)
                        else:
                            data = self.ser.read(3)
                            if len(data) == 3:
                                monitor_height, monitor_tilt, desk_height = struct.unpack('BBB', data)
                                self.dataReceived.emit(self.board_label, monitor_height, monitor_tilt, desk_height)
                    elif header == b'\xFA':
                        uid_length_byte = self.ser.read(1)
                        if uid_length_byte:
                            uid_length = uid_length_byte[0]
                            uid_bytes = self.ser.read(uid_length)
                            if len(uid_bytes) == uid_length:
                                uid_str = uid_bytes.hex().upper()
                                self.rfidReceived.emit(uid_str)
                                print(json.dumps({"desk_gui": "RFID UID received", "uid": uid_str}, indent=4))
                    elif header == b'\xFB':
                        data_bytes = self.ser.read(5)
                        if len(data_bytes) == 5:
                            mode = data_bytes[0]
                            brightness = data_bytes[1]
                            monitor_height = data_bytes[2]
                            monitor_tilt = data_bytes[3]
                            desk_height = data_bytes[4]
                            data_str = f"Mode: {mode}, Brightness: {brightness}, Monitor: {monitor_height}/{monitor_tilt}, Desk: {desk_height}"
                            self.rfidDataReceived.emit(data_str)
                            print(json.dumps({"desk_gui": "RFID Data received", "data": data_str}, indent=4))
                    else:
                        pass
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
