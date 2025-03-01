import sys
import random
import datetime
import os
import socketio
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent, pyqtSignal

# UI 파일 로드 (경로에 맞게 수정)
from_class = uic.loadUiType("/home/qpzjadla/iot-repo-3/src/Communication/userGUI.ui")[0]

class MainWindow(QMainWindow, from_class):
    updateUI = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        print(os.getcwd())

        self.sio = socketio.Client()
        try:
            self.sio.connect("http://192.168.0.45:2000")
            print("SocketIO connected!")
        except Exception as e:
            print("SocketIO connection failed:", e)

        @self.sio.on('response_data')
        def on_response_data(data):
            print("✅ Received from server:", data)

        @self.sio.on('desk_update')
        def on_desk_update(data):
            print("✅ User GUI received desk update from server:", data)
            self.updateUI.emit(data)

        self.updateUI.connect(self.handle_desk_update)

        self.current_uid = None
        self.rfid_label.setText("None(RFID Status: Unrecognized)")

        self.mode1_radio.setEnabled(False)
        self.mode2_radio.setEnabled(False)
        self.mode_radio.setEnabled(False)

        self.brightness_spin.valueChanged.connect(self.on_spin_changed)
        self.deskh_spin.valueChanged.connect(self.on_spin_changed)
        self.monitort_spin.valueChanged.connect(self.on_spin_changed)
        self.monitorh_spin.valueChanged.connect(self.on_spin_changed)

        self.brightness_spin.installEventFilter(self)
        self.deskh_spin.installEventFilter(self)
        self.monitort_spin.installEventFilter(self)
        self.monitorh_spin.installEventFilter(self)

        self.save_btn.clicked.connect(self.on_save_clicked)
        self.log_btn.clicked.connect(self.open_log_dialog)

    def handle_desk_update(self, data):
        self.brightness_spin.setValue(data.get("light", self.brightness_spin.value()))
        self.deskh_spin.setValue(data.get("desk_height", self.deskh_spin.value()))
        self.monitorh_spin.setValue(data.get("monitor_height", self.monitorh_spin.value()))
        self.monitort_spin.setValue(data.get("monitor_angle", self.monitort_spin.value()))

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source in [self.brightness_spin, self.deskh_spin, self.monitort_spin, self.monitorh_spin]:
            if event.key() == Qt.Key_Up:
                source.setValue(source.value() + 1)
                self.on_spin_changed()
                return True
            elif event.key() == Qt.Key_Down:
                source.setValue(source.value() - 1)
                self.on_spin_changed()
                return True
        return super().eventFilter(source, event)

    def simulate_rfid_tag(self):
        fake_uid = "04AABBCCDD"
        self.on_rfid_tagged(fake_uid)

    def on_rfid_tagged(self, uid):
        self.current_uid = uid
        self.rfid_label.setText(f"UID: {uid}")
        self.mode1_radio.setEnabled(True)
        self.mode2_radio.setEnabled(True)
        self.mode_radio.setEnabled(True)

    def on_spin_changed(self):
        data = {
            "user_id": self.current_uid if self.current_uid else "None",
            "function_code": random.randint(1, 10),
            "mode": self.get_current_mode_index(),
            "request_id": random.randint(1000, 9999),
            "timestamp": datetime.datetime.now().isoformat(),
            "light": self.brightness_spin.value(),
            "desk_status": 1 if self.deskh_spin.value() > 0 else 0,
            "monitor_height": self.monitorh_spin.value(),
            "monitor_angle": self.monitort_spin.value(),
            "desk_height": self.deskh_spin.value()
        }
        print("➡ Sending spinbox changed data:", data)
        self.sio.emit('send_data', data)

    def get_current_mode_index(self):
        if self.mode1_radio.isChecked():
            return 0
        elif self.mode2_radio.isChecked():
            return 1
        elif self.mode_radio.isChecked():
            return 2
        else:
            return -1

    def on_save_clicked(self):
        if not self.current_uid:
            QMessageBox.warning(self, "Warning", "RFID가 태그되지 않았습니다.")
            return
        mode_idx = self.get_current_mode_index()
        if mode_idx == -1:
            QMessageBox.warning(self, "Warning", "모드를 선택해주세요.")
            return

        data = {
            "user_id": self.current_uid,
            "function_code": 99,
            "mode": mode_idx,
            "request_id": random.randint(1000, 9999),
            "timestamp": datetime.datetime.now().isoformat(),
            "light": self.brightness_spin.value(),
            "desk_status": 1 if self.deskh_spin.value() > 0 else 0,
            "monitor_height": self.monitorh_spin.value(),
            "monitor_angle": self.monitort_spin.value(),
            "desk_height": self.deskh_spin.value()
        }
        print("➡ Saving current mode data:", data)
        self.sio.emit('send_data', data)
        QMessageBox.information(self, "Saved", f"모드 {mode_idx+1} 상태를 저장했습니다.")

    def open_log_dialog(self):
        QMessageBox.information(self, "Log", "여기서 로그 페이지를 띄우거나 테이블로 표시합니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
