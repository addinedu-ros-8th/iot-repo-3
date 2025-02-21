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
PORT = 1234
exit_flag = False

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    print("Arduino에 연결되었습니다. (서버에서)")
except Exception as e:
    print("Arduino 연결 오류:", e)
    ser = None

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
                if ch == '\x1b':
                    print("\nESC 키 입력 감지. 종료합니다.")
                    exit_flag = True
                    break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def arduino_listener(client_conn):
    if not ser:
        return
    while not exit_flag:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print("Arduino 메시지:", line)
                    try:
                        client_conn.sendall(line.encode('utf-8'))
                    except Exception as e:
                        print("클라이언트 전송 오류:", e)
                        break
        except Exception as e:
            print("Arduino 리스너 오류:", e)
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
            arduino_thread = threading.Thread(target=arduino_listener, args=(conn,), daemon=True)
            arduino_thread.start()
            while not exit_flag:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print("클라이언트 연결 종료.")
                        break
                    received_message = data.decode('utf-8')
                    print("수신:", received_message)
                    try:
                        json_data = json.loads(received_message)
                    except json.JSONDecodeError as e:
                        print("JSON 파싱 에러:", e)
                        json_data = None
                    if ser and json_data is not None:
                        message_to_arduino = json.dumps(json_data, separators=(',', ':')) + "\n"
                        ser.write(message_to_arduino.encode('utf-8'))
                        print("Arduino로 전송:", message_to_arduino)
                    response = {"status": "ok", "received": json_data, "message": "성공"}
                    conn.sendall(json.dumps(response, separators=(',', ':')).encode('utf-8'))
                except socket.timeout:
                    continue
                except Exception as e:
                    print("오류 발생:", e)
                    break
            print("연결종료.")

if __name__ == '__main__':
    key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    key_thread.start()
    run_server()
    key_thread.join()
    print("프로그램 종료됨.")
