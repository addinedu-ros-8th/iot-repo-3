# desk_gui.py

import sys
import serial
import struct
import json
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime

# Socket.IO 클라이언트 라이브러리
import socketio


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
    def __init__(self, stacked_widget, serial_writer, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer  # static_board에 명령 전송

        # MainWindow 참조 (현재 상태 갱신 + 서버 전송용)
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
            print(json.dumps({"desk_gui": "LED up clicked", "led_brightness": self.data_value}, indent=4))

            # MainWindow에 LED 밝기 반영 후 서버로 전송
            self.main_window.current_led_brightness = self.data_value
            self.main_window.send_data_to_server()

    def decrease_data(self):
        if self.data_value > 0:
            self.data_value -= 1
            self.data_label.setText(str(self.data_value))
            packet = struct.pack('BB', 0xFF, self.data_value)
            self.serial_writer.write_command(packet)
            print(json.dumps({"desk_gui": "LED down clicked", "led_brightness": self.data_value}, indent=4))

            # MainWindow에 LED 밝기 반영 후 서버로 전송
            self.main_window.current_led_brightness = self.data_value
            self.main_window.send_data_to_server()

    def update_brightness(self, value):
        self.data_value = value
        self.data_label.setText(str(value))


class DeskControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer

        # MainWindow 참조
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
        # 1) 동적 보드로 명령 전송
        packet = struct.pack('BB', 0xFD, 0)
        self.serial_writer.write_command(packet)

        # 2) GUI 측 값도 +1 (임시) 반영 후 서버 전송
        self.main_window.current_desk_height += 1
        self.data_value_label.setText(str(self.main_window.current_desk_height))
        self.main_window.send_data_to_server()

    def send_down_command(self):
        # 1) 동적 보드로 명령 전송
        packet = struct.pack('BB', 0xFD, 1)
        self.serial_writer.write_command(packet)

        # 2) GUI 측 값도 -1 (임시) 반영 후 서버 전송
        if self.main_window.current_desk_height > 0:
            self.main_window.current_desk_height -= 1
        self.data_value_label.setText(str(self.main_window.current_desk_height))
        self.main_window.send_data_to_server()


class MonitorControlScreen(QWidget):
    def __init__(self, stacked_widget, serial_writer, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_writer = serial_writer

        # MainWindow 참조
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

        # 초기 텍스트
        self.data_label_front_back.setText(str(self.main_window.current_monitor_angle))
        self.data_label_up_down.setText(str(self.main_window.current_monitor_height))

    def send_front_command(self):
        # 1) 동적 보드로 명령 전송
        # 여기서는 "monitor tilt = 1" 이라는 예시
        # 실제로는 monitor_angle을 +1 하는 식으로 구현할 수도 있음
        new_angle = self.main_window.current_monitor_angle + 1
        if new_angle > 255:
            new_angle = 255

        packet = struct.pack('BB', 0xFC, new_angle)
        self.serial_writer.write_command(packet)

        # 2) GUI 측 값도 업데이트 후 서버 전송
        self.main_window.current_monitor_angle = new_angle
        self.data_label_front_back.setText(str(new_angle))
        self.main_window.send_data_to_server()

    def send_back_command(self):
        # monitor tilt -= 1
        new_angle = max(0, self.main_window.current_monitor_angle - 1)
        packet = struct.pack('BB', 0xFC, new_angle)
        self.serial_writer.write_command(packet)

        self.main_window.current_monitor_angle = new_angle
        self.data_label_front_back.setText(str(new_angle))
        self.main_window.send_data_to_server()

    def send_up_command(self):
        # monitor height += 1
        new_height = self.main_window.current_monitor_height + 1
        if new_height > 255:
            new_height = 255
        packet = struct.pack('BB', 0xFB, new_height)
        self.serial_writer.write_command(packet)

        self.main_window.current_monitor_height = new_height
        self.data_label_up_down.setText(str(new_height))
        self.main_window.send_data_to_server()

    def send_down_command(self):
        # monitor height -= 1
        new_height = max(0, self.main_window.current_monitor_height - 1)
        packet = struct.pack('BB', 0xFB, new_height)
        self.serial_writer.write_command(packet)

        self.main_window.current_monitor_height = new_height
        self.data_label_up_down.setText(str(new_height))
        self.main_window.send_data_to_server()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt GUI Example")
        self.setFixedSize(320, 480)
        self.stacked_widget = QStackedWidget()

        # Socket.IO 클라이언트 생성 및 서버 연결
        self.sio = socketio.Client()
        try:
            self.sio.connect("http://192.168.0.30:5007")
            print("Socket.IO connected to server.")
        except Exception as e:
            print("Socket.IO connection failed:", e)

        # 현재 상태값 저장용 변수 (서버로 보낼 값)
        self.current_led_brightness = 0
        self.current_monitor_height = 0
        self.current_monitor_angle = 0
        self.current_desk_height = 0

        # 동적 보드와 정적 보드의 시리얼 리더 생성
        self.serial_reader1 = SerialReader(port='/dev/ttyACM2', baudrate=115200, board_label="dynamic_board")
        self.serial_reader2 = SerialReader(port='/dev/ttyACM1', baudrate=9600, board_label="static_board")

        self.serial_reader1.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.dataReceived.connect(self.handle_serial_data)
        self.serial_reader2.rfidReceived.connect(self.handle_rfid_data)
        self.serial_reader2.rfidDataReceived.connect(self.handle_rfid_mode_data)

        self.serial_reader1.start()
        self.serial_reader2.start()

        # MainScreen에 serial_reader2 (static_board)를 전달
        self.main_screen = MainScreen(self.stacked_widget, serial_writer=self.serial_reader2)
        self.control_mode_screen = ControlModeScreen(self.stacked_widget)

        # LED / Monitor / Desk 컨트롤 화면에 MainWindow 참조를 넘겨준다
        self.led_control_screen = LEDControlScreen(self.stacked_widget, serial_writer=self.serial_reader2, main_window=self)
        self.monitor_control_screen = MonitorControlScreen(self.stacked_widget, serial_writer=self.serial_reader1, main_window=self)
        self.desk_control_screen = DeskControlScreen(self.stacked_widget, serial_writer=self.serial_reader1, main_window=self)

        self.stacked_widget.addWidget(self.main_screen)             # index 0
        self.stacked_widget.addWidget(self.control_mode_screen)     # index 1
        self.stacked_widget.addWidget(self.led_control_screen)      # index 2
        self.stacked_widget.addWidget(self.monitor_control_screen)  # index 3
        self.stacked_widget.addWidget(self.desk_control_screen)     # index 4

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def send_data_to_server(self):
        """현재 상태를 서버로 전송하는 메서드"""
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

    @pyqtSlot(str, int, int, int)
    def handle_serial_data(self, board, monitor_height, monitor_tilt, desk_height):
        """
        시리얼로부터 0xFF 헤더 데이터를 수신하면 호출됨.
        - dynamic_board: 3바이트(monitor_height, monitor_tilt, desk_height)
        - static_board: 1바이트(led_brightness)로 처리
        """
        if board == "dynamic_board":
            self.monitor_control_screen.data_label_up_down.setText(str(monitor_height))
            self.monitor_control_screen.data_label_front_back.setText(str(monitor_tilt))
            self.desk_control_screen.data_value_label.setText(str(desk_height))

            # MainWindow 내부 상태 갱신
            self.current_monitor_height = monitor_height
            self.current_monitor_angle = monitor_tilt
            self.current_desk_height = desk_height

            data_dict = {
                "board": board,
                "monitor_height": monitor_height,
                "monitor_tilt": monitor_tilt,
                "desk_height": desk_height
            }
            print(json.dumps(data_dict, indent=4))
            # 서버로 전송
            self.send_data_to_server()

        elif board == "static_board":
            # LED 밝기 정보 수신 -> LEDControlScreen 업데이트
            self.led_control_screen.update_brightness(monitor_height)
            self.current_led_brightness = monitor_height

            data_dict = {
                "board": board,
                "led_brightness": monitor_height
            }
            print(json.dumps(data_dict, indent=4))
            # 서버로 전송
            self.send_data_to_server()

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
            monitor_part = parts[2].split(':')[1].strip()  # "H/T"
            monitor_height, monitor_tilt = [int(x.strip()) for x in monitor_part.split('/')]
            desk_height_val = int(parts[3].split(':')[1].strip())
        except Exception as e:
            print("RFID 데이터 파싱 에러:", e)
            return

        # Update the GUI with the new values
        self.led_control_screen.update_brightness(brightness_val)
        self.monitor_control_screen.data_label_up_down.setText(str(monitor_height))
        self.monitor_control_screen.data_label_front_back.setText(str(monitor_tilt))
        self.desk_control_screen.data_value_label.setText(str(desk_height_val))

        # MainWindow 내부 상태 갱신
        self.current_led_brightness = brightness_val
        self.current_monitor_height = monitor_height
        self.current_monitor_angle = monitor_tilt
        self.current_desk_height = desk_height_val

        # 하드웨어로도 다시 전송
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

        # 서버로 전송
        self.send_data_to_server()


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
                        # LED or dynamic board data
                        if self.board_label == "static_board":
                            # static_board → LED 밝기 1바이트 + (테스트용) 2바이트 더?
                            data = self.ser.read(3)
                            if len(data) == 3:
                                led_brightness = data[0]
                                self.dataReceived.emit(self.board_label, led_brightness, 0, 0)
                        else:
                            # dynamic_board → 3바이트 (monitor_height, monitor_tilt, desk_height)
                            data = self.ser.read(3)
                            if len(data) == 3:
                                monitor_height, monitor_tilt, desk_height = struct.unpack('BBB', data)
                                self.dataReceived.emit(self.board_label, monitor_height, monitor_tilt, desk_height)
                    elif header == b'\xFA':
                        # RFID UID 패킷
                        uid_length_byte = self.ser.read(1)
                        if uid_length_byte:
                            uid_length = uid_length_byte[0]
                            uid_bytes = self.ser.read(uid_length)
                            if len(uid_bytes) == uid_length:
                                uid_str = uid_bytes.hex().upper()
                                self.rfidReceived.emit(uid_str)
                                print(json.dumps({"desk_gui": "RFID UID received", "uid": uid_str}, indent=4))
                    elif header == b'\xFB':
                        # RFID 내부 데이터 패킷 (5바이트: ModeData)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

