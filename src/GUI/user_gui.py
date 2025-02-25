import sys
import socket
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qt_material import apply_stylesheet  # pip install qt_material 설치

# ─────────────────────────────────────────
# QThread를 이용한 소켓 클라이언트 (통일된 JSON 데이터 형식 사용)
# ─────────────────────────────────────────
class SocketClientThread(QThread):
    newMessage = pyqtSignal(dict)
    
    def __init__(self, host, port, parent=None):
        super().__init__(parent)
        self.host = '192.168.0.45'
        self.port = 3001
        self.running = True
        self.sock = None
        self.connected = False  # 연결 상태 플래그

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
            print("서버에 연결되었습니다. (GUI 클라이언트)")
        except Exception as e:
            print("서버 연결 실패:", e)
            self.connected = False
            return

        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("서버가 연결을 종료했습니다.")
                    self.connected = False
                    break
                message = data.decode('utf-8')
                try:
                    json_message = json.loads(message)
                    self.newMessage.emit(json_message)
                except json.JSONDecodeError:
                    print("수신된 메시지 (문자열):", message)
            except Exception as e:
                print("수신 오류:", e)
                self.connected = False
                break

        self.sock.close()

    def send_data(self, data):
        if not self.connected or self.sock is None or self.sock.fileno() == -1:
            print("소켓이 연결되어 있지 않습니다. 데이터를 전송할 수 없습니다.")
            return
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
# RFID 작업 다이얼로그 (저장/불러오기 선택)
# ─────────────────────────────────────────
class SaveOrLoadRFIDDialog(QDialog):
    def __init__(self, rfid, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"RFID 카드 [{rfid}] 작업 선택")
        self.resize(400, 200)
        self.rfid = rfid
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        label = QLabel(f"카드 [{rfid}]에 대해 아래 작업 중 선택하세요:")
        label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(label)
        
        self.btn_load = QPushButton("저장된 모드 불러오기")
        self.btn_load.setStyleSheet("font-size: 14pt;")
        self.btn_save = QPushButton("현재 설정 저장")
        self.btn_save.setStyleSheet("font-size: 14pt;")
        
        # 각각의 버튼에 대해 accept()/reject()를 사용하여 선택 후 종료
        self.btn_load.clicked.connect(self.accept)
        self.btn_save.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_load)
        button_layout.addWidget(self.btn_save)
        layout.addLayout(button_layout)


# ─────────────────────────────────────────
# Log Data Window (로그 테이블 화면)
# ─────────────────────────────────────────
class LogDataWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowTitle("Log Data")
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
        # 예제 데이터
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
        self.btn_back.setMinimumSize(140, 80)
        self.btn_back.clicked.connect(self.go_back)
        main_layout.addWidget(self.btn_back, alignment=Qt.AlignRight)

    def go_back(self):
        self.main_window.show()
        self.close()


# ─────────────────────────────────────────
# 메인 윈도우 (User GUI: Desk GUI와 통신 연동)
# ─────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ErgoDesk GUI")
        self.resize(1280, 720)

        # 현재 설정 값 (통일된 데이터 형식에 맞춤)
        self.currentValues = {
            "Brightness": 0,
            "DeskHeight": 0,
            "MonitorHeight": 0,
            "MonitorAngle": 0
        }
        # 미리 정의된 모드 (예시)
        self.modes = {
            1: {"Brightness": 1, "DeskHeight": 50, "MonitorHeight": 30, "MonitorAngle": 45},
            2: {"Brightness": 3, "DeskHeight": 40, "MonitorHeight": 35, "MonitorAngle": 30},
            3: {"Brightness": 8, "DeskHeight": 30, "MonitorHeight": 40, "MonitorAngle": 15},
        }
        # RFID 카드별 저장된 모드 설정 (카드ID: 설정 값)
        self.rfid_modes = {}
        self.active_rfid = None  # 현재 인식된 RFID 카드

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
        # RFID 상태 표시 라벨 추가
        self.label_rfid_status = QLabel("RFID 상태: 미인식")
        self.label_rfid_status.setStyleSheet("font-size: 18pt; color: red;")
        top_layout.addWidget(self.label_ergodesk)
        top_layout.addStretch(1)
        top_layout.addWidget(self.label_user_id)
        top_layout.addWidget(self.label_rfid_status)
        main_layout.addLayout(top_layout)

        # 중단 레이아웃 (설정 값 표시 및 모드 버튼)
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(10)
        main_layout.addLayout(middle_layout)

        # 좌측: 설정 값 표시 + "Save in Mode" 버튼
        left_value_layout = QVBoxLayout()
        left_value_layout.setContentsMargins(0, 0, 0, 0)
        left_value_layout.setSpacing(5)
        value_layout = QGridLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(10)
        self.label_brightness_title = QLabel("Brightness:")
        self.label_brightness_title.setStyleSheet("font-size: 24pt;")
        self.spin_brightness = QSpinBox()
        self.spin_brightness.setStyleSheet("font-size: 24pt;")
        self.spin_brightness.setRange(0, 8)
        self.spin_brightness.setValue(self.currentValues["Brightness"])
        value_layout.addWidget(self.label_brightness_title, 0, 0)
        value_layout.addWidget(self.spin_brightness, 0, 1)
        self.label_desk_title = QLabel("Desk Height:")
        self.label_desk_title.setStyleSheet("font-size: 24pt;")
        self.spin_desk_height = QSpinBox()
        self.spin_desk_height.setStyleSheet("font-size: 24pt;")
        self.spin_desk_height.setRange(0, 50)
        self.spin_desk_height.setValue(self.currentValues["DeskHeight"])
        value_layout.addWidget(self.label_desk_title, 1, 0)
        value_layout.addWidget(self.spin_desk_height, 1, 1)
        self.label_monitor_title = QLabel("Monitor Height:")
        self.label_monitor_title.setStyleSheet("font-size: 24pt;")
        self.spin_monitor_height = QSpinBox()
        self.spin_monitor_height.setStyleSheet("font-size: 24pt;")
        self.spin_monitor_height.setRange(0, 90)
        self.spin_monitor_height.setValue(self.currentValues["MonitorHeight"])
        self.label_monitor_angle_title = QLabel("Monitor Tilt:")
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
        self.btn_save_in_mode.setMinimumSize(200, 60)
        left_value_layout.addWidget(self.btn_save_in_mode)
        left_value_layout_widget = QWidget()
        left_value_layout_widget.setLayout(left_value_layout)
        left_value_layout_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        middle_layout.addWidget(left_value_layout_widget, 4)

        # 우측: 모드 버튼
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

        # 하단 레이아웃 (로그 메시지 및 Log Data 버튼)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)
        self.btn_log_data = QPushButton("Log Data")
        self.btn_log_data.setStyleSheet("font-size: 18pt;")
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
        # 버튼 시그널 연결
        self.btn_mode1.clicked.connect(self.load_mode1)
        self.btn_mode2.clicked.connect(self.load_mode2)
        self.btn_mode3.clicked.connect(self.load_mode3)
        self.btn_save_in_mode.clicked.connect(self.save_current_mode_to_rfid)
        self.btn_log_data.clicked.connect(self.show_log_data_window)

        # 소켓 클라이언트 시작 (통일된 데이터 형식 사용)
        self.client_thread = SocketClientThread('192.168.0.45', 2007)
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

    def save_current_mode_to_rfid(self):
        if self.active_rfid:
            self.rfid_modes[self.active_rfid] = self.currentValues.copy()
            self.log_message(f"현재 설정이 RFID 카드 [{self.active_rfid}]에 저장되었습니다.")
        else:
            self.log_message("RFID 카드가 인식되지 않았습니다.")

    def show_log_data_window(self):
        self.log_window = LogDataWindow(self)
        self.log_window.show()
        self.hide()

    def send_current_values(self):
        # 통일된 데이터 형식으로 메시지 전송
        data = {
            "function_code": "CMD001",
            "mode": 0,
            "brightness": self.currentValues["Brightness"],
            "monitor_height": self.currentValues["MonitorHeight"],
            "monitor_tilt": self.currentValues["MonitorAngle"],
            "desk_height": self.currentValues["DeskHeight"],
            "request_id": "desk_gui",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        if self.active_rfid:
            data["rfid"] = self.active_rfid
        self.client_thread.send_data(data)

    def handle_new_message(self, msg):
        # RFID 필드가 포함된 메시지 처리
        if "rfid" in msg:
            rfid = msg["rfid"]
            self.active_rfid = rfid
            # RFID 상태 라벨 업데이트 (인식됨)
            self.label_rfid_status.setText(f"RFID 상태: [{rfid}] 인식됨")
            self.label_rfid_status.setStyleSheet("font-size: 18pt; color: green;")
            self.log_message(f"RFID 카드 [{rfid}] 인식됨.")
            if rfid in self.rfid_modes:
                dlg = SaveOrLoadRFIDDialog(rfid, self)
                if dlg.exec_() == QDialog.Accepted:
                    self.currentValues = self.rfid_modes[rfid].copy()
                    self.log_message(f"RFID 카드 [{rfid}]의 설정 불러옴.")
                    self.update_spinboxes()
                    self.send_current_values()
                else:
                    self.rfid_modes[rfid] = self.currentValues.copy()
                    self.log_message(f"현재 설정을 RFID 카드 [{rfid}]에 저장함.")
            else:
                dlg = SaveOrLoadRFIDDialog(rfid, self)
                if dlg.exec_() == QDialog.Accepted:
                    self.log_message(f"저장된 설정이 없으므로, 현재 설정을 불러올 수 없습니다.")
                else:
                    self.rfid_modes[rfid] = self.currentValues.copy()
                    self.log_message(f"현재 설정을 RFID 카드 [{rfid}]에 저장함.")
        # 나머지 필드 업데이트 (서버로부터 받은 값)
        if "brightness" in msg and not self.spin_brightness.hasFocus():
            self.currentValues["Brightness"] = msg["brightness"]
        if "desk_height" in msg:
            self.currentValues["DeskHeight"] = msg["desk_height"]
        if "monitor_height" in msg:
            self.currentValues["MonitorHeight"] = msg["monitor_height"]
        if "monitor_tilt" in msg:
            self.currentValues["MonitorAngle"] = msg["monitor_tilt"]
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
