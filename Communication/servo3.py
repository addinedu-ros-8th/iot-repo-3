import sys
import threading
import socket
import json
import serial
import time
import select
import termios
import tty
import pymysql  # MariaDB 연결을 위한 라이브러리

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qt_material import apply_stylesheet

# ---------------------------
# 글로벌 변수 및 설정
# ---------------------------
exit_flag = False

HOST = '0.0.0.0'
PORT = 2005

# 클라이언트 전송 시 동기화를 위한 lock
client_lock = threading.Lock()

# MariaDB 연결 설정
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '0000'
DB_NAME = 'ergodb'

# Arduino 연결 시도 (예: /dev/ttyACM3, /dev/ttyACM0)
ser0 = None
ser1 = None
try:
    ser0 = serial.Serial('/dev/ttyACM3', 9600, timeout=1)
    time.sleep(2)
    print("Dynamic Board에 연결되었습니다. (서버에서)")
except Exception as e:
    print("Dynamic Board 연결 오류:", e)

try:
    ser1 = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    print("Static Board에 연결되었습니다. (서버에서)")
except Exception as e:
    print("Static Board 연결 오류:", e)

# ---------------------------
# 서버 관련 함수들
# ---------------------------
def insert_into_db(data):
    """JSON 데이터를 MariaDB 'desk' 테이블에 삽입"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO desk (led_r, led_g, led_b, servo_1, servo_2, LinearActuator)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (
                data.get('led_r', 0),
                data.get('led_g', 0),
                data.get('led_b', 0),
                data.get('servo_1', 0),
                data.get('servo_2', 0),
                data.get('LinearActuator', 0)
            ))
            connection.commit()
            print("DB에 데이터 삽입 완료:", data)
    except Exception as e:
        print("DB 삽입 오류:", e)
    finally:
        connection.close()

def send_to_client(conn, msg):
    """클라이언트 소켓에 안전하게 메시지 전송"""
    try:
        with client_lock:
            conn.sendall(msg.encode('utf-8'))
    except Exception as e:
        print("클라이언트 전송 오류:", e)

def keyboard_listener():
    """키보드(ESC 키) 입력 감지: 필요시 사용 (현재는 GUI 창 종료로 대체 가능)"""
    global exit_flag
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while not exit_flag:
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # ESC 키 감지
                    print("\nESC 키 입력 감지. 종료합니다.")
                    exit_flag = True
                    break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def arduino_listener(ser, port_name, client_conn):
    """각 Arduino 보드의 시리얼 데이터를 처리"""
    if not ser:
        return
    while not exit_flag:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print(f"Arduino 메시지 ({port_name}, 원본):", line)
                    try:
                        json_data = json.loads(line)
                        print(f"Arduino 메시지 ({port_name}, JSON 파싱 성공):", json_data)
                        insert_into_db(json_data)
                    except json.JSONDecodeError:
                        json_data = {"arduino_data": line}
                        print(f"Arduino 메시지 ({port_name}, JSON 파싱 실패):", json_data)
                    try:
                        msg = json.dumps(json_data, separators=(',', ':'))
                        send_to_client(client_conn, msg)
                        print(f"클라이언트 전송 메시지 ({port_name}):", msg)
                    except Exception as e:
                        print("클라이언트 전송 오류:", e)
                        break
        except Exception as e:
            print(f"Arduino 리스너 오류 ({port_name}):", e)
            break

def run_server():
    """서버 소켓 실행 및 클라이언트/시리얼 통신 처리"""
    global exit_flag
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"서버가 {PORT} 포트에서 대기 중입니다.")
        # 타임아웃을 설정하여 주기적으로 exit_flag를 확인
        server_socket.settimeout(1.0)
        conn = None
        while not exit_flag:
            try:
                conn, addr = server_socket.accept()
                break
            except socket.timeout:
                continue
        if not conn:
            print("클라이언트 연결 없음, 서버 종료.")
            return
        with conn:
            print("클라이언트 연결됨:", addr)
            conn.settimeout(0.5)
            # 두 Arduino 리스너 스레드 실행
            if ser0:
                threading.Thread(target=arduino_listener, args=(ser0, 'ACM0', conn), daemon=True).start()
            if ser1:
                threading.Thread(target=arduino_listener, args=(ser1, 'ACM1', conn), daemon=True).start()
            while not exit_flag:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print("클라이언트 연결 종료.")
                        break
                    received_message = data.decode('utf-8')
                    print("클라이언트로부터 수신한 메시지:", received_message)
                    try:
                        json_data = json.loads(received_message)
                        print("서버: 새로운 데이터 수신됨:", json_data)
                        insert_into_db(json_data)
                    except json.JSONDecodeError as e:
                        print("클라이언트 JSON 파싱 에러:", e)
                        json_data = None
                    if json_data is not None:
                        message_to_arduino = json.dumps(json_data, separators=(',', ':')) + "\n"
                        if ser0:
                            ser0.write(message_to_arduino.encode('utf-8'))
                            print("Arduino (ACM0)로 전송:", message_to_arduino)
                        if ser1:
                            ser1.write(message_to_arduino.encode('utf-8'))
                            print("Arduino (ACM1)로 전송:", message_to_arduino)
                    response = {"status": "ok", "received": json_data, "message": "성공"}
                    response_str = json.dumps(response, separators=(',', ':'))
                    send_to_client(conn, response_str)
                    print("클라이언트로 응답 전송:", response_str)
                except socket.timeout:
                    continue
                except Exception as e:
                    print("서버 처리 중 오류 발생:", e)
                    break
            print("서버 종료 시작.")

# ---------------------------
# GUI 관련 클래스들
# ---------------------------
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
        self.brightness = 0
        
        layout = QVBoxLayout()
        
        self.label = QLabel("LED Brightness Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        grid_layout = QGridLayout()
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(80, 80)
        up_btn.clicked.connect(self.increase_brightness)
        grid_layout.addWidget(up_btn, 0, 0, alignment=Qt.AlignCenter)
        
        self.brightness_label = QLabel(str(self.brightness))
        self.brightness_label.setAlignment(Qt.AlignCenter)
        self.brightness_label.setFixedSize(80, 80)
        grid_layout.addWidget(self.brightness_label, 1, 0, alignment=Qt.AlignCenter)
        
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
        self.setFixedSize(320, 480)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(MainScreen(self.stacked_widget))
        self.stacked_widget.addWidget(ControlModeScreen(self.stacked_widget))
        self.stacked_widget.addWidget(LEDControlScreen(self.stacked_widget))
        self.stacked_widget.addWidget(MonitorControlScreen(self.stacked_widget))
        self.stacked_widget.addWidget(DeskControlScreen(self.stacked_widget))
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def closeEvent(self, event):
        global exit_flag
        exit_flag = True
        event.accept()

# ---------------------------
# 메인 실행 함수
# ---------------------------
def main():
    # 서버 스레드를 백그라운드 데몬 스레드로 실행
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    # (원한다면 keyboard_listener도 별도 스레드로 실행 가능)
    # key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    # key_thread.start()

    # GUI 애플리케이션 실행 (메인 스레드)
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheet(app, theme='dark_teal.xml')
    window.show()
    ret = app.exec_()

    # GUI 종료 후 exit_flag를 True로 설정해 서버 스레드 종료 유도
    global exit_flag
    exit_flag = True
    server_thread.join(timeout=2)
    sys.exit(ret)

if __name__ == '__main__':
    main()
