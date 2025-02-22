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
        self.host = '192.168.0.45'
        self.port = 8978
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
                try:
                    json_message = json.loads(message)
                    # 수신된 JSON 데이터를 시그널로 전달
                    self.newMessage.emit(json_message)
                except json.JSONDecodeError:
                    print("수신된 메시지 (문자열):", message)
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
        self.current_values = current_values.copy()  # 현재값 복사해서 로컬에서 수정

        layout = QVBoxLayout()

        # LED 설정
        led_layout = QHBoxLayout()
        self.label_r_title = QLabel("R:")
        self.label_r_title.setStyleSheet("font-size: 18pt;")
        self.label_g_title = QLabel("G:")
        self.label_g_title.setStyleSheet("font-size: 18pt;")
        self.label_b_title = QLabel("B:")
        self.label_b_title.setStyleSheet("font-size: 18pt;")

        self.spin_r = QSpinBox()
        self.spin_r.setStyleSheet("font-size: 18pt;")
        self.spin_g = QSpinBox()
        self.spin_g.setStyleSheet("font-size: 18pt;")
        self.spin_b = QSpinBox()
        self.spin_b.setStyleSheet("font-size: 18pt;")
        self.spin_r.setRange(0, 8)
        self.spin_g.setRange(0, 8)
        self.spin_b.setRange(0, 8)
        self.spin_r.setValue(self.current_values["R"])
        self.spin_g.setValue(self.current_values["G"])
        self.spin_b.setValue(self.current_values["B"])

        led_layout.addWidget(self.label_r_title)
        led_layout.addWidget(self.spin_r)
        led_layout.addWidget(self.label_g_title)
        led_layout.addWidget(self.spin_g)
        led_layout.addWidget(self.label_b_title)
        led_layout.addWidget(self.spin_b)

        # Desk 설정
        desk_layout = QHBoxLayout()
        self.label_desk_title = QLabel("Desk Height:")
        self.label_desk_title.setStyleSheet("font-size: 18pt;")
        self.spin_desk_height = QSpinBox()
        self.spin_desk_height.setStyleSheet("font-size: 18pt;")
        self.spin_desk_height.setRange(0, 50)
        self.spin_desk_height.setValue(self.current_values["DeskHeight"])
        desk_layout.addWidget(self.label_desk_title)
        desk_layout.addWidget(self.spin_desk_height)

        # Monitor 설정
        monitor_layout = QHBoxLayout()
        self.label_monitor_height_title = QLabel("Monitor Height:")
        self.label_monitor_height_title.setStyleSheet("font-size: 18pt;")
        self.spin_monitor_height = QSpinBox()
        self.spin_monitor_height.setStyleSheet("font-size: 18pt;")
        self.spin_monitor_height.setRange(0, 90)
        self.spin_monitor_height.setValue(self.current_values["MonitorHeight"])

        self.label_monitor_angle_title = QLabel("Angle:")
        self.label_monitor_angle_title.setStyleSheet("font-size: 18pt;")
        self.spin_monitor_angle = QSpinBox()
        self.spin_monitor_angle.setStyleSheet("font-size: 18pt;")
        self.spin_monitor_angle.setRange(0, 90)
        self.spin_monitor_angle.setValue(self.current_values["MonitorAngle"])

        monitor_layout.addWidget(self.label_monitor_height_title)
        monitor_layout.addWidget(self.spin_monitor_height)
        monitor_layout.addWidget(self.label_monitor_angle_title)
        monitor_layout.addWidget(self.spin_monitor_angle)

        layout.addLayout(led_layout)
        layout.addLayout(desk_layout)
        layout.addLayout(monitor_layout)

        # 버튼(OK/Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("font-size: 18pt;")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_values(self):
        return {
            "R": self.spin_r.value(),
            "G": self.spin_g.value(),
            "B": self.spin_b.value(),
            "DeskHeight": self.spin_desk_height.value(),
            "MonitorHeight": self.spin_monitor_height.value(),
            "MonitorAngle": self.spin_monitor_angle.value()
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
    """
    Log Data 창: 로그 테이블을 보여주고, Back 버튼으로 메인화면으로 돌아갑니다.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # 돌아갈 때 메인 윈도우를 다시 보여주기 위해 참조
        
        self.setWindowTitle("Log Data")
        self.setFixedSize(1280, 720)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 상단 레이아웃: ERGODESK / User ID : None / Log Data
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
        
        # 테이블 위젯
        self.table = QTableWidget()
        self.table.setStyleSheet("font-size: 18pt;")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Log ID", "Time Stamp", "Request ID", "Target", "Action", "Value", "Status"
        ])
        
        # 예시 데이터 2행
        self.table.setRowCount(2)
        self.table.setItem(0, 0, QTableWidgetItem("lg01"))
        self.table.setItem(0, 1, QTableWidgetItem("2025-02-14 10:37:30"))
        self.table.setItem(0, 2, QTableWidgetItem("desk_gui"))
        self.table.setItem(0, 3, QTableWidgetItem("servo1"))
        self.table.setItem(0, 4, QTableWidgetItem("tilt"))
        self.table.setItem(0, 5, QTableWidgetItem("30"))
        self.table.setItem(0, 6, QTableWidgetItem("success"))

        self.table.setItem(1, 0, QTableWidgetItem("lg02"))
        self.table.setItem(1, 1, QTableWidgetItem("2025-02-16 13:37:30"))
        self.table.setItem(1, 2, QTableWidgetItem("desk_gui"))
        self.table.setItem(1, 3, QTableWidgetItem("Led1"))
        self.table.setItem(1, 4, QTableWidgetItem("on"))
        self.table.setItem(1, 5, QTableWidgetItem("255"))
        self.table.setItem(1, 6, QTableWidgetItem("success"))
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        main_layout.addWidget(self.table)
        
        # 하단 Back 버튼
        self.btn_back = QPushButton("Back")
        self.btn_back.setStyleSheet("font-size: 18pt;")
        self.btn_back.setFixedSize(140, 100)
        self.btn_back.clicked.connect(self.go_back)
        main_layout.addWidget(self.btn_back, alignment=Qt.AlignRight)
        
    def go_back(self):
        """
        Back 버튼을 누르면 LogDataWindow를 닫고, 메인 윈도우를 다시 표시합니다.
        """
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
            "R": 0,
            "G": 0,
            "B": 0,
            "DeskHeight": 0,
            "MonitorHeight": 0,
            "MonitorAngle": 0
        }

        self.modes = {
            1: {"R": 1, "G": 1, "B": 1, "DeskHeight": 50, "MonitorHeight": 30, "MonitorAngle": 45},
            2: {"R": 0, "G": 2, "B": 0, "DeskHeight": 40, "MonitorHeight": 35, "MonitorAngle": 30},
            3: {"R": 2, "G": 0, "B": 5, "DeskHeight": 30, "MonitorHeight": 40, "MonitorAngle": 15},
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

        self.label_led_title = QLabel("LED")
        self.label_led_title.setStyleSheet("font-size: 18pt;")

        self.label_r = QLabel(f"R : {self.currentValues['R']}")
        self.label_r.setStyleSheet("font-size: 18pt;")

        self.label_g = QLabel(f"G : {self.currentValues['G']}")
        self.label_g.setStyleSheet("font-size: 18pt;")

        self.label_b = QLabel(f"B : {self.currentValues['B']}")
        self.label_b.setStyleSheet("font-size: 18pt;")

        right_layout.addWidget(self.label_led_title, 0, 0)
        right_layout.addWidget(self.label_r, 0, 1)
        right_layout.addWidget(self.label_g, 0, 2)
        right_layout.addWidget(self.label_b, 0, 3)

        self.label_desk_title = QLabel("DESK")
        self.label_desk_title.setStyleSheet("font-size: 18pt;")

        self.label_desk_height = QLabel(f"Height : {self.currentValues['DeskHeight']}")
        self.label_desk_height.setStyleSheet("font-size: 18pt;")

        right_layout.addWidget(self.label_desk_title, 1, 0)
        right_layout.addWidget(self.label_desk_height, 1, 1)

        self.label_monitor_title = QLabel("MONITOR")
        self.label_monitor_title.setStyleSheet("font-size: 18pt;")

        self.label_monitor_height = QLabel(f"Height : {self.currentValues['MonitorHeight']}")
        self.label_monitor_height.setStyleSheet("font-size: 18pt;")

        self.label_monitor_angle = QLabel(f"Angle : {self.currentValues['MonitorAngle']}")
        self.label_monitor_angle.setStyleSheet("font-size: 18pt;")

        right_layout.addWidget(self.label_monitor_title, 2, 0)
        right_layout.addWidget(self.label_monitor_height, 2, 1)
        right_layout.addWidget(self.label_monitor_angle, 2, 2)

        # 하단: Save in Mode 버튼과 로그 출력 레이블을 포함하는 레이아웃
        save_log_layout = QHBoxLayout()
        self.btn_save_in_mode = QPushButton("Save in Mode")
        self.btn_save_in_mode.setStyleSheet("font-size: 18pt;")
        self.btn_save_in_mode.setFixedSize(200,80)
        # 로그 출력용 레이블
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

    # ─────────────────────────────────────────
    # 로그 메시지 업데이트 함수
    # ─────────────────────────────────────────
    def log_message(self, message):
        self.log_label.setText(message)

    # ─────────────────────────────────────────
    # 상태 라벨 업데이트
    # ─────────────────────────────────────────
    def update_labels(self):
        self.label_r.setText(f"R : {self.currentValues['R']}")
        self.label_g.setText(f"G : {self.currentValues['G']}")
        self.label_b.setText(f"B : {self.currentValues['B']}")
        self.label_desk_height.setText(f"Height : {self.currentValues['DeskHeight']}")
        self.label_monitor_height.setText(f"Height : {self.currentValues['MonitorHeight']}")
        self.label_monitor_angle.setText(f"Angle : {self.currentValues['MonitorAngle']}")

    # ─────────────────────────────────────────
    # 모드 로드 + 서버로 전송 및 로그 메시지 출력
    # ─────────────────────────────────────────
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

    # ─────────────────────────────────────────
    # Control Mode 다이얼로그 (값 변경 후 로그 메시지 출력)
    # ─────────────────────────────────────────
    def enter_control_mode(self):
        dlg = ControlDialog(self.currentValues, self)
        if dlg.exec_() == QDialog.Accepted:
            self.currentValues = dlg.get_values()
            self.update_labels()
            self.send_current_values()
            self.log_message("Control mode updated.")

    # ─────────────────────────────────────────
    # Save in Mode 다이얼로그 (값 저장 후 로그 메시지 출력)
    # ─────────────────────────────────────────
    def go_save_in_mode_page(self):
        dlg = SaveInModeDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            selected_mode = dlg.get_selected_mode()
            if selected_mode in self.modes:
                self.modes[selected_mode] = self.currentValues.copy()
                self.log_message(f"현재 설정을 Mode {selected_mode}에 저장했습니다.")

    # ─────────────────────────────────────────
    # Log Data 창 열기
    # ─────────────────────────────────────────
    def show_log_data_window(self):
        self.log_window = LogDataWindow(self)
        self.log_window.show()
        self.hide()

    # ─────────────────────────────────────────
    # 서버로 현재 상태 전송
    # ─────────────────────────────────────────
    def send_current_values(self):
        data = {
            "LED R": self.currentValues["R"],
            "LED G": self.currentValues["G"],
            "LED B": self.currentValues["B"],
            "Linear Actuator": self.currentValues["DeskHeight"],
            "MonitorHeight": self.currentValues["MonitorHeight"],
            "MonitorAngle": self.currentValues["MonitorAngle"]
        }
        self.client_thread.send_data(data)

    # ─────────────────────────────────────────
    # 서버에서 온 메시지 처리
    # ─────────────────────────────────────────
    def handle_new_message(self, msg):
        if "LED R" in msg:
            self.currentValues["R"] = msg["LED R"]
        if "LED G" in msg:
            self.currentValues["G"] = msg["LED G"]
        if "LED B" in msg:
            self.currentValues["B"] = msg["LED B"]
        if "Linear Actuator" in msg:
            self.currentValues["DeskHeight"] = msg["Linear Actuator"]
        if "MonitorHeight" in msg:
            self.currentValues["MonitorHeight"] = msg["MonitorHeight"]
        if "MonitorAngle" in msg:
            self.currentValues["MonitorAngle"] = msg["MonitorAngle"]
        self.update_labels()

    # ─────────────────────────────────────────
    # 종료 시 소켓 스레드 정리
    # ─────────────────────────────────────────
    def closeEvent(self, event):
        self.client_thread.stop()
        event.accept()


# ─────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
