import sys
import socket
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qt_material import apply_stylesheet  # pip install qt_material 설치

# ─────────────────────────────────────────
# QThread를 이용한 소켓 클라이언트 구현
# ─────────────────────────────────────────
class SocketClientThread(QThread):
    newMessage = pyqtSignal(dict)  # 수신한 JSON 메시지를 전달하는 시그널

    def __init__(self, host, port, parent=None):
        super().__init__(parent)
        self.host = '192.168.0.165'  # 서버 IP (적절하게 수정)
        self.port = 9898
        self.running = True
        self.sock = None

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
            print("서버에 연결되었습니다. (GUI 클라이언트)")
        except Exception as e:
            print("서버 연결 실패:", e)
            return

        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("서버가 연결을 종료했습니다.")
                    break
                message = data.decode('utf-8')
                print("서버에서 수신한 원본 메시지:", message)
                try:
                    json_message = json.loads(message)
                    print("서버에서 수신한 JSON 메시지:", json_message)
                    print("데이터 타입:", type(json_message))
                    self.newMessage.emit(json_message)
                except json.JSONDecodeError:
                    print("수신된 메시지 (문자열 처리):", message)
            except Exception as e:
                print("수신 오류:", e)
                break

        self.sock.close()

    def send_data(self, data):
        try:
            json_str = json.dumps(data, separators=(',', ':'))
            self.sock.sendall(json_str.encode('utf-8'))
            print("클라이언트: 서버에 전송:", json_str)
        except Exception as e:
            print("전송 오류:", e)

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.quit()
        self.wait()


# ─────────────────────────────────────────
# ControlDialog (Control Mode)
# ─────────────────────────────────────────
class ControlDialog(QDialog):
    def __init__(self, current_values, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control Mode")
        self.setFixedSize(600, 400)
        self.current_values = current_values.copy()

        layout = QVBoxLayout()

        # LED 설정
        led_layout = QHBoxLayout()
        self.label_r_title = QLabel("led_r:")
        self.label_r_title.setStyleSheet("font-size: 18pt;")
        self.label_g_title = QLabel("led_g:")
        self.label_g_title.setStyleSheet("font-size: 18pt;")
        self.label_b_title = QLabel("led_b:")
        self.label_b_title.setStyleSheet("font-size: 18pt;")

        self.spin_r = QSpinBox()
        self.spin_r.setStyleSheet("font-size: 18pt;")
        self.spin_g = QSpinBox()
        self.spin_g.setStyleSheet("font-size: 18pt;")
        self.spin_b = QSpinBox()
        self.spin_b.setStyleSheet("font-size: 18pt;")
        self.spin_r.setRange(0, 255)
        self.spin_g.setRange(0, 255)
        self.spin_b.setRange(0, 255)
        self.spin_r.setValue(self.current_values["led_r"])
        self.spin_g.setValue(self.current_values["led_g"])
        self.spin_b.setValue(self.current_values["led_b"])

        led_layout.addWidget(self.label_r_title)
        led_layout.addWidget(self.spin_r)
        led_layout.addWidget(self.label_g_title)
        led_layout.addWidget(self.spin_g)
        led_layout.addWidget(self.label_b_title)
        led_layout.addWidget(self.spin_b)

        # Servo 설정
        servo_layout = QHBoxLayout()
        self.label_servo1_title = QLabel("servo_1:")
        self.label_servo1_title.setStyleSheet("font-size: 18pt;")
        self.label_servo2_title = QLabel("servo_2:")
        self.label_servo2_title.setStyleSheet("font-size: 18pt;")

        self.spin_servo1 = QSpinBox()
        self.spin_servo1.setStyleSheet("font-size: 18pt;")
        self.spin_servo2 = QSpinBox()
        self.spin_servo2.setStyleSheet("font-size: 18pt;")
        self.spin_servo1.setRange(0, 180)
        self.spin_servo2.setRange(0, 180)
        self.spin_servo1.setValue(self.current_values["servo_1"])
        self.spin_servo2.setValue(self.current_values["servo_2"])

        servo_layout.addWidget(self.label_servo1_title)
        servo_layout.addWidget(self.spin_servo1)
        servo_layout.addWidget(self.label_servo2_title)
        servo_layout.addWidget(self.spin_servo2)

        # LinearActuator 설정
        actuator_layout = QHBoxLayout()
        self.label_actuator_title = QLabel("LinearActuator:")
        self.label_actuator_title.setStyleSheet("font-size: 18pt;")
        self.spin_actuator = QSpinBox()
        self.spin_actuator.setStyleSheet("font-size: 18pt;")
        self.spin_actuator.setRange(0, 1000)
        self.spin_actuator.setValue(self.current_values["LinearActuator"])
        actuator_layout.addWidget(self.label_actuator_title)
        actuator_layout.addWidget(self.spin_actuator)

        layout.addLayout(led_layout)
        layout.addLayout(servo_layout)
        layout.addLayout(actuator_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("font-size: 18pt;")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_values(self):
        return {
            "led_r": self.spin_r.value(),
            "led_g": self.spin_g.value(),
            "led_b": self.spin_b.value(),
            "servo_1": self.spin_servo1.value(),
            "servo_2": self.spin_servo2.value(),
            "LinearActuator": self.spin_actuator.value()
        }


# ─────────────────────────────────────────
# SaveInModeDialog (Save in Mode)
# ─────────────────────────────────────────
class SaveInModeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save in Mode")
        self.setFixedSize(600, 400)
        layout = QVBoxLayout()

        self.radio_group = QButtonGroup(self)

        self.radio_mode1 = QRadioButton("Mode 1")
        self.radio_mode1.setStyleSheet("font-size: 18pt;")
        self.radio_mode2 = QRadioButton("Mode 2")
        self.radio_mode2.setStyleSheet("font-size: 18pt;")
        self.radio_mode3 = QRadioButton("Mode 3")
        self.radio_mode3.setStyleSheet("font-size: 18pt;")

        self.radio_mode1.setChecked(True)
        self.radio_group.addButton(self.radio_mode1, 1)
        self.radio_group.addButton(self.radio_mode2, 2)
        self.radio_group.addButton(self.radio_mode3, 3)

        layout.addWidget(self.radio_mode1)
        layout.addWidget(self.radio_mode2)
        layout.addWidget(self.radio_mode3)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("font-size: 18pt;")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected_mode(self):
        return self.radio_group.checkedId()


# ─────────────────────────────────────────
# LogDataWindow (로그 테이블 화면)
# ─────────────────────────────────────────
class LogDataWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        self.setWindowTitle("Log Data")
        self.setFixedSize(1280, 720)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        top_layout = QHBoxLayout()
        self.label_ergodesk = QLabel("ERGODESK")
        self.label_ergodesk.setStyleSheet("font-size: 18pt; font-weight: bold;")
        self.label_user_id = QLabel("User ID : None")
        self.label_user_id.setStyleSheet("font-size: 18pt;")
        self.label_log_data = QLabel("Log Data")
        self.label_log_data.setStyleSheet("font-size: 18pt;")
        top_layout.addWidget(self.label_ergodesk)
        top_layout.addWidget(self.label_user_id)
        top_layout.addWidget(self.label_log_data)
        main_layout.addLayout(top_layout)
        
        self.table = QTableWidget()
        self.table.setStyleSheet("font-size: 18pt;")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Log ID", "Time Stamp", "Request ID", "Target", "Action", "Value", "Status"
        ])
        self.table.setRowCount(2)
        self.table.setItem(0, 0, QTableWidgetItem("lg01"))
        self.table.setItem(0, 1, QTableWidgetItem("2025-02-14 10:37:30"))
        self.table.setItem(0, 2, QTableWidgetItem("desk_gui"))
        self.table.setItem(0, 3, QTableWidgetItem("servo_1"))
        self.table.setItem(0, 4, QTableWidgetItem("tilt"))
        self.table.setItem(0, 5, QTableWidgetItem("30"))
        self.table.setItem(0, 6, QTableWidgetItem("success"))
        self.table.setItem(1, 0, QTableWidgetItem("lg02"))
        self.table.setItem(1, 1, QTableWidgetItem("2025-02-16 13:37:30"))
        self.table.setItem(1, 2, QTableWidgetItem("desk_gui"))
        self.table.setItem(1, 3, QTableWidgetItem("led_r"))
        self.table.setItem(1, 4, QTableWidgetItem("on"))
        self.table.setItem(1, 5, QTableWidgetItem("255"))
        self.table.setItem(1, 6, QTableWidgetItem("success"))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)
        
        self.btn_back = QPushButton("Back")
        self.btn_back.setStyleSheet("font-size: 18pt;")
        self.btn_back.setFixedSize(140, 100)
        self.btn_back.clicked.connect(self.go_back)
        main_layout.addWidget(self.btn_back, alignment=Qt.AlignRight)
        
    def go_back(self):
        self.main_window.show()
        self.close()


# ─────────────────────────────────────────
# 메인 윈도우
# ─────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ErgoDesk GUI")
        self.setFixedSize(1280, 720)

        self.currentValues = {
            "led_r": 0,
            "led_g": 0,
            "led_b": 0,
            "servo_1": 90,
            "servo_2": 90,
            "LinearActuator": 0
        }

        self.modes = {
            1: {"led_r": 10, "led_g": 10, "led_b": 10, "servo_1": 90, "servo_2": 90, "LinearActuator": 100},
            2: {"led_r": 50, "led_g": 0, "led_b": 0, "servo_1": 45, "servo_2": 135, "LinearActuator": 200},
            3: {"led_r": 0, "led_g": 50, "led_b": 100, "servo_1": 120, "servo_2": 60, "LinearActuator": 300},
        }

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 상단 레이아웃
        top_layout = QHBoxLayout()
        self.label_ergodesk = QLabel("ERGODESK")
        self.label_ergodesk.setStyleSheet("font-size: 18pt; font-weight: bold;")
        self.label_user_id = QLabel("User ID : None")
        self.label_user_id.setStyleSheet("font-size: 18pt;")
        self.btn_log_data = QPushButton("Log Data")
        self.btn_log_data.setStyleSheet("font-size: 18pt;")
        top_layout.addWidget(self.label_ergodesk)
        top_layout.addWidget(self.label_user_id)
        top_layout.addWidget(self.btn_log_data)
        main_layout.addLayout(top_layout)

        # 중단 레이아웃 (좌측: 버튼, 우측: 값 표시)
        middle_layout = QHBoxLayout()
        main_layout.addLayout(middle_layout)

        # 좌측 버튼 레이아웃
        left_layout = QVBoxLayout()
        self.btn_mode1 = QPushButton("Mode 1")
        self.btn_mode1.setStyleSheet("font-size: 18pt;")
        self.btn_mode1.setFixedSize(200,100)
        self.btn_mode2 = QPushButton("Mode 2")
        self.btn_mode2.setStyleSheet("font-size: 18pt;")
        self.btn_mode2.setFixedSize(200,100)
        self.btn_mode3 = QPushButton("Mode 3")
        self.btn_mode3.setStyleSheet("font-size: 18pt;")
        self.btn_mode3.setFixedSize(200,100)
        self.btn_control = QPushButton("Control Mode")
        self.btn_control.setStyleSheet("font-size: 18pt;")
        self.btn_control.setFixedSize(200,100)
        left_layout.addWidget(self.btn_mode1)
        left_layout.addWidget(self.btn_mode2)
        left_layout.addWidget(self.btn_mode3)
        left_layout.addWidget(self.btn_control)
        middle_layout.addLayout(left_layout)

        # 우측 값 표시 레이아웃
        right_layout = QGridLayout()
        middle_layout.addLayout(right_layout)

        # LED 값 표시
        self.label_led_title = QLabel("LED")
        self.label_led_title.setStyleSheet("font-size: 18pt;")
        self.label_led_r = QLabel(f"led_r: {self.currentValues['led_r']}")
        self.label_led_r.setStyleSheet("font-size: 18pt;")
        self.label_led_g = QLabel(f"led_g: {self.currentValues['led_g']}")
        self.label_led_g.setStyleSheet("font-size: 18pt;")
        self.label_led_b = QLabel(f"led_b: {self.currentValues['led_b']}")
        self.label_led_b.setStyleSheet("font-size: 18pt;")
        right_layout.addWidget(self.label_led_title, 0, 0)
        right_layout.addWidget(self.label_led_r, 0, 1)
        right_layout.addWidget(self.label_led_g, 0, 2)
        right_layout.addWidget(self.label_led_b, 0, 3)

        # Servo 값 표시
        self.label_servo_title = QLabel("Servo")
        self.label_servo_title.setStyleSheet("font-size: 18pt;")
        self.label_servo_1 = QLabel(f"servo_1: {self.currentValues['servo_1']}")
        self.label_servo_1.setStyleSheet("font-size: 18pt;")
        self.label_servo_2 = QLabel(f"servo_2: {self.currentValues['servo_2']}")
        self.label_servo_2.setStyleSheet("font-size: 18pt;")
        right_layout.addWidget(self.label_servo_title, 1, 0)
        right_layout.addWidget(self.label_servo_1, 1, 1)
        right_layout.addWidget(self.label_servo_2, 1, 2)

        # LinearActuator 값 표시
        self.label_actuator_title = QLabel("LinearActuator")
        self.label_actuator_title.setStyleSheet("font-size: 18pt;")
        self.label_actuator = QLabel(f"{self.currentValues['LinearActuator']}")
        self.label_actuator.setStyleSheet("font-size: 18pt;")
        right_layout.addWidget(self.label_actuator_title, 2, 0)
        right_layout.addWidget(self.label_actuator, 2, 1)

        # 하단: Save in Mode 버튼과 로그 출력 레이아웃
        save_log_layout = QHBoxLayout()
        self.btn_save_in_mode = QPushButton("Save in Mode")
        self.btn_save_in_mode.setStyleSheet("font-size: 18pt;")
        self.btn_save_in_mode.setFixedSize(200,80)
        self.log_label = QLabel("")
        self.log_label.setStyleSheet("font-size: 18pt; color: white; background-color: #444444;")
        self.log_label.setFixedHeight(80)
        self.log_label.setAlignment(Qt.AlignCenter)
        save_log_layout.addWidget(self.btn_save_in_mode)
        save_log_layout.addWidget(self.log_label)
        main_layout.addLayout(save_log_layout)

        # 버튼 시그널 연결
        self.btn_mode1.clicked.connect(self.load_mode1)
        self.btn_mode2.clicked.connect(self.load_mode2)
        self.btn_mode3.clicked.connect(self.load_mode3)
        self.btn_control.clicked.connect(self.enter_control_mode)
        self.btn_save_in_mode.clicked.connect(self.go_save_in_mode_page)
        self.btn_log_data.clicked.connect(self.show_log_data_window)

        # 서버로부터 값을 수신하는 소켓 클라이언트 스레드 시작
        self.client_thread = SocketClientThread('192.168.0.45', 1234)
        self.client_thread.newMessage.connect(self.handle_new_message)
        self.client_thread.start()

    def log_message(self, message):
        self.log_label.setText(message)

    def update_labels(self):
        self.label_led_r.setText(f"led_r: {self.currentValues['led_r']}")
        self.label_led_g.setText(f"led_g: {self.currentValues['led_g']}")
        self.label_led_b.setText(f"led_b: {self.currentValues['led_b']}")
        self.label_servo_1.setText(f"servo_1: {self.currentValues['servo_1']}")
        self.label_servo_2.setText(f"servo_2: {self.currentValues['servo_2']}")
        self.label_actuator.setText(f"{self.currentValues['LinearActuator']}")

    def load_mode1(self):
        self.currentValues = self.modes[1].copy()
        self.update_labels()
        self.send_current_values()
        self.log_message("Mode 1 loaded.")

    def load_mode2(self):
        self.currentValues = self.modes[2].copy()
        self.update_labels()
        self.send_current_values()
        self.log_message("Mode 2 loaded.")

    def load_mode3(self):
        self.currentValues = self.modes[3].copy()
        self.update_labels()
        self.send_current_values()
        self.log_message("Mode 3 loaded.")

    def enter_control_mode(self):
        dlg = ControlDialog(self.currentValues, self)
        if dlg.exec_() == QDialog.Accepted:
            self.currentValues = dlg.get_values()
            self.update_labels()
            self.send_current_values()
            self.log_message("Control mode updated.")

    def go_save_in_mode_page(self):
        dlg = SaveInModeDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            selected_mode = dlg.get_selected_mode()
            if selected_mode in self.modes:
                self.modes[selected_mode] = self.currentValues.copy()
                self.log_message(f"현재 설정을 Mode {selected_mode}에 저장했습니다.")

    def show_log_data_window(self):
        self.log_window = LogDataWindow(self)
        self.log_window.show()
        self.hide()

    def send_current_values(self):
        data = {
            "led_r": self.currentValues["led_r"],
            "led_g": self.currentValues["led_g"],
            "led_b": self.currentValues["led_b"],
            "servo_1": self.currentValues["servo_1"],
            "servo_2": self.currentValues["servo_2"],
            "LinearActuator": self.currentValues["LinearActuator"]
        }
        self.client_thread.send_data(data)

    def handle_new_message(self, msg):
        print("GUI에서 수신한 메시지:", msg)
        if "led_r" in msg:
            self.currentValues["led_r"] = msg["led_r"]
        if "led_g" in msg:
            self.currentValues["led_g"] = msg["led_g"]
        if "led_b" in msg:
            self.currentValues["led_b"] = msg["led_b"]
        if "servo_1" in msg:
            self.currentValues["servo_1"] = msg["servo_1"]
        if "servo_2" in msg:
            self.currentValues["servo_2"] = msg["servo_2"]
        if "LinearActuator" in msg:
            self.currentValues["LinearActuator"] = msg["LinearActuator"]
        self.update_labels()

    def closeEvent(self, event):
        self.client_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())