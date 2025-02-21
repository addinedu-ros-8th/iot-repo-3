import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

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
        layout = QVBoxLayout()
        
        self.label = QLabel("LED Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        grid_layout = QGridLayout()
        colors = ["R", "G", "B"]
        for i, color in enumerate(colors):
            up_btn = QPushButton("▲")
            up_btn.setFixedSize(80, 80)
            grid_layout.addWidget(up_btn, 0, i)
            
            color_btn = QLabel(color)
            color_btn.setFixedSize(80, 80)
            grid_layout.addWidget(color_btn, 1, i)
            
            down_btn = QPushButton("▼")
            down_btn.setFixedSize(80, 80)
            grid_layout.addWidget(down_btn, 2, i)
        
        layout.addLayout(grid_layout)
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

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
        self.setWindowTitle("PyQt GUI Example")
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
    window.show()
    sys.exit(app.exec_())
