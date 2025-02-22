import socket
import json
import threading
import serial
import time
import sys
import select
import termios
import tty

HOST = '0.0.0.0'
PORT = 2001
exit_flag = False

# 클라이언트 전송 시 동기화를 위한 lock
client_lock = threading.Lock()

# Arduino 연결 시도 (ACM0, ACM1)
ser0 = None
ser1 = None
try:
    ser0 = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    time.sleep(2)
    print("Dynamic Board에 연결되었습니다. (서버에서)")
except Exception as e:
    print("Dynamic Board 연결 오류:", e)

try:
    ser1 = serial.Serial('/dev/ttyACM2', 9600, timeout=1)
    time.sleep(2)
    print("Static Board에 연결되었습니다. (서버에서)")
except Exception as e:
    print("Static Board 연결 오류:", e)

def send_to_client(conn, msg):
    """클라이언트 소켓에 안전하게 메시지 전송"""
    try:
        with client_lock:
            conn.sendall(msg.encode('utf-8'))
    except Exception as e:
        print("클라이언트 전송 오류:", e)

def keyboard_listener():
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
    if not ser:
        return
    while not exit_flag:
        try:
            if ser.in_waiting > 0:
                # 오류 발생 시 'replace' 옵션 사용
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print(f"Arduino 메시지 ({port_name}, 원본):", line)
                    try:
                        json_data = json.loads(line)
                        print(f"Arduino 메시지 ({port_name}, JSON 파싱 성공):", json_data)
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
    global exit_flag
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"서버가 {PORT} 포트에서 대기 중입니다.")
        conn, addr = server_socket.accept()
        with conn:
            print("클라이언트 연결됨:", addr)
            conn.settimeout(0.5)
            # 두 Arduino 리스너 스레드 생성 (ACM0, ACM1)
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
                    except json.JSONDecodeError as e:
                        print("클라이언트 JSON 파싱 에러:", e)
                        json_data = None
                    if json_data is not None:
                        message_to_arduino = json.dumps(json_data, separators=(',', ':')) + "\n"
                        # 두 Arduino 보드에 동시에 전송
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

if __name__ == '__main__':
    key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    key_thread.start()
    run_server()
    key_thread.join()
    print("프로그램 종료됨.")
