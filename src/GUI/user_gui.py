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
# SaveInModeDialog (Save in Mode)
# ─────────────────────────────────────────
class SaveInModeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save in Mode")
        # 다이얼로그 크기 고정 대신 최소 크기, 혹은 resize
        self.resize(1000, 800)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.radio_group = QButtonGroup(self)

        self.radio_mode1 = QRadioButton("Mode 1")
        self.radio_mode1.setStyleSheet("font-size: 24pt;")
        self.radio_mode2 = QRadioButton("Mode 2")
        self.radio_mode2.setStyleSheet("font-size: 24pt;")
        self.radio_mode3 = QRadioButton("Mode 3")
        self.radio_mode3.setStyleSheet("font-size: 24pt;")

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
        # 창 크기 고정 대신 resize
        self.resize(1280, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        central_widget.setLayout(main_layout)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

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

        self.btn_back = QPushButton("Back")
        self.btn_back.setStyleSheet("font-size: 18pt;")
        # setFixedSize 대신 setMinimumSize
        self.btn_back.setMinimumSize(140, 80)
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
        # 고정 크기 대신 resize
        self.resize(1280, 720)

        self.currentValues = {
            "Brightness": 0,
            "DeskHeight": 0,
            "MonitorHeight": 0,
            "MonitorAngle": 0
        }
        self.modes = {
            1: {"Brightness": 1, "DeskHeight": 50, "MonitorHeight": 30, "MonitorAngle": 45},
            2: {"Brightness": 3, "DeskHeight": 40, "MonitorHeight": 35, "MonitorAngle": 30},
            3: {"Brightness": 8, "DeskHeight": 30, "MonitorHeight": 40, "MonitorAngle": 15},
        }

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        central_widget.setLayout(main_layout)

        # 상단 레이아웃
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        self.label_ergodesk = QLabel("ERGODESK")
        self.label_ergodesk.setStyleSheet("font-size: 18pt; font-weight: bold;")
        self.label_user_id = QLabel("User ID : None")
        self.label_user_id.setStyleSheet("font-size: 18pt;")

        top_layout.addWidget(self.label_ergodesk)
        top_layout.addStretch(1)
        top_layout.addWidget(self.label_user_id)
        main_layout.addLayout(top_layout)

        # 중단 레이아웃
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(10)
        main_layout.addLayout(middle_layout)

        # 좌측 (값 표시 + Save in Mode)
        left_value_layout = QVBoxLayout()
        left_value_layout.setContentsMargins(0, 0, 0, 0)
        left_value_layout.setSpacing(5)

        value_layout = QGridLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(10)

        # Brightness SpinBox
        self.label_brightness_title = QLabel("Brightness:")
        self.label_brightness_title.setStyleSheet("font-size: 24pt;")
        self.spin_brightness = QSpinBox()
        self.spin_brightness.setStyleSheet("font-size: 24pt;")
        self.spin_brightness.setRange(0, 8)
        self.spin_brightness.setValue(self.currentValues["Brightness"])
        value_layout.addWidget(self.label_brightness_title, 0, 0)
        value_layout.addWidget(self.spin_brightness, 0, 1)

        # Desk
        self.label_desk_title = QLabel("DESK:")
        self.label_desk_title.setStyleSheet("font-size: 24pt;")
        self.spin_desk_height = QSpinBox()
        self.spin_desk_height.setStyleSheet("font-size: 24pt;")
        self.spin_desk_height.setRange(0, 50)
        self.spin_desk_height.setValue(self.currentValues["DeskHeight"])
        value_layout.addWidget(self.label_desk_title, 1, 0)
        value_layout.addWidget(self.spin_desk_height, 1, 1)

        # Monitor
        self.label_monitor_title = QLabel("MONITOR:")
        self.label_monitor_title.setStyleSheet("font-size: 24pt;")
        self.spin_monitor_height = QSpinBox()
        self.spin_monitor_height.setStyleSheet("font-size: 24pt;")
        self.spin_monitor_height.setRange(0, 90)
        self.spin_monitor_height.setValue(self.currentValues["MonitorHeight"])

        self.label_monitor_angle_title = QLabel("Angle:")
        self.label_monitor_angle_title.setStyleSheet("font-size: 24pt;")
        self.spin_monitor_angle = QSpinBox()
        self.spin_monitor_angle.setStyleSheet("font-size: 24pt;")
        self.spin_monitor_angle.setRange(0, 90)
        self.spin_monitor_angle.setValue(self.currentValues["MonitorAngle"])

        value_layout.addWidget(self.label_monitor_title, 2, 0)
        value_layout.addWidget(self.spin_monitor_height, 2, 1)
        value_layout.addWidget(self.label_monitor_angle_title, 2, 2)
        value_layout.addWidget(self.spin_monitor_angle, 2, 3)

        left_value_layout.addLayout(value_layout)

        self.btn_save_in_mode = QPushButton("Save in Mode")
        self.btn_save_in_mode.setStyleSheet("font-size: 18pt;")
        # setFixedSize -> setMinimumSize
        self.btn_save_in_mode.setMinimumSize(200, 60)
        left_value_layout.addWidget(self.btn_save_in_mode)

        left_value_layout_widget = QWidget()
        left_value_layout_widget.setLayout(left_value_layout)
        left_value_layout_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        middle_layout.addWidget(left_value_layout_widget, 4)

        # 우측 (모드 버튼)
        right_button_layout = QVBoxLayout()
        right_button_layout.setContentsMargins(0, 0, 0, 0)
        right_button_layout.setSpacing(10)

        self.btn_mode1 = QPushButton("Mode 1")
        self.btn_mode1.setStyleSheet("font-size: 18pt;")
        self.btn_mode1.setMinimumSize(200, 80)

        self.btn_mode2 = QPushButton("Mode 2")
        self.btn_mode2.setStyleSheet("font-size: 18pt;")
        self.btn_mode2.setMinimumSize(200, 80)

        self.btn_mode3 = QPushButton("Mode 3")
        self.btn_mode3.setStyleSheet("font-size: 18pt;")
        self.btn_mode3.setMinimumSize(200, 80)

        right_button_layout.addWidget(self.btn_mode1)
        right_button_layout.addWidget(self.btn_mode2)
        right_button_layout.addWidget(self.btn_mode3)

        right_button_layout_widget = QWidget()
        right_button_layout_widget.setLayout(right_button_layout)
        right_button_layout_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        middle_layout.addWidget(right_button_layout_widget, 1)

        # 하단 레이아웃
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)

        self.btn_log_data = QPushButton("Log Data")
        self.btn_log_data.setStyleSheet("font-size: 18pt;")
        # setFixedSize -> setMinimumSize
        self.btn_log_data.setMinimumSize(200, 60)

        self.log_label = QLabel("")
        self.log_label.setStyleSheet("font-size: 18pt; color: white; background-color: #444444;")
        self.log_label.setFixedHeight(60)
        self.log_label.setAlignment(Qt.AlignCenter)

        bottom_layout.addWidget(self.log_label)
        bottom_layout.addWidget(self.btn_log_data)
        main_layout.addLayout(bottom_layout)

        # SpinBox 값 변경 연결
        self.spin_brightness.valueChanged.connect(self.on_value_changed)
        self.spin_desk_height.valueChanged.connect(self.on_value_changed)
        self.spin_monitor_height.valueChanged.connect(self.on_value_changed)
        self.spin_monitor_angle.valueChanged.connect(self.on_value_changed)

        # 버튼 시그널
        self.btn_mode1.clicked.connect(self.load_mode1)
        self.btn_mode2.clicked.connect(self.load_mode2)
        self.btn_mode3.clicked.connect(self.load_mode3)
        self.btn_save_in_mode.clicked.connect(self.go_save_in_mode_page)
        self.btn_log_data.clicked.connect(self.show_log_data_window)

        self.client_thread = SocketClientThread('192.168.0.45', 1234)
        self.client_thread.newMessage.connect(self.handle_new_message)
        self.client_thread.start()

    def on_value_changed(self):
        self.currentValues["Brightness"] = self.spin_brightness.value()
        self.currentValues["DeskHeight"] = self.spin_desk_height.value()
        self.currentValues["MonitorHeight"] = self.spin_monitor_height.value()
        self.currentValues["MonitorAngle"] = self.spin_monitor_angle.value()
        self.send_current_values()
        self.log_message("Values updated.")

    def log_message(self, message):
        self.log_label.setText(message)

    def update_spinboxes(self):
        self.spin_brightness.setValue(self.currentValues["Brightness"])
        self.spin_desk_height.setValue(self.currentValues["DeskHeight"])
        self.spin_monitor_height.setValue(self.currentValues["MonitorHeight"])
        self.spin_monitor_angle.setValue(self.currentValues["MonitorAngle"])

    def load_mode1(self):
        self.currentValues = self.modes[1].copy()
        self.update_spinboxes()
        self.send_current_values()
        self.log_message("Mode 1 loaded.")

    def load_mode2(self):
        self.currentValues = self.modes[2].copy()
        self.update_spinboxes()
        self.send_current_values()
        self.log_message("Mode 2 loaded.")

    def load_mode3(self):
        self.currentValues = self.modes[3].copy()
        self.update_spinboxes()
        self.send_current_values()
        self.log_message("Mode 3 loaded.")

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
            "Brightness": self.currentValues["Brightness"],
            "Linear Actuator": self.currentValues["DeskHeight"],
            "MonitorHeight": self.currentValues["MonitorHeight"],
            "MonitorAngle": self.currentValues["MonitorAngle"]
        }
        self.client_thread.send_data(data)

    def handle_new_message(self, msg):
        if "Brightness" in msg:
            self.currentValues["Brightness"] = msg["Brightness"]
        if "Linear Actuator" in msg:
            self.currentValues["DeskHeight"] = msg["Linear Actuator"]
        if "MonitorHeight" in msg:
            self.currentValues["MonitorHeight"] = msg["MonitorHeight"]
        if "MonitorAngle" in msg:
            self.currentValues["MonitorAngle"] = msg["MonitorAngle"]
        self.update_spinboxes()

    def closeEvent(self, event):
        self.client_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
