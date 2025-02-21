import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from qt_material import apply_stylesheet

class ControlDialog(QDialog):
    """
    Control Mode 다이얼로그.
    LED(R,G,B), Desk(Height), Monitor(Height, Angle) 값을
    사용자가 직접 입력할 수 있게 하는 예시입니다.
    """
    def __init__(self, current_values, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control Mode")
        self.current_values = current_values.copy()  # 현재값 복사해서 로컬에서 수정
        
        layout = QVBoxLayout()
        
        # LED 설정
        led_layout = QHBoxLayout()
        self.spin_r = QSpinBox()
        self.spin_g = QSpinBox()
        self.spin_b = QSpinBox()
        self.spin_r.setRange(0, 8)
        self.spin_g.setRange(0, 8)
        self.spin_b.setRange(0, 8)
        
        # 현재값 반영
        self.spin_r.setValue(self.current_values["R"])
        self.spin_g.setValue(self.current_values["G"])
        self.spin_b.setValue(self.current_values["B"])
        
        led_layout.addWidget(QLabel("R:"))
        led_layout.addWidget(self.spin_r)
        led_layout.addWidget(QLabel("G:"))
        led_layout.addWidget(self.spin_g)
        led_layout.addWidget(QLabel("B:"))
        led_layout.addWidget(self.spin_b)
        
        # Desk 설정
        desk_layout = QHBoxLayout()
        self.spin_desk_height = QSpinBox()
        self.spin_desk_height.setRange(0, 50)  # 예시로 0~200
        self.spin_desk_height.setValue(self.current_values["DeskHeight"])
        desk_layout.addWidget(QLabel("Desk Height:"))
        desk_layout.addWidget(self.spin_desk_height)
        
        # Monitor 설정
        monitor_layout = QHBoxLayout()
        self.spin_monitor_height = QSpinBox()
        self.spin_monitor_height.setRange(0, 90)  # 예시 범위
        self.spin_monitor_height.setValue(self.current_values["MonitorHeight"])
        
        self.spin_monitor_angle = QSpinBox()
        self.spin_monitor_angle.setRange(0, 90)  # 예시 범위
        self.spin_monitor_angle.setValue(self.current_values["MonitorAngle"])
        
        monitor_layout.addWidget(QLabel("Monitor Height:"))
        monitor_layout.addWidget(self.spin_monitor_height)
        monitor_layout.addWidget(QLabel("Angle:"))
        monitor_layout.addWidget(self.spin_monitor_angle)
        
        layout.addLayout(led_layout)
        layout.addLayout(desk_layout)
        layout.addLayout(monitor_layout)
        
        # 버튼(OK/Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
    def get_values(self):
        """
        사용자가 최종 OK를 눌렀을 때, 현재 spin box 값들을 반환.
        """
        return {
            "R": self.spin_r.value(),
            "G": self.spin_g.value(),
            "B": self.spin_b.value(),
            "DeskHeight": self.spin_desk_height.value(),
            "MonitorHeight": self.spin_monitor_height.value(),
            "MonitorAngle": self.spin_monitor_angle.value()
        }


class SaveInModeDialog(QDialog):
    """
    Save in Mode 버튼을 눌렀을 때 뜨는 다이얼로그.
    Mode1, Mode2, Mode3 중 어디에 저장할지 고르는 예시입니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save in Mode")
        
        layout = QVBoxLayout()
        
        # 라디오 버튼을 이용해 Mode1, Mode2, Mode3 중 선택
        self.radio_group = QButtonGroup(self)
        
        self.radio_mode1 = QRadioButton("Mode 1")
        self.radio_mode2 = QRadioButton("Mode 2")
        self.radio_mode3 = QRadioButton("Mode 3")
        
        # 기본 선택
        self.radio_mode1.setChecked(True)
        
        self.radio_group.addButton(self.radio_mode1, 1)
        self.radio_group.addButton(self.radio_mode2, 2)
        self.radio_group.addButton(self.radio_mode3, 3)
        
        layout.addWidget(self.radio_mode1)
        layout.addWidget(self.radio_mode2)
        layout.addWidget(self.radio_mode3)
        
        # OK/Cancel 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
    def get_selected_mode(self):
        """
        사용자가 선택한 모드 번호(1,2,3)를 반환.
        """
        return self.radio_group.checkedId()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 메인 윈도우 설정
        self.setWindowTitle("ErgoDesk GUI")
        self.resize(1600, 900)
        
        # ─────────────────────────────────────────
        # 현재(혹은 기본)값과 Mode별로 저장된 값
        # ─────────────────────────────────────────
        self.currentValues = {
            "R": 0,
            "G": 0,
            "B": 0,
            "DeskHeight": 0,
            "MonitorHeight": 0,
            "MonitorAngle": 0
        }
        
        # 실제 프로젝트에서는 파일, DB 등에서 로드할 수도 있습니다.
        # 여기서는 예시로 모드별 초기값을 임의로 설정
        self.modes = {
            1: {"R": 1, "G": 1, "B": 1, "DeskHeight": 50, "MonitorHeight": 30, "MonitorAngle": 45},
            2: {"R": 0,   "G": 2, "B": 0,   "DeskHeight": 40, "MonitorHeight": 35, "MonitorAngle": 30},
            3: {"R": 2, "G": 0,   "B": 5, "DeskHeight": 30, "MonitorHeight": 40, "MonitorAngle": 15},
        }
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 상단 레이아웃 (ERGODESK, User ID, Log Data)
        top_layout = QHBoxLayout()
        self.label_ergodesk = QLabel("ERGODESK")
        self.label_ergodesk.setStyleSheet("font-size: 18pt; font-weight: bold;")
        
        self.label_user_id = QLabel("User ID : None")
        self.label_log_data = QLabel("Log Data")
        
        top_layout.addWidget(self.label_ergodesk)
        top_layout.addWidget(self.label_user_id)
        top_layout.addWidget(self.label_log_data)
        
        main_layout.addLayout(top_layout)
        
        # 중단 레이아웃 (좌: Mode 버튼들, 우: LED/Desk/Monitor)
        middle_layout = QHBoxLayout()
        main_layout.addLayout(middle_layout)
        
        # 좌측 버튼 레이아웃
        left_layout = QVBoxLayout()
        self.btn_mode1 = QPushButton("Mode 1")
        self.btn_mode2 = QPushButton("Mode 2")
        self.btn_mode3 = QPushButton("Mode 3")
        self.btn_control = QPushButton("Control Mode")
        
        left_layout.addWidget(self.btn_mode1)
        left_layout.addWidget(self.btn_mode2)
        left_layout.addWidget(self.btn_mode3)
        left_layout.addWidget(self.btn_control)
        
        middle_layout.addLayout(left_layout)
        
        # 우측 LED, Desk, Monitor 값 표시
        right_layout = QGridLayout()
        middle_layout.addLayout(right_layout)
        
        # LED
        self.label_led_title = QLabel("LED")
        self.label_r = QLabel(f"R : {self.currentValues['R']}")
        self.label_g = QLabel(f"G : {self.currentValues['G']}")
        self.label_b = QLabel(f"B : {self.currentValues['B']}")
        
        right_layout.addWidget(self.label_led_title, 0, 0)
        right_layout.addWidget(self.label_r,         0, 1)
        right_layout.addWidget(self.label_g,         0, 2)
        right_layout.addWidget(self.label_b,         0, 3)
        
        # DESK
        self.label_desk_title = QLabel("DESK")
        self.label_desk_height = QLabel(f"Height : {self.currentValues['DeskHeight']}")
        
        right_layout.addWidget(self.label_desk_title, 1, 0)
        right_layout.addWidget(self.label_desk_height, 1, 1)
        
        # MONITOR
        self.label_monitor_title = QLabel("MONITOR")
        self.label_monitor_height = QLabel(f"Height : {self.currentValues['MonitorHeight']}")
        self.label_monitor_angle = QLabel(f"Angle : {self.currentValues['MonitorAngle']}")
        
        right_layout.addWidget(self.label_monitor_title, 2, 0)
        right_layout.addWidget(self.label_monitor_height, 2, 1)
        right_layout.addWidget(self.label_monitor_angle,  2, 2)
        
        # 하단 Save in Mode 버튼
        self.btn_save_in_mode = QPushButton("Save in Mode")
        main_layout.addWidget(self.btn_save_in_mode, alignment=Qt.AlignRight)
        
        # 시그널 연결
        self.btn_mode1.clicked.connect(self.load_mode1)
        self.btn_mode2.clicked.connect(self.load_mode2)
        self.btn_mode3.clicked.connect(self.load_mode3)
        self.btn_control.clicked.connect(self.enter_control_mode)
        self.btn_save_in_mode.clicked.connect(self.go_save_in_mode_page)
        
    def update_labels(self):
        """
        self.currentValues를 기반으로 화면의 라벨들을 업데이트
        """
        self.label_r.setText(f"R : {self.currentValues['R']}")
        self.label_g.setText(f"G : {self.currentValues['G']}")
        self.label_b.setText(f"B : {self.currentValues['B']}")
        self.label_desk_height.setText(f"Height : {self.currentValues['DeskHeight']}")
        self.label_monitor_height.setText(f"Height : {self.currentValues['MonitorHeight']}")
        self.label_monitor_angle.setText(f"Angle : {self.currentValues['MonitorAngle']}")
        
    def load_mode1(self):
        self.currentValues = self.modes[1].copy()
        self.update_labels()
        
    def load_mode2(self):
        self.currentValues = self.modes[2].copy()
        self.update_labels()
        
    def load_mode3(self):
        self.currentValues = self.modes[3].copy()
        self.update_labels()
        
    def enter_control_mode(self):
        """
        Control Mode: 사용자에게 현재값을 편집할 수 있는 다이얼로그를 띄움
        """
        dlg = ControlDialog(self.currentValues, self)
        if dlg.exec_() == QDialog.Accepted:
            # OK를 눌렀을 때만 값 반영
            self.currentValues = dlg.get_values()
            self.update_labels()
        
    def go_save_in_mode_page(self):
        """
        Save in Mode: 어느 모드에 저장할지 선택하는 다이얼로그를 띄우고,
        선택된 모드에 self.currentValues를 저장
        """
        dlg = SaveInModeDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            selected_mode = dlg.get_selected_mode()
            if selected_mode in self.modes:
                self.modes[selected_mode] = self.currentValues.copy()
                # 필요하다면 확인 메시지, 로그 남기기 등 추가
                print(f"현재 설정을 Mode {selected_mode}에 저장했습니다.")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheet(app, theme='dark_teal.xml') # 스타일 적용
    window.show()
    sys.exit(app.exec_())
