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
                # RFID 읽기 명령을 전송하는 슬롯 연결 (해당 블록 번호 사용)
                btn.clicked.connect(lambda _, b=block: self.send_rfid_read_command(b))
            else:
                # Control Mode는 화면 전환
                btn.clicked.connect(lambda _, i=1: self.stacked_widget.setCurrentIndex(i))
            grid_layout.addWidget(btn, *pos)
        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def send_rfid_read_command(self, block):
        # RFID 읽기 명령: 헤더 0xFD, 기능코드 0x04 (읽기), 블록번호 (4,5,6 중 하나)
        packet = struct.pack('BBB', 0xFD, 0x04, block)
        self.serial_writer.write_command(packet)
        print(f"RFID Read 명령 전송: {packet} (블록 {block})")

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
            print(json.dumps({"desk_gui": "LED up clicked", "led_brightness": self.data_value}, indent=4))

    def decrease_data(self):
        if self.data_value > 0:
            self.data_value -= 1
            self.data_label.setText(str(self.data_value))
            packet = struct.pack('BB', 0xFF, self.data_value)
            self.serial_writer.write_command(packet)
            print(json.dumps({"desk_gui": "LED down clicked", "led_brightness": self.data_value}, indent=4))

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
        self.serial_reader2 = SerialReader(port='/dev/ttyACM0', baudrate=9600, board_label="static_board")

        self.serial_reader1.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.rfidReceived.connect(self.handle_rfid_data)
        self.serial_reader2.rfidDataReceived.connect(self.handle_rfid_mode_data)

        self.serial_reader1.start()
        self.serial_reader2.start()

        # MainScreen에 serial_reader2 (static_board)를 전달
        self.main_screen = MainScreen(self.stacked_widget, serial_writer=self.serial_reader2)
        self.control_mode_screen = ControlModeScreen(self.stacked_widget)
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
            self.led_control_screen.update_brightness(monitor_height)
            data_dict = {
                "board": board,
                "led_brightness": monitor_height
            }
            print(json.dumps(data_dict, indent=4))

    @pyqtSlot(str)
    def handle_rfid_data(self, uid):
        self.main_screen.label.setText(f"User ID : {uid}")
        print(json.dumps({"desk_gui": "RFID UID updated", "uid": uid}, indent=4))

    @pyqtSlot(str)
    def handle_rfid_mode_data(self, data_str):
        # Expected RFID ModeData string format:
        # "Mode: X, Brightness: Y, Monitor: H/T, Desk: Z"
        try:
            parts = data_str.split(',')
            mode = int(parts[0].split(':')[1].strip())
            brightness_val = int(parts[1].split(':')[1].strip())
            monitor_part = parts[2].split(':')[1].strip()  # Expected format "H/T"
            monitor_height, monitor_tilt = [int(x.strip()) for x in monitor_part.split('/')]
            desk_height_val = int(parts[3].split(':')[1].strip())
            print("data read")
        except Exception as e:
            print("RFID 데이터 파싱 에러:", e)
            return

        # Update the GUI with the new values
        self.led_control_screen.update_brightness(brightness_val)
        self.monitor_control_screen.data_label_up_down.setText(str(monitor_height))
        self.monitor_control_screen.data_label_front_back.setText(str(monitor_tilt))
        self.desk_control_screen.data_value_label.setText(str(desk_height_val))

        # --- Send control data separately ---
        # 1. Send LED brightness command to the static board.
        #    Using header 0xFF with brightness value.
        led_packet = struct.pack('BB', 0xFF, brightness_val)
        self.serial_reader2.write_command(led_packet)
        print("Sent LED brightness command to static board:", led_packet)
        
        # 2. Send monitor up/down command to the dynamic board.
        #    Using header 0xFB and the monitor height value.
        monitor_updown_packet = struct.pack('BB', 0xFB, monitor_height)
        self.serial_reader1.write_command(monitor_updown_packet)
        print("Sent monitor up/down command to dynamic board:", monitor_updown_packet)
        
        # 3. Send monitor front/back command to the dynamic board.
        #    Using header 0xFC and the monitor tilt value.
        monitor_frontback_packet = struct.pack('BB', 0xFC, monitor_tilt)
        self.serial_reader1.write_command(monitor_frontback_packet)
        print("Sent monitor front/back command to dynamic board:", monitor_frontback_packet)
        
        # # 4. Send desk control command to the dynamic board.
        # #    Using header 0xFD and the desk height value.
        # desk_packet = struct.pack('BB', 0xFD, desk_height_val)
        # self.serial_reader1.write_command(desk_packet)
        # print("Sent desk control command to dynamic board:", desk_packet)
        
        # For debugging or visual feedback, append just the mode value to the main GUI label.
        current_text = self.main_screen.label.text()
        new_text = current_text + "\nMode: " + str(mode)
        self.main_screen.label.setText(new_text)
        print(json.dumps({"desk_gui": "RFID ModeData updated", "mode": mode}, indent=4))



# ----------------------------
# 시리얼 리더 (QThread 사용, 쓰기 기능 포함)
# ----------------------------
class SerialReader(QThread):
    dataReceived = pyqtSignal(str, int, int, int)  # board, monitor_height, monitor_tilt, desk_height
    rfidReceived = pyqtSignal(str)  # RFID UID를 문자열로 전달
    rfidDataReceived = pyqtSignal(str)  # RFID 내부 데이터(ModeData)를 문자열로 전달

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
                        # LED 제어나 동적 보드 데이터 처리
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
                        # RFID UID 패킷 처리
                        uid_length_byte = self.ser.read(1)
                        if uid_length_byte:
                            uid_length = uid_length_byte[0]
                            uid_bytes = self.ser.read(uid_length)
                            if len(uid_bytes) == uid_length:
                                uid_str = uid_bytes.hex().upper()
                                self.rfidReceived.emit(uid_str)
                                print(json.dumps({"desk_gui": "RFID UID received", "uid": uid_str}, indent=4))
                    elif header == b'\xFB':
                        # RFID 내부 데이터 패킷 처리 (5바이트: ModeData)
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
                        # 알 수 없는 헤더는 무시
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

# ----------------------------
# 메인 실행
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
