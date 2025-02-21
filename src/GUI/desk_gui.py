import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from qt_material import apply_stylesheet # pip install qt_material 필수

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
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.brightness = 0  # 초기 밝기 값 (0 ~ 8 사이)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("LED Brightness Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        grid_layout = QGridLayout()
        
        # 위(▲) 버튼: 밝기 증가
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(80, 80)
        up_btn.clicked.connect(self.increase_brightness)
        grid_layout.addWidget(up_btn, 0, 0, alignment=Qt.AlignCenter)
        
        # 현재 밝기 값을 표시하는 라벨
        self.brightness_label = QLabel(str(self.brightness))
        self.brightness_label.setAlignment(Qt.AlignCenter)
        self.brightness_label.setFixedSize(80, 80)
        grid_layout.addWidget(self.brightness_label, 1, 0, alignment=Qt.AlignCenter)
        
        # 아래(▼) 버튼: 밝기 감소
        down_btn = QPushButton("▼")
        down_btn.setFixedSize(80, 80)
        down_btn.clicked.connect(self.decrease_brightness)
        grid_layout.addWidget(down_btn, 2, 0, alignment=Qt.AlignCenter)
        
        layout.addLayout(grid_layout)
        
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    def increase_brightness(self):
        if self.brightness < 9:
            self.brightness += 1
            self.brightness_label.setText(str(self.brightness))

    def decrease_brightness(self):
        if self.brightness > 0:
            self.brightness -= 1
            self.brightness_label.setText(str(self.brightness))


class DeskControlScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        
        self.label = QLabel("Desk Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        grid_layout = QGridLayout()
        btn_up = QPushButton("▲")
        btn_down = QPushButton("▼")
        btn_up.setFixedSize(120, 120)
        btn_down.setFixedSize(120, 120)
        grid_layout.addWidget(btn_up, 0, 1)
        grid_layout.addWidget(btn_down, 2, 1)
        
        layout.addLayout(grid_layout)
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
    
class MonitorControlScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        
        self.label = QLabel("Monitor Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        grid_layout = QGridLayout()
        btn_front = QPushButton("Front")
        btn_up = QPushButton("Up")
        btn_back = QPushButton("Back")
        btn_down = QPushButton("Down")
        
        btn_front.setFixedSize(100, 100)
        btn_back.setFixedSize(100, 100)
        btn_up.setFixedSize(100, 100)
        btn_down.setFixedSize(100, 100)
        
        grid_layout.addWidget(btn_front, 0, 0)
        grid_layout.addWidget(btn_back, 1, 0)
        grid_layout.addWidget(btn_up, 0, 1)
        grid_layout.addWidget(btn_down, 1, 1)
        
        layout.addLayout(grid_layout)
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DESK GUI Example")
        self.setFixedSize(320, 480)  # 3.5인치 화면 비율 고정
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(MainScreen(self.stacked_widget))
        self.stacked_widget.addWidget(ControlModeScreen(self.stacked_widget))
        self.stacked_widget.addWidget(LEDControlScreen(self.stacked_widget))
        self.stacked_widget.addWidget(MonitorControlScreen(self.stacked_widget))
        self.stacked_widget.addWidget(DeskControlScreen(self.stacked_widget))
        
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheet(app, theme='dark_teal.xml') # 스타일 적용
    window.show()
    sys.exit(app.exec_())
