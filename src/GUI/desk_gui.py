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
client_conn = None  # 클라이언트 소켓 전역 변수

HOST = '0.0.0.0'
PORT = 2007

# 클라이언트 전송 시 동기화를 위한 lock
client_lock = threading.Lock()

# MariaDB 연결 설정 (적절히 수정)
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '0000'
DB_NAME = 'ergodb'

# Arduino 연결 시도 (예: /dev/ttyACM3, /dev/ttyACM0)
ser0 = None
ser1 = None
try:
    ser0 = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
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
# 공통 함수: DB 삽입, 클라이언트 전송, 명령 전송
# ---------------------------
def insert_into_db(data):
    """
    JSON 데이터를 새 프로토콜에 맞게 MariaDB의 desk_info, log 테이블에 삽입.
    desk_info 테이블:
        light, desk_status, monitor_height, monitor_angle, desk_height
    log 테이블:
        user_id, function_code, mode, desk_info_id, request_id, timestamp
    """
    try:
        # desk_info 테이블에 삽입할 데이터 추출
        light = data.get('brightness', 0)
        desk_status_str = data.get('desk_status', "INACTIVE")
        desk_status = 1 if str(desk_status_str).upper() == "ACTIVE" else 0
        monitor_height = data.get('monitor_height', 0)
        monitor_angle = data.get('monitor_tilt', 0)  # monitor_tilt 값을 monitor_angle으로 사용
        desk_height = data.get('desk_height', 0)
        
        # log 테이블에 삽입할 데이터 추출
        # function_code: 예) "CMD001"에서 숫자만 추출하여 정수형으로 변환
        function_code_str = data.get('function_code', '0')
        function_code = int(''.join(filter(str.isdigit, function_code_str))) if any(c.isdigit() for c in function_code_str) else 0
        
        # mode: 문자열이면 매핑, 숫자면 그대로 사용
        mode_val = data.get('mode', 0)
        if isinstance(mode_val, str):
            if mode_val.upper() == "AUTO":
                mode = 1
            elif mode_val.upper() == "MANUAL":
                mode = 2
            else:
                mode = 0
        else:
            mode = mode_val
        
        user_id = 1  # 기본 사용자 id (실제 상황에 맞게 수정 필요)
        
        request_id_str = data.get('request_id', '0')
        try:
            request_id = int(request_id_str)
        except ValueError:
            request_id = 0
        
        # timestamp 처리: ISO8601 형식 "YYYY-MM-DDTHH:MM:SSZ" → "YYYY-MM-DD HH:MM:SS"
        timestamp_str = data.get('timestamp')
        if timestamp_str:
            timestamp = timestamp_str.replace('T', ' ').replace('Z', '')
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # desk_info 테이블에 데이터 삽입
            sql_desk_info = """
            INSERT INTO desk_info (light, desk_status, monitor_height, monitor_angle, desk_height)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_desk_info, (light, desk_status, monitor_height, monitor_angle, desk_height))
            desk_info_id = cursor.lastrowid
            
            # log 테이블에 데이터 삽입
            sql_log = """
            INSERT INTO log (user_id, function_code, mode, desk_info_id, request_id, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_log, (user_id, function_code, mode, desk_info_id, request_id, timestamp))
            
            connection.commit()
            print("DB에 데이터 삽입 완료:", data)
            
    except Exception as e:
        print("DB 삽입 오류:", e)


def send_to_client(conn, msg):
    """클라이언트 소켓에 안전하게 메시지 전송"""
    try:
        with client_lock:
            conn.sendall(msg.encode('utf-8'))
    except Exception as e:
        print("클라이언트 전송 오류:", e)

def send_command(data):
    """전역 client_conn을 사용해 명령 메시지 전송"""
    global client_conn
    if client_conn:
        try:
            msg = json.dumps(data, separators=(',', ':')) + "\n"
            send_to_client(client_conn, msg)
            print("명령 전송:", msg)
        except Exception as e:
            print("명령 전송 중 오류:", e)
    else:
        print("클라이언트 연결 없음. 명령 전송 실패.")

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
    """
    각 Arduino 보드의 시리얼 데이터를 처리.
    새로운 프로토콜 형태의 JSON이 들어온다고 가정:
    {
      "function_code": "CMD001",
      "mode": "AUTO",
      "desk_status": "ACTIVE",
      "brightness": 200,
      "monitor_height": 40,
      "monitor_tilt": 15,
      "desk_height": 75,
      "request_id": "arduino_board",
      "timestamp": "2025-02-25T12:34:56Z"
    }
    """
    if not ser:
        return
    while not exit_flag:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print(f"Arduino 메시지 ({port_name}, 원본):", line)
                    try:
                        # JSON 파싱 시도
                        json_data = json.loads(line)
                        print(f"Arduino 메시지 ({port_name}, JSON 파싱 성공):", json_data)
                        # DB 저장
                        insert_into_db(json_data)
                    except json.JSONDecodeError:
                        # 파싱 실패 시 임의 구조로 처리
                        json_data = {"arduino_data": line}
                        print(f"Arduino 메시지 ({port_name}, JSON 파싱 실패):", json_data)

                    # 클라이언트에게도 전송
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
    global client_conn
    print("서버 스레드 시작됨", flush=True)
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
                client_conn = conn  # 전역에 저장
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
                        # DB 저장
                        insert_into_db(json_data)
                    except json.JSONDecodeError as e:
                        print("클라이언트 JSON 파싱 에러:", e)
                        json_data = None

                    if json_data is not None:
                        # Arduino로도 전달 (동일 프로토콜 구조라고 가정)
                        message_to_arduino = json.dumps(json_data, separators=(',', ':')) + "\n"
                        if ser0:
                            ser0.write(message_to_arduino.encode('utf-8'))
                            print("Arduino (ACM0)로 전송:", message_to_arduino)
                        if ser1:
                            ser1.write(message_to_arduino.encode('utf-8'))
                            print("Arduino (ACM1)로 전송:", message_to_arduino)

                        # 클라이언트에 응답 (간단히 status: ok)
                        response = {
                            "status": "ok",
                            "received": json_data,
                            "message": "성공"
                        }
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
            self.send_led_command()

    def decrease_brightness(self):
        if self.brightness > 0:
            self.brightness -= 1
            self.brightness_label.setText(str(self.brightness))
            self.send_led_command()

    def send_led_command(self):
        data = {
            "function_code": "CMD001",
            "mode": "AUTO",
            "desk_status": "ACTIVE",
            "brightness": self.brightness,
            "monitor_height": 0,
            "monitor_tilt": 0,
            "desk_height": 0,
            "request_id": "desk_gui",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        send_command(data)

class DeskControlScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.desk_height = 0  # 현재 책상 높이 상태 변수
        layout = QVBoxLayout()
        self.label = QLabel("Desk Control")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        grid_layout = QGridLayout()
        btn_up = QPushButton("▲")
        btn_down = QPushButton("▼")
        btn_up.setFixedSize(120, 120)
        btn_down.setFixedSize(120, 120)
        btn_up.clicked.connect(self.increase_desk_height)
        btn_down.clicked.connect(self.decrease_desk_height)
        grid_layout.addWidget(btn_up, 0, 1)
        grid_layout.addWidget(btn_down, 2, 1)
        layout.addLayout(grid_layout)
        
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 50)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)
    
    def increase_desk_height(self):
        if self.desk_height < 100:
            self.desk_height += 5
            self.send_desk_command()
    
    def decrease_desk_height(self):
        if self.desk_height > 0:
            self.desk_height -= 5
            self.send_desk_command()
    
    def send_desk_command(self):
        data = {
            "function_code": "CMD001",
            "mode": "AUTO",
            "desk_status": "ACTIVE",
            "brightness": 0,
            "monitor_height": 0,
            "monitor_tilt": 0,
            "desk_height": self.desk_height,
            "request_id": "desk_gui",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        send_command(data)
    
class MonitorControlScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.monitor_height = 30
        self.monitor_tilt = 45
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
        btn_front.clicked.connect(self.set_front)
        btn_back.clicked.connect(self.set_back)
        btn_up.clicked.connect(self.increase_monitor_height)
        btn_down.clicked.connect(self.decrease_monitor_height)
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
        
    def increase_monitor_height(self):
        if self.monitor_height < 90:
            self.monitor_height += 5
            self.send_monitor_command()
    
    def decrease_monitor_height(self):
        if self.monitor_height > 0:
            self.monitor_height -= 5
            self.send_monitor_command()
    
    def set_front(self):
        # Front: 모니터 기울기를 감소
        if self.monitor_tilt > 0:
            self.monitor_tilt -= 5
            self.send_monitor_command()
    
    def set_back(self):
        # Back: 모니터 기울기를 증가
        if self.monitor_tilt < 90:
            self.monitor_tilt += 5
            self.send_monitor_command()
    
    def send_monitor_command(self):
        data = {
            "function_code": "CMD001",
            "mode": "AUTO",
            "desk_status": "ACTIVE",
            "brightness": 0,
            "monitor_height": self.monitor_height,
            "monitor_tilt": self.monitor_tilt,
            "desk_height": 0,
            "request_id": "desk_gui",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        send_command(data)
        
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
